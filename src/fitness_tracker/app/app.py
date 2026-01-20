"""
Fitness Tracker - Reflex Web App
Track your workouts, analyze fitness app screenshots, and monitor your progress.
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

class WorkoutAnalysis(BaseModel):
    image_description: str
    exercise_type: str  # Running, Cycling, Swimming, Strength Training, Yoga, Walking, HIIT, Sports, Other
    duration_hours: int
    duration_minutes: int
    calories_burned: int

class WorkoutState(rx.State):
    """State management for the fitness tracker app."""

    # Form inputs
    notes: str = ""
    exercise_type: str = ""
    duration_hours: int = 0
    duration_minutes: int = 0
    calories_burned: int = 0

    # Image handling
    image_uri: str = ""
    image_preview: str = ""
    temp_file_data: bytes = b""

    # AI results
    workout_description: str = ""

    # UI state
    success_message: str = ""
    error_message: str = ""
    is_loading: bool = False
    is_analyzing: bool = False

    # History and stats
    workout_history: list[dict] = []
    daily_total_hours: float = 0.0
    daily_total_calories: int = 0
    weekly_total_hours: float = 0.0
    weekly_total_calories: int = 0

    # Config
    project_id: str = "gen-lang-client-0288149151"

    def set_duration_hours(self, value: str):
        """Set duration hours from string input."""
        try:
            self.duration_hours = int(value) if value else 0
        except ValueError:
            self.duration_hours = 0

    def set_duration_minutes(self, value: str):
        """Set duration minutes from string input."""
        try:
            self.duration_minutes = int(value) if value else 0
        except ValueError:
            self.duration_minutes = 0

    def set_calories_burned(self, value: str):
        """Set calories burned from string input."""
        try:
            self.calories_burned = int(value) if value else 0
        except ValueError:
            self.calories_burned = 0

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
            filename = f"workout_images/{uuid.uuid4()}.png"

            storage_client = storage.Client(project=self.project_id)
            bucket = storage_client.bucket(bucket_name)
            blob = bucket.blob(filename)

            blob.upload_from_string(self.temp_file_data, content_type="image/png")
            self.image_uri = f"gs://{bucket_name}/{filename}"

            # Analyze the image
            await self.analyze_workout_image()

        except Exception as e:
            self.error_message = f"Error uploading image: {str(e)}"
        finally:
            self.is_analyzing = False

    async def analyze_workout_image(self):
        """Analyze the uploaded workout image using Gemini API."""
        if not self.image_uri:
            return

        try:
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
                    "Analyze this workout/fitness app screenshot. Extract: exercise type (Running, Cycling, Swimming, Strength Training, Yoga, Walking, HIIT, Sports, or Other), duration in hours and minutes, calories burned, and description.",
                    types.Part.from_uri(
                        file_uri=self.image_uri,
                        mime_type="image/png",
                    ),
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=WorkoutAnalysis,
                )
            )

            # Parse the result
            result = WorkoutAnalysis.model_validate_json(response.text)
            self.workout_description = result.image_description
            self.exercise_type = result.exercise_type
            self.duration_hours = result.duration_hours
            self.duration_minutes = result.duration_minutes
            self.calories_burned = result.calories_burned

            # Auto-fill the notes field
            self.notes = result.image_description

        except Exception as e:
            self.error_message = f"Error analyzing image: {str(e)}"
            raise  # Re-raise to be caught by caller

    def clear_image(self):
        """Clear the uploaded image and analysis."""
        self.image_uri = ""
        self.image_preview = ""
        self.workout_description = ""
        self.temp_file_data = b""

    def submit_workout(self):
        """Handle workout submission."""
        self.error_message = ""
        self.success_message = ""

        if not self.exercise_type:
            self.error_message = "Please select an exercise type!"
            return

        if self.duration_hours == 0 and self.duration_minutes == 0:
            self.error_message = "Please enter a duration!"
            return

        try:
            self.is_loading = True
            yield  # Force UI update to show loading state

            # Calculate total duration in hours
            total_hours = self.duration_hours + (self.duration_minutes / 60.0)

            # Create DataFrame for BigQuery
            now = datetime.now()
            data = {
                "workout_timestamp": [now],
                "exercise_type": [self.exercise_type],
                "duration_hours": [total_hours],
                "duration_minutes": [self.duration_minutes],
                "calories_burned": [self.calories_burned],
                "notes": [self.notes],
                "image_uri": [self.image_uri if self.image_uri else ""],
                "created_at": [now],
            }
            df = pd.DataFrame(data)

            # Save to BigQuery
            table_id = f"{self.project_id}.personal_assistant.fitness_tracker"
            df.to_gbq(
                destination_table=table_id,
                project_id=self.project_id,
                if_exists="append"
            )

            self.success_message = f"Workout recorded! {self.exercise_type} for {self.duration_hours}h {self.duration_minutes}m"

            # Clear form
            self.notes = ""
            self.exercise_type = ""
            self.duration_hours = 0
            self.duration_minutes = 0
            self.calories_burned = 0
            self.clear_image()

            # Refresh history and stats
            self.get_workout_history()
            self.calculate_daily_totals()
            self.calculate_weekly_totals()

        except Exception as e:
            self.error_message = f"Error: {str(e)}"
        finally:
            self.is_loading = False

    def get_workout_history(self) -> None:
        """Fetch recent workout history from BigQuery."""
        try:
            client = bigquery.Client(project=self.project_id)
            query = f"""
                SELECT workout_timestamp, exercise_type, duration_hours, duration_minutes,
                       calories_burned, notes
                FROM `{self.project_id}.personal_assistant.fitness_tracker`
                ORDER BY workout_timestamp DESC
                LIMIT 10
            """
            df = client.query(query).to_dataframe()

            # Convert DataFrame to list of dicts for display
            self.workout_history = df.to_dict('records')
        except Exception as e:
            self.error_message = f"Error loading history: {str(e)}"

    def calculate_daily_totals(self) -> None:
        """Calculate today's total workout duration and calories."""
        try:
            client = bigquery.Client(project=self.project_id)
            query = f"""
                SELECT
                    COALESCE(SUM(duration_hours), 0) as total_hours,
                    COALESCE(SUM(calories_burned), 0) as total_calories
                FROM `{self.project_id}.personal_assistant.fitness_tracker`
                WHERE DATE(workout_timestamp) = CURRENT_DATE()
            """
            df = client.query(query).to_dataframe()

            if not df.empty:
                self.daily_total_hours = float(df['total_hours'].iloc[0])
                self.daily_total_calories = int(df['total_calories'].iloc[0])
        except Exception as e:
            self.error_message = f"Error calculating daily totals: {str(e)}"

    def calculate_weekly_totals(self) -> None:
        """Calculate this week's total workout duration and calories."""
        try:
            client = bigquery.Client(project=self.project_id)
            query = f"""
                SELECT
                    COALESCE(SUM(duration_hours), 0) as total_hours,
                    COALESCE(SUM(calories_burned), 0) as total_calories
                FROM `{self.project_id}.personal_assistant.fitness_tracker`
                WHERE DATE(workout_timestamp) >= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
            """
            df = client.query(query).to_dataframe()

            if not df.empty:
                self.weekly_total_hours = float(df['total_hours'].iloc[0])
                self.weekly_total_calories = int(df['total_calories'].iloc[0])
        except Exception as e:
            self.error_message = f"Error calculating weekly totals: {str(e)}"

    def on_mount(self):
        """Load workout history and calculate stats when the page loads."""
        self.get_workout_history()
        self.calculate_daily_totals()
        self.calculate_weekly_totals()

def loading_overlay() -> rx.Component:
    """Corner loading indicator with spinner."""
    return rx.cond(
        WorkoutState.is_loading | WorkoutState.is_analyzing,
        rx.box(
            rx.hstack(
                rx.spinner(
                    size="2",
                    color="white",
                ),
                rx.text(
                    rx.cond(
                        WorkoutState.is_analyzing,
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
                "background": "linear-gradient(90deg, #10B981 0%, #06B6D4 50%, #3B82F6 100%)",
                "border_radius": "8px",
                "box_shadow": "0 4px 12px -4px rgba(16, 185, 129, 0.5)",
                "z_index": "9999",
            },
        ),
    )

def index() -> rx.Component:
    """Main page of the fitness tracker."""
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
                        "Fitness Tracker",
                        size="9",
                        style={
                            "background": "linear-gradient(90deg, #10B981 0%, #06B6D4 50%, #3B82F6 100%)",
                            "background_clip": "text",
                            "-webkit-background-clip": "text",
                            "-webkit-text-fill-color": "transparent",
                            "font_weight": "700",
                            "letter_spacing": "-0.02em",
                        },
                    ),
                    rx.text(
                        "Track your workouts, analyze fitness app screenshots, and monitor your progress",
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

                # Stats Dashboard Card
                rx.box(
                    rx.vstack(
                        rx.heading(
                            "Your Progress",
                            size="6",
                            margin_bottom="1em",
                            style={
                                "color": "#0F172A",
                                "font_weight": "600",
                                "letter_spacing": "-0.01em",
                            },
                        ),

                        rx.hstack(
                            # Today stats
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("calendar", size=20, color="#10B981"),
                                        rx.text(
                                            "Today",
                                            weight="bold",
                                            size="3",
                                            color="#0F172A",
                                        ),
                                        spacing="2",
                                        align_items="center",
                                    ),
                                    rx.text(
                                        f"{WorkoutState.daily_total_hours:.1f}h",
                                        size="7",
                                        weight="bold",
                                        style={
                                            "background": "linear-gradient(90deg, #10B981 0%, #06B6D4 100%)",
                                            "background_clip": "text",
                                            "-webkit-background-clip": "text",
                                            "-webkit-text-fill-color": "transparent",
                                        },
                                    ),
                                    rx.hstack(
                                        rx.icon("flame", size=16, color="#F59E0B"),
                                        rx.text(
                                            f"{WorkoutState.daily_total_calories} cal",
                                            size="3",
                                            color="#1F2937",
                                            weight="medium",
                                        ),
                                        spacing="1",
                                    ),
                                    spacing="2",
                                    align_items="start",
                                ),
                                style={
                                    "flex": "1",
                                    "padding": "24px",
                                    "background": "linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%)",
                                    "border_radius": "10px",
                                    "border": "1px solid #A7F3D0",
                                },
                            ),

                            # Weekly stats
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.icon("calendar-days", size=20, color="#3B82F6"),
                                        rx.text(
                                            "This Week",
                                            weight="bold",
                                            size="3",
                                            color="#0F172A",
                                        ),
                                        spacing="2",
                                        align_items="center",
                                    ),
                                    rx.text(
                                        f"{WorkoutState.weekly_total_hours:.1f}h",
                                        size="7",
                                        weight="bold",
                                        style={
                                            "background": "linear-gradient(90deg, #06B6D4 0%, #3B82F6 100%)",
                                            "background_clip": "text",
                                            "-webkit-background-clip": "text",
                                            "-webkit-text-fill-color": "transparent",
                                        },
                                    ),
                                    rx.hstack(
                                        rx.icon("flame", size=16, color="#F59E0B"),
                                        rx.text(
                                            f"{WorkoutState.weekly_total_calories} cal",
                                            size="3",
                                            color="#1F2937",
                                            weight="medium",
                                        ),
                                        spacing="1",
                                    ),
                                    spacing="2",
                                    align_items="start",
                                ),
                                style={
                                    "flex": "1",
                                    "padding": "24px",
                                    "background": "linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%)",
                                    "border_radius": "10px",
                                    "border": "1px solid #93C5FD",
                                },
                            ),

                            spacing="4",
                            width="100%",
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

                # Input form with Reflex-style card
                rx.box(
                    rx.vstack(
                        rx.heading(
                            "Record a Workout",
                            size="6",
                            margin_bottom="1em",
                            style={
                                "color": "#0F172A",
                                "font_weight": "600",
                                "letter_spacing": "-0.01em",
                            },
                        ),

                        # Exercise Type dropdown
                        rx.text(
                            "Exercise Type",
                            size="2",
                            weight="medium",
                            margin_bottom="0.5em",
                            color="#1F2937",
                        ),
                        rx.select(
                            ["Running", "Cycling", "Swimming", "Strength Training", "Yoga", "Walking", "HIIT", "Sports", "Other"],
                            placeholder="Select exercise type",
                            value=WorkoutState.exercise_type,
                            on_change=WorkoutState.set_exercise_type,
                            size="3",
                            style={
                                "width": "100%",
                                "border_radius": "8px",
                                "border": "1px solid #E2E8F0",
                                "background": "#FFFFFF",
                            },
                        ),

                        # Duration inputs
                        rx.text(
                            "Duration",
                            size="2",
                            weight="medium",
                            margin_top="1.5em",
                            margin_bottom="0.5em",
                            color="#1F2937",
                        ),
                        rx.hstack(
                            rx.vstack(
                                rx.text("Hours", size="1", color="#6B7280"),
                                rx.input(
                                    value=WorkoutState.duration_hours,
                                    on_change=WorkoutState.set_duration_hours,
                                    type="number",
                                    min="0",
                                    max="24",
                                    placeholder="0",
                                    size="3",
                                    style={
                                        "width": "100%",
                                        "border_radius": "8px",
                                        "border": "1px solid #E2E8F0",
                                    },
                                ),
                                spacing="1",
                                flex="1",
                            ),
                            rx.vstack(
                                rx.text("Minutes", size="1", color="#6B7280"),
                                rx.input(
                                    value=WorkoutState.duration_minutes,
                                    on_change=WorkoutState.set_duration_minutes,
                                    type="number",
                                    min="0",
                                    max="59",
                                    placeholder="0",
                                    size="3",
                                    style={
                                        "width": "100%",
                                        "border_radius": "8px",
                                        "border": "1px solid #E2E8F0",
                                    },
                                ),
                                spacing="1",
                                flex="1",
                            ),
                            spacing="3",
                            width="100%",
                        ),

                        # Calories input
                        rx.text(
                            "Calories Burned",
                            size="2",
                            weight="medium",
                            margin_top="1.5em",
                            margin_bottom="0.5em",
                            color="#1F2937",
                        ),
                        rx.input(
                            value=WorkoutState.calories_burned,
                            on_change=WorkoutState.set_calories_burned,
                            type="number",
                            min="0",
                            max="10000",
                            placeholder="0",
                            size="3",
                            style={
                                "width": "100%",
                                "border_radius": "8px",
                                "border": "1px solid #E2E8F0",
                            },
                        ),

                        # Notes textarea
                        rx.text(
                            "Notes",
                            size="2",
                            weight="medium",
                            margin_top="1.5em",
                            margin_bottom="0.5em",
                            color="#1F2937",
                        ),
                        rx.text_area(
                            placeholder="Optional workout notes...",
                            value=WorkoutState.notes,
                            on_change=WorkoutState.set_notes,
                            width="100%",
                            rows="3",
                            style={
                                "border_radius": "8px",
                                "border": "1px solid #E2E8F0",
                                "padding": "12px 16px",
                                "font_size": "14px",
                                "background": "#FFFFFF",
                                "color": "#000000",
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
                                WorkoutState.image_preview == "",
                                # Show upload box when no image
                                rx.upload(
                                    rx.vstack(
                                        rx.icon("upload", size=28, color="#374151"),
                                        rx.text(
                                            "Drag and drop a workout screenshot or click to select",
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
                                            "border_color": "#10B981",
                                            "background": "#ECFDF5",
                                        },
                                    },
                                    on_drop=WorkoutState.handle_file_select(rx.upload_files(upload_id="upload1")),
                                ),
                                # Show preview when image is selected
                                rx.vstack(
                                    rx.box(
                                        rx.image(
                                            src=WorkoutState.image_preview,
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
                                        on_click=WorkoutState.clear_image,
                                        size="2",
                                        style={
                                            "background": "#FEF2F2",
                                            "color": "#DC2626",
                                            "border": "1px solid #FEE2E2",
                                            "border_radius": "6px",
                                            "margin_top": "0.5em",
                                            "font_weight": "500",
                                        },
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                            ),

                            # Hidden upload component for re-upload
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

                            # Analyze button
                            rx.button(
                                rx.cond(
                                    WorkoutState.is_analyzing,
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
                                on_click=WorkoutState.handle_upload_and_analyze,
                                disabled=rx.cond(
                                    WorkoutState.image_preview == "",
                                    True,
                                    WorkoutState.is_analyzing,
                                ),
                                size="3",
                                width="100%",
                                style={
                                    "margin_top": "1em",
                                    "background": "linear-gradient(90deg, #10B981 0%, #06B6D4 100%)",
                                    "color": "white",
                                    "border": "none",
                                    "border_radius": "8px",
                                    "padding": "12px 20px",
                                    "font_weight": "500",
                                },
                            ),

                            # AI Analysis results
                            rx.cond(
                                WorkoutState.workout_description != "",
                                rx.box(
                                    rx.vstack(
                                        rx.hstack(
                                            rx.icon("sparkles", size=18, color="#10B981"),
                                            rx.text(
                                                "AI Analysis",
                                                weight="bold",
                                                size="3",
                                                color="#0F172A",
                                            ),
                                            spacing="2",
                                        ),
                                        rx.text(
                                            WorkoutState.workout_description,
                                            size="2",
                                            color="#000000",
                                            style={"line_height": "1.6"},
                                        ),
                                        spacing="3",
                                    ),
                                    style={
                                        "margin_top": "1em",
                                        "padding": "1.25em",
                                        "background": "linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%)",
                                        "border_radius": "8px",
                                        "border": "1px solid #A7F3D0",
                                    },
                                ),
                            ),

                            width="100%",
                            spacing="2",
                        ),

                        # Record Workout Button
                        rx.button(
                            rx.cond(
                                WorkoutState.is_loading,
                                rx.hstack(
                                    rx.spinner(size="3", color="white"),
                                    rx.text("Saving...", color="white", weight="medium"),
                                    spacing="2",
                                    justify="center",
                                ),
                                rx.hstack(
                                    rx.text("Record Workout", weight="medium"),
                                    spacing="2",
                                    justify="center",
                                ),
                            ),
                            on_click=WorkoutState.submit_workout,
                            size="4",
                            width="100%",
                            disabled=WorkoutState.is_loading,
                            style={
                                "margin_top": "1.5em",
                                "background": "linear-gradient(90deg, #10B981 0%, #06B6D4 50%, #3B82F6 100%)",
                                "color": "white",
                                "border_radius": "8px",
                                "padding": "14px 20px",
                                "font_weight": "500",
                                "border": "none",
                                "cursor": "pointer",
                            },
                        ),

                        # Success/Error messages
                        rx.cond(
                            WorkoutState.success_message != "",
                            rx.box(
                                rx.hstack(
                                    rx.icon("check-circle-2", size=18, color="#10B981"),
                                    rx.text(
                                        WorkoutState.success_message,
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
                            WorkoutState.error_message != "",
                            rx.box(
                                rx.hstack(
                                    rx.icon("alert-circle", size=18, color="#EF4444"),
                                    rx.text(
                                        WorkoutState.error_message,
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

                # Workout History
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.heading(
                                "Recent Workouts",
                                size="6",
                                style={
                                    "color": "#0F172A",
                                    "font_weight": "600",
                                    "letter_spacing": "-0.01em",
                                },
                            ),
                            rx.box(
                                rx.text(
                                    WorkoutState.workout_history.length(),
                                    weight="bold",
                                    size="2",
                                    color="white",
                                ),
                                style={
                                    "background": "linear-gradient(90deg, #10B981 0%, #06B6D4 100%)",
                                    "padding": "4px 12px",
                                    "border_radius": "16px",
                                },
                            ),
                            spacing="3",
                            align_items="center",
                            margin_bottom="1.25em",
                        ),

                        rx.cond(
                            WorkoutState.workout_history.length() > 0,
                            rx.vstack(
                                rx.foreach(
                                    WorkoutState.workout_history,
                                    lambda workout: rx.box(
                                        rx.vstack(
                                            rx.hstack(
                                                rx.box(
                                                    rx.icon("activity", size=24, color="#10B981"),
                                                    style={
                                                        "padding": "12px",
                                                        "background": "linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%)",
                                                        "border_radius": "10px",
                                                        "border": "1px solid #A7F3D0",
                                                    },
                                                ),
                                                rx.vstack(
                                                    rx.text(
                                                        workout["exercise_type"],
                                                        weight="bold",
                                                        size="3",
                                                        color="#0F172A",
                                                    ),
                                                    rx.text(
                                                        workout["workout_timestamp"],
                                                        size="2",
                                                        color="#6B7280",
                                                    ),
                                                    rx.hstack(
                                                        rx.icon("clock", size=14, color="#1F2937"),
                                                        rx.text(
                                                            f"{workout['duration_hours']:.1f}h",
                                                            size="2",
                                                            color="#1F2937",
                                                            weight="bold",
                                                        ),
                                                        rx.icon("flame", size=14, color="#F59E0B"),
                                                        rx.text(
                                                            f"{workout['calories_burned']} cal",
                                                            size="2",
                                                            color="#F59E0B",
                                                            weight="bold",
                                                        ),
                                                        spacing="2",
                                                    ),
                                                    spacing="1",
                                                    align_items="start",
                                                ),
                                                spacing="3",
                                                width="100%",
                                                align_items="start",
                                            ),
                                            rx.cond(
                                                workout["notes"] != "",
                                                rx.box(
                                                    rx.text(
                                                        workout["notes"],
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
                                        },
                                    ),
                                ),
                                width="100%",
                                spacing="2",
                            ),
                            rx.box(
                                rx.vstack(
                                    rx.icon("dumbbell", size=48, color="#CBD5E1"),
                                    rx.text(
                                        "No workouts recorded yet",
                                        size="3",
                                        weight="bold",
                                        color="#1F2937",
                                    ),
                                    rx.text(
                                        "Start tracking your first workout above!",
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
            on_mount=WorkoutState.on_mount,
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
    title="Fitness Tracker | Track Your Workouts",
    description="Track your workouts, analyze fitness app screenshots, and monitor your progress",
)
