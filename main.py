import os
from langfuse import observe
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Vertex AI
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "europe-west1")

if PROJECT_ID:
    vertexai.init(project=PROJECT_ID, location=LOCATION)


@observe()
def story():
    """Generate a story using Google Gemini Pro"""
    model = GenerativeModel("gemini-2.0-flash")

    prompt = (
        """Explain Langfuse in a simple and consice way, suitable for a beginner."""
    )

    response = model.generate_content(prompt)
    return response.text


@observe()
def story_generation():
    """Main function to orchestrate story generation"""
    return story()


if __name__ == "__main__":
    result = story_generation()
    print("Generated Story:")
    print("=" * 50)
    print(result)
