"""
Meal Hour Tracker - Reflex Web App
Track your eating times to maintain an 8-hour eating window for intermittent fasting.
"""

import reflex as rx
import pandas as pd
from datetime import datetime, timedelta
from google.cloud import bigquery
from google import genai
from google.genai import types
from pydantic import BaseModel
from google.cloud import storage
import base64
import uuid

class FoodAnalysis(BaseModel):
    image_description: str
    calorie_intake: int

class MealState(rx.State):
    """State management for the meal tracker app."""
    
    notes: str = ""
    current_time: str = ""
    window_end_time: str = ""
    success_message: str = ""
    error_message: str = ""
    meal_history: list[dict] = []
    is_loading: bool = False
    project_id: str = "gen-lang-client-0288149151"
    
    # New state variables for image handling
    uploaded_files: list[str] = []
    image_uri: str = ""
    image_preview: str = ""
    calorie_estimate: int = 0
    food_description: str = ""
    temp_file_data: bytes = b""
    is_analyzing: bool = False
    
    async def handle_file_select(self, files: list[rx.UploadFile]):
        """Handle file selection and show preview only (no upload/analysis yet)."""
        self.error_message = ""
        
        for file in files:
            try:
                # Read the file content
                upload_data = await file.read()
                
                # Store temporarily
                self.temp_file_data = upload_data
                
                # Generate preview (base64 data URL)
                self.image_preview = f"data:image/png;base64,{base64.b64encode(upload_data).decode()}"
                
            except Exception as e:
                self.error_message = f"Error loading image: {str(e)}"

    async def handle_upload_and_analyze(self):
        """Upload the selected image to GCS and analyze it."""
        if not self.temp_file_data:
            self.error_message = "Please select an image first!"
            return
        
        try:
            self.is_analyzing = True
            self.error_message = ""
            yield  # Force UI update to show loading state
            
            # Upload to Google Cloud Storage
            bucket_name = "personal_assistant_agent"
            filename = f"meal_images/{uuid.uuid4()}.png"
            
            storage_client = storage.Client(project=self.project_id)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(filename)
            
            blob.upload_from_string(self.temp_file_data, content_type="image/png")
            self.image_uri = f"gs://{bucket_name}/{filename}"
            
            # Analyze the image
            await self.analyze_food_image()
            
        except Exception as e:
            self.error_message = f"Error uploading image: {str(e)}"
        finally:
            self.is_analyzing = False

    async def analyze_food_image(self):
        """Analyze the uploaded food image using Gemini API."""
        if not self.image_uri:
            return
        
        try:
            # Note: is_analyzing is already set to True by the caller
            
            # Initialize Gemini client
            client = genai.Client(
                vertexai=True,
                project=self.project_id,
                location="global",
            )
            
            model = "gemini-3-flash-preview"
            
            # Generate content with structured output
            response = client.models.generate_content(
                model=model,
                contents=[
                    "What is shown in this image? What is the estimated calorie intake?",
                    types.Part.from_uri(
                        file_uri=self.image_uri,
                        mime_type="image/png",
                    ),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=FoodAnalysis,
                )
            )
            
            # Parse the result
            result = FoodAnalysis.model_validate_json(response.text)
            self.food_description = result.image_description
            self.calorie_estimate = result.calorie_intake
            
            # Auto-fill the notes field
            self.notes = f"{result.image_description} (Est. {result.calorie_intake} calories)"
            
        except Exception as e:
            self.error_message = f"Error analyzing image: {str(e)}"
            raise  # Re-raise to be caught by caller
    
    def clear_image(self):
        """Clear the uploaded image and analysis."""
        self.image_uri = ""
        self.image_preview = ""
        self.calorie_estimate = 0
        self.food_description = ""
        self.temp_file_data = b""
    
    def record_time_with_notes(self, notes: str, calorie: int = 0) -> pd.DataFrame:
        """
        Records the current time, current time plus 8 hours, notes, and calorie estimate.
        Returns a pandas DataFrame with a single row.
        """
        now = datetime.now()
        plus_8h = now + timedelta(hours=8)
        fmt = "%Y-%m-%d %H:%M:%S"
        data = {
            "current_time": [now.strftime(fmt)],
            "current_time_plus_8h": [plus_8h.strftime(fmt)],
            "notes": [notes],
            "calorie": [calorie]
        }
        return pd.DataFrame(data)
    
    def save_df_to_bq(self, df: pd.DataFrame) -> None:
        """
        Saves the given DataFrame to the BigQuery table.
        """
        table_id = f"{self.project_id}.personal_assistant.meal_hour"
        df.to_gbq(
            destination_table=table_id,
            project_id=self.project_id,
            if_exists="append"
        )
    
    def get_meal_history(self) -> None:
        """
        Fetch recent meal history from BigQuery.
        """
        try:
            client = bigquery.Client(project=self.project_id)
            query = f"""
                SELECT current_time, current_time_plus_8h, notes, calorie 
                FROM `{self.project_id}.personal_assistant.meal_hour`
                ORDER BY current_time DESC
                LIMIT 10
            """
            df = client.query(query).to_dataframe()
            
            # Convert DataFrame to list of dicts for display
            self.meal_history = df.to_dict('records')
        except Exception as e:
            self.error_message = f"Error loading history: {str(e)}"
    
    def submit_meal(self):
        """Handle meal submission."""
        self.error_message = ""
        self.success_message = ""
        
        if not self.notes.strip():
            self.error_message = "Please enter a note about your meal!"
            return
        
        try:
            self.is_loading = True
            yield  # Force UI update to show loading state
            
            # Record the time with calorie estimate
            df = self.record_time_with_notes(self.notes, self.calorie_estimate)
            
            # Update display times
            self.current_time = df['current_time'].iloc[0]
            self.window_end_time = df['current_time_plus_8h'].iloc[0]
            
            # Save to BigQuery
            self.save_df_to_bq(df)
            
            self.success_message = f"Meal recorded! Your 8-hour eating window ends at {self.window_end_time}"
            self.notes = ""  # Clear the input
            
            # Clear image data after successful submission
            self.clear_image()
            
            # Refresh history
            self.get_meal_history()
            
        except Exception as e:
            self.error_message = f"❌ Error: {str(e)}"
        finally:
            self.is_loading = False
    
    def on_mount(self):
        """Load meal history when the page loads."""
        self.get_meal_history()

def loading_overlay() -> rx.Component:
    """Corner loading indicator with spinner."""
    return rx.cond(
        MealState.is_loading | MealState.is_analyzing,
        rx.box(
            rx.hstack(
                rx.spinner(
                    size="2",
                    color="white",
                ),
                rx.text(
                    rx.cond(
                        MealState.is_analyzing,
                        "Analyzing...",
                        "Saving..."
                    ),
                    color="white",
                    weight="medium",
                    size="2",
                ),
                spacing="2",
                align_items="center",
            ),
            style={
                "position": "fixed",
                "bottom": "24px",
                "right": "24px",
                "padding": "12px 20px",
                "background": "linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%)",
                "border_radius": "8px",
                "box_shadow": "0 4px 12px -4px rgba(99, 102, 241, 0.5)",
                "z_index": "9999",
            },
        ),
    )

def index() -> rx.Component:
    """Main page of the meal tracker."""
    return rx.fragment(
        # Loading overlay
        loading_overlay(),
        
        # Main content
        rx.box(
            rx.container(
            rx.vstack(
                # Header with modern gradient text
                rx.vstack(
                    rx.heading(
                        "Meal Hour Tracker",
                        size="9",
                        style={
                            "background": "linear-gradient(90deg, #6366F1 0%, #8B5CF6 50%, #D946EF 100%)",
                            "background_clip": "text",
                            "-webkit-background-clip": "text",
                            "-webkit-text-fill-color": "transparent",
                            "font_weight": "700",
                            "letter_spacing": "-0.02em",
                        },
                    ),
                    rx.text(
                        "Track your eating times to maintain an 8-hour eating window for intermittent fasting",
                        size="3",
                        color="#000000",
                        style={
                            "text_align": "center",
                            "max_width": "600px",
                            "line_height": "1.6",
                        },
                    ),
                    spacing="3",
                    align_items="center",
                    margin_bottom="4em",
                    margin_top="2em",
                ),
                
                # Input form with Reflex-style card
                rx.box(
                    rx.vstack(
                        rx.heading(
                            "Record a Meal",
                            size="6",
                            margin_bottom="1em",
                            style={
                                "color": "#0F172A",
                                "font_weight": "600",
                                "letter_spacing": "-0.01em",
                            },
                        ),
                        
                        rx.text(
                            "What did you eat?",
                            size="2",
                            weight="medium",
                            margin_bottom="0.5em",
                            color="#1F2937",
                        ),
                        
                        rx.text_area(
                            placeholder="",
                            value=MealState.notes,
                            on_change=MealState.set_notes,
                            width="100%",
                            rows="4",
                            style={
                                "border_radius": "8px",
                                "border": "1px solid #E2E8F0",
                                "padding": "12px 16px",
                                "font_size": "14px",
                                "background": "#FFFFFF",
                                "color": "#000000",
                                "transition": "all 0.2s ease",
                                ":focus": {
                                    "border_color": "#8B5CF6",
                                    "outline": "none",
                                    "box_shadow": "0 0 0 3px rgba(139, 92, 246, 0.1)",
                                },
                                ":hover": {
                                    "border_color": "#CBD5E1",
                                },
                                "::placeholder": {
                                    "color": "#6B7280",
                                },
                            },
                        ),
                        
                        # Image Upload Section
                        rx.vstack(
                            rx.text(
                                "Add a photo (optional)",
                                size="2",
                                weight="medium",
                                margin_top="1.5em",
                                margin_bottom="0.5em",
                                color="#000000",
                            ),
                            
                            # Upload area with conditional display
                            rx.cond(
                                MealState.image_preview == "",
                                # Show upload box when no image
                                rx.upload(
                                    rx.vstack(
                                        rx.icon("upload", size=28, color="#374151"),
                                        rx.text(
                                            "Drag and drop an image here or click to select",
                                            size="2",
                                            color="#1F2937",
                                            weight="medium",
                                        ),
                                        rx.text(
                                            "PNG or JPEG",
                                            size="1",
                                            color="#374151",
                                        ),
                                        align="center",
                                        spacing="2",
                                        padding="2.5em",
                                    ),
                                    id="upload1",
                                    accept={
                                        "image/png": [".png"],
                                        "image/jpeg": [".jpg", ".jpeg"],
                                    },
                                    max_files=1,
                                    style={
                                        "border": "2px dashed #CBD5E1",
                                        "border_radius": "8px",
                                        "background": "#F8FAFC",
                                        "transition": "all 0.2s ease",
                                        ":hover": {
                                            "border_color": "#8B5CF6",
                                            "background": "#F5F3FF",
                                        },
                                    },
                                    on_drop=MealState.handle_file_select(rx.upload_files(upload_id="upload1")),
                                ),
                                # Show preview when image is selected
                                rx.vstack(
                                    rx.box(
                                        rx.image(
                                            src=MealState.image_preview,
                                            style={
                                                "width": "100%",
                                                "max_height": "300px",
                                                "object_fit": "contain",
                                                "border_radius": "8px",
                                            },
                                        ),
                                        style={
                                            "border": "1px solid #E2E8F0",
                                            "border_radius": "8px",
                                            "padding": "1em",
                                            "background": "#F8FAFC",
                                        },
                                    ),
                                    rx.button(
                                        rx.hstack(
                                            rx.icon("x", size=14),
                                            rx.text("Remove Photo"),
                                            spacing="1",
                                        ),
                                        on_click=MealState.clear_image,
                                        size="2",
                                        style={
                                            "background": "#FEF2F2",
                                            "color": "#DC2626",
                                            "border": "1px solid #FEE2E2",
                                            "border_radius": "6px",
                                            "margin_top": "0.5em",
                                            "font_weight": "500",
                                            "transition": "all 0.2s ease",
                                            ":hover": {
                                                "background": "#FEE2E2",
                                                "border_color": "#FCA5A5",
                                            },
                                        },
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                            ),
                            
                            # Upload and Analyze button - hidden upload component for re-upload
                            rx.upload(
                                rx.text("", display="none"),
                                id="upload1",
                                accept={
                                    "image/png": [".png"],
                                    "image/jpeg": [".jpg", ".jpeg"],
                                },
                                max_files=1,
                                display="none",
                            ),
                            
                            # Upload & Analyze button with loading state
                            rx.button(
                                rx.cond(
                                    MealState.is_analyzing,
                                    rx.hstack(
                                        rx.spinner(size="2", color="white"),
                                        rx.text("Analyzing...", weight="medium"),
                                        spacing="2",
                                        justify="center",
                                    ),
                                    rx.hstack(
                                        rx.text("Analyze Photo", weight="medium"),
                                        spacing="2",
                                    ),
                                ),
                                on_click=MealState.handle_upload_and_analyze,
                                disabled=rx.cond(
                                    MealState.image_preview == "",
                                    True,
                                    MealState.is_analyzing,
                                ),
                                size="3",
                                width="100%",
                                style={
                                    "margin_top": "1em",
                                    "background": "linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%)",
                                    "color": "white",
                                    "border": "none",
                                    "border_radius": "8px",
                                    "padding": "12px 20px",
                                    "font_weight": "500",
                                    "transition": "all 0.2s ease",
                                    ":hover": {
                                        "transform": "translateY(-1px)",
                                        "box_shadow": "0 8px 16px -4px rgba(99, 102, 241, 0.4)",
                                    },
                                    ":disabled": {
                                        "opacity": "0.5",
                                        "cursor": "not-allowed",
                                        "transform": "none",
                                    },
                                },
                            ),
                            
                            # AI Analysis results
                            rx.cond(
                                MealState.food_description != "",
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("sparkles", size=18, color="#8B5CF6"),
                                            rx.text(
                                                "AI Analysis",
                                                weight="bold",
                                                size="3",
                                                color="#0F172A",
                                            ),
                                            spacing="2",
                                        ),
                                        rx.text(
                                            MealState.food_description,
                                            size="2",
                                            color="#000000",
                                            style={"line_height": "1.6"},
                                        ),
                                        rx.box(
                                            rx.hstack(
                                                rx.icon("flame", size=16, color="#F59E0B"),
                                                rx.text(
                                                    f"{MealState.calorie_estimate} calories",
                                                    weight="bold",
                                                    size="3",
                                                    style={
                                                        "background": "linear-gradient(90deg, #F59E0B 0%, #EF4444 100%)",
                                                        "background_clip": "text",
                                                        "-webkit-background-clip": "text",
                                                        "-webkit-text-fill-color": "transparent",
                                                    },
                                                ),
                                                spacing="2",
                                            ),
                                            style={
                                                "padding": "8px 12px",
                                                "background": "#FEF3C7",
                                                "border_radius": "6px",
                                                "border": "1px solid #FDE68A",
                                            },
                                        ),
                                        spacing="3",
                                    ),
                                    style={
                                        "margin_top": "1em",
                                        "padding": "1.25em",
                                        "background": "linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%)",
                                        "border_radius": "8px",
                                        "border": "1px solid #DDD6FE",
                                    },
                                ),
                            ),
                            
                            width="100%",
                            spacing="2",
                        ),
                        
                        # Record Meal Button
                        rx.button(
                            rx.cond(
                                MealState.is_loading,
                                rx.hstack(
                                    rx.spinner(size="3", color="white"),
                                    rx.text("Saving...", color="white", weight="medium"),
                                    spacing="2",
                                    justify="center",
                                ),
                                rx.hstack(
                                    rx.text("Record Meal Time", weight="medium"),
                                    spacing="2",
                                    justify="center",
                                ),
                            ),
                            on_click=MealState.submit_meal,
                            size="4",
                            width="100%",
                            disabled=MealState.is_loading,
                            style={
                                "margin_top": "1.5em",
                                "background": "linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%)",
                                "color": "white",
                                "border_radius": "8px",
                                "padding": "14px 20px",
                                "font_weight": "500",
                                "border": "none",
                                "cursor": "pointer",
                                "transition": "all 0.2s ease",
                                ":hover": {
                                    "transform": "translateY(-1px)",
                                    "box_shadow": "0 12px 24px -8px rgba(99, 102, 241, 0.5)",
                                },
                                ":disabled": {
                                    "opacity": "0.5",
                                    "cursor": "not-allowed",
                                    "transform": "none",
                                },
                            },
                        ),
                        
                        # Success/Error messages
                        rx.cond(
                            MealState.success_message != "",
                            rx.box(
                                rx.hstack(
                                    rx.icon("check-circle-2", size=18, color="#10B981"),
                                    rx.text(
                                        MealState.success_message,
                                        size="2",
                                        weight="medium",
                                        color="#047857",
                                    ),
                                    spacing="2",
                                    align_items="center",
                                ),
                                style={
                                    "margin_top": "1em",
                                    "padding": "12px 16px",
                                    "background": "#ECFDF5",
                                    "border": "1px solid #A7F3D0",
                                    "border_radius": "8px",
                                },
                            ),
                        ),
                        
                        rx.cond(
                            MealState.error_message != "",
                            rx.box(
                                rx.hstack(
                                    rx.icon("alert-circle", size=18, color="#EF4444"),
                                    rx.text(
                                        MealState.error_message,
                                        size="2",
                                        weight="medium",
                                        color="#B91C1C",
                                    ),
                                    spacing="2",
                                    align_items="center",
                                ),
                                style={
                                    "margin_top": "1em",
                                    "padding": "12px 16px",
                                    "background": "#FEF2F2",
                                    "border": "1px solid #FECACA",
                                    "border_radius": "8px",
                                },
                            ),
                        ),
                        
                        width="100%",
                        spacing="3",
                    ),
                    style={
                        "width": "100%",
                        "padding": "32px",
                        "background": "white",
                        "border_radius": "12px",
                        "border": "1px solid #E2E8F0",
                        "box_shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.05)",
                        "margin_bottom": "24px",
                    },
                ),
                
                # Recent Meals History
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.heading(
                                "Recent Meals",
                                size="6",
                                style={
                                    "color": "#0F172A",
                                    "font_weight": "600",
                                    "letter_spacing": "-0.01em",
                                },
                            ),
                            rx.box(
                                rx.text(
                                    MealState.meal_history.length(),
                                    weight="bold",
                                    size="2",
                                    color="white",
                                ),
                                style={
                                    "background": "linear-gradient(90deg, #6366F1 0%, #8B5CF6 100%)",
                                    "padding": "4px 12px",
                                    "border_radius": "16px",
                                },
                            ),
                            spacing="3",
                            align_items="center",
                            margin_bottom="1.25em",
                        ),
                        
                        rx.cond(
                            MealState.meal_history.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    MealState.meal_history,
                                    lambda meal: rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.box(
                                                    rx.icon("clock", size=24, color="#8B5CF6"),
                                                    style={
                                                        "padding": "12px",
                                                        "background": "linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%)",
                                                        "border_radius": "10px",
                                                        "border": "1px solid #DDD6FE",
                                                    },
                                                ),
                                                rx.vstack(
                                                    rx.text(
                                                        meal["current_time"],
                                                        weight="bold",
                                                        size="3",
                                                        color="#0F172A",
                                                    ),
                                                    rx.hstack(
                                                        rx.icon("timer", size=14, color="#1F2937"),
                                                        rx.text(
                                                            f"Window ends: {meal['current_time_plus_8h']}",
                                                            size="2",
                                                            color="#1F2937",
                                                        ),
                                                        spacing="1",
                                                    ),
                                                    rx.hstack(
                                                        rx.icon("flame", size=14, color="#F59E0B"),
                                                        rx.text(
                                                            f"{meal.get('calorie', 0)} cal",
                                                            size="2",
                                                            color="#F59E0B",
                                                            weight="bold",
                                                        ),
                                                        spacing="1",
                                                    ),
                                                    spacing="1",
                                                    align_items="start",
                                                ),
                                                spacing="3",
                                                width="100%",
                                                align_items="start",
                                            ),
                                            rx.box(
                                                rx.text(
                                                    meal["notes"],
                                                    size="2",
                                                    color="#000000",
                                                    style={"line_height": "1.6"},
                                                ),
                                                style={
                                                    "padding": "12px",
                                                    "background": "#F8FAFC",
                                                    "border_radius": "6px",
                                                    "margin_top": "12px",
                                                    "border": "1px solid #F1F5F9",
                                                },
                                            ),
                                            spacing="2",
                                            width="100%",
                                        ),
                                        style={
                                            "padding": "20px",
                                            "background": "white",
                                            "border": "1px solid #E2E8F0",
                                            "border_radius": "10px",
                                            "margin_bottom": "12px",
                                            "transition": "all 0.2s ease",
                                            ":hover": {
                                                "border_color": "#8B5CF6",
                                                "box_shadow": "0 4px 12px -4px rgba(139, 92, 246, 0.2)",
                                                "transform": "translateY(-1px)",
                                            },
                                        },
                                    ),
                                ),
                                width="100%",
                                spacing="2",
                            ),
                            rx.box(
                                rx.vstack(
                                    rx.icon("utensils", size=48, color="#CBD5E1"),
                                    rx.text(
                                        "No meals recorded yet",
                                        size="3",
                                        weight="bold",
                                        color="#1F2937",
                                    ),
                                    rx.text(
                                        "Start tracking your first meal above!",
                                        size="2",
                                        color="#374151",
                                    ),
                                    spacing="3",
                                    align_items="center",
                                ),
                                style={
                                    "padding": "60px",
                                    "text_align": "center",
                                },
                            ),
                        ),
                        
                        width="100%",
                        spacing="2",
                    ),
                    style={
                        "width": "100%",
                        "padding": "32px",
                        "background": "white",
                        "border_radius": "12px",
                        "border": "1px solid #E2E8F0",
                        "box_shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.05)",
                    },
                ),
                
                width="100%",
                max_width="900px",
                padding="40px 20px",
                spacing="4",
            ),
            on_mount=MealState.on_mount,
        ),
        style={
            "min_height": "100vh",
            "background": "linear-gradient(180deg, #FAFAFA 0%, #F5F5F5 100%)",
            "padding": "0",
        },
        ),
    )

# App configuration with Reflex-style modern design
app = rx.App(
    style={
        "font_family": "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "color": "#000000",
    },
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
    ],
)

app.add_page(
    index,
    route="/",
    title="Meal Hour Tracker | Track Your Intermittent Fasting",
    description="Track your eating times to maintain an 8-hour eating window for intermittent fasting",
)
