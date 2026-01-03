# Personal Assistant

A personal assistant application.

## Setup

1. Create and activate the virtual environment:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   uv pip install -e .
   ```

3. Set up environment variables:
   Create a `.env` file in the project root with:
   ```
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CLOUD_PROJECT=your_project_id
   ```

## Google Cloud Authentication

For BigQuery and other Google Cloud services, you need to authenticate:

1. **Install Google Cloud SDK** (if not already installed):
   ```bash
   # On macOS with Homebrew
   brew install google-cloud-sdk
   
   # Or using curl
   curl https://sdk.cloud.google.com | bash
   ```

2. **Authenticate with Application Default Credentials**:
   ```bash
   gcloud auth application-default login
   ```
   This will open a browser window for authentication. The credentials will be stored locally and used automatically by the BigQuery client.

3. **Set your project** (optional):
   ```bash
   gcloud config set project YOUR_PROJECT_ID
   ```

### Alternative: Service Account Authentication

If using a service account JSON key:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
```

Or add to your `.env` file:
```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

## Development

Add new dependencies:
```bash
uv pip install <package-name>
```

## License

[Add your license here]

