# 🍽️ Meal Hour Tracker

A Reflex web application for tracking your eating times to maintain an 8-hour eating window for intermittent fasting.

## Features

- ✅ **Automatic Timestamp Recording** - Records the exact time when you log a meal
- ⏰ **8-Hour Window Tracking** - Automatically calculates when your eating window ends
- 📝 **Meal Notes** - Add notes about what you ate
- 💾 **BigQuery Storage** - All data is saved to Google BigQuery
- 📊 **Meal History** - View your 10 most recent meals
- 🎨 **Beautiful UI** - Clean, modern interface built with Reflex

## How It Works

1. Enter a note about your meal (e.g., "Breakfast - oatmeal and coffee")
2. Click "Record Meal Time"
3. The app automatically records:
   - Current timestamp
   - End of 8-hour eating window (current time + 8 hours)
   - Your notes
4. Data is saved to BigQuery table: `personal_assistant.meal_hour`

## Setup

### Prerequisites

- Python 3.12+
- Google Cloud credentials configured
- BigQuery table: `gen-lang-client-0288149151.personal_assistant.meal_hour`

### Installation

1. Navigate to the meal_hour directory:
```bash
cd tests/meal_hour
```

2. Install dependencies (from project root):
```bash
uv pip install -e .
```

Or install individually:
```bash
pip install reflex google-cloud-bigquery pandas pandas-gbq
```

### Running the App

From the `tests/meal_hour` directory, run:

```bash
reflex run
```

The app will start on `http://localhost:3000`

## Usage Example

**Scenario**: You're doing 16:8 intermittent fasting

1. You eat your first meal at 12:00 PM
2. Open the app and enter: "Lunch - grilled chicken salad"
3. Click "Record Meal Time"
4. The app shows: "Your 8-hour eating window ends at 8:00 PM"
5. Now you know you should finish all eating by 8:00 PM

## Data Schema

The app saves data to BigQuery with the following schema:

| Column | Type | Description |
|--------|------|-------------|
| `current_time` | STRING | When the meal was recorded (YYYY-MM-DD HH:MM:SS) |
| `current_time_plus_8h` | STRING | End of 8-hour eating window |
| `notes` | STRING | User's notes about the meal |

## Configuration

Edit `rxconfig.py` to change:
- Port number (default: 3000)
- App name

Edit `main.py` to change:
- BigQuery project ID (default: `gen-lang-client-0288149151`)
- Table name
- Number of meals shown in history (default: 10)

## Troubleshooting

**Error: "Module 'reflex' not found"**
- Run: `pip install reflex`

**Error: "Could not authenticate to BigQuery"**
- Ensure Google Cloud credentials are set up:
  ```bash
  export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
  ```

**Error: "Table not found"**
- Create the BigQuery table first or ensure it exists

## Future Enhancements

- [ ] Add timezone support
- [ ] Visualize eating patterns with charts
- [ ] Send notifications when eating window is closing
- [ ] Export data to CSV
- [ ] Calculate fasting duration between meals
- [ ] Mobile-responsive design improvements

