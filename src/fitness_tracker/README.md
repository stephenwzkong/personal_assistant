# Fitness Tracker

A Reflex web application for tracking workouts with AI-powered analysis of fitness app screenshots.

## Features

- Upload workout screenshots (Strava, Apple Fitness, etc.)
- AI analysis via Gemini to extract exercise type, duration, and calories
- Track workouts in BigQuery
- View daily and weekly statistics
- Workout history with recent activity

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
reflex run

# Or use the start script
./start.sh
```

## Deployment

Deploy to Google Cloud Run:

```bash
mise run build-push-deploy
```

## Environment Variables

Required:
- `GOOGLE_API_KEY` - For Gemini AI analysis
- `GOOGLE_CLOUD_PROJECT` - GCP project ID

Optional:
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account key
