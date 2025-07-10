# Langfuse Integration with Google Gemini

This is a basic implementation of Langfuse tracing with Google Vertex AI Gemini integration.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Google Cloud:**
   - Create a Google Cloud Project
   - Enable the Vertex AI API: https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com
   - Set up authentication (choose one):
     - **Option A (Recommended):** Run `gcloud auth application-default login`
     - **Option B:** Create a service account key and set `GOOGLE_APPLICATION_CREDENTIALS`

3. **Configure environment variables:**
   - Copy `.env.example` to `.env`: `cp .env.example .env`
   - Replace `your-google-cloud-project-id` with your actual Google Cloud Project ID
   - Add your Langfuse credentials (get them from your Langfuse dashboard)

4. **Run the application:**
   ```bash
   python main.py
   ```

## What it does

- Uses the `@observe()` decorator to automatically trace function calls
- Integrates with Google Vertex AI Gemini Pro for text generation
- Captures generation metadata, performance metrics, and traces
- Sends trace data to your Langfuse instance

## Features traced

- Function execution times and call structure
- Gemini API calls (including model, input/output, latency)
- Input/output data for debugging and analysis
- Error handling and logging

## View traces

After running the script, you can view the traces in your Langfuse dashboard.
