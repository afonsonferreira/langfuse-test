import os
from langfuse import observe
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Initialize Vertex AI
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

if PROJECT_ID:
    vertexai.init(project=PROJECT_ID, location=LOCATION)


@observe(name="character_generator")
def generate_character(character_type: str) -> dict:
    """Generate a character for the story with specific attributes"""
    model = GenerativeModel("gemini-2.0-flash")

    prompt = f"""Generate a detailed {character_type} character for an epic story.
    Return as JSON with the following structure:
    {{
        "name": "character name",
        "species": "species/race",
        "background": "brief background story",
        "special_abilities": ["ability1", "ability2"],
        "personality_traits": ["trait1", "trait2", "trait3"]
    }}
    
    Make it creative and unique!"""

    response = model.generate_content(prompt)

    try:
        import json

        # Parse the JSON response
        character_data = json.loads(
            response.text.strip().replace("```json", "").replace("```", "")
        )
        return character_data
    except json.JSONDecodeError:
        # If JSON parsing fails, return the raw text
        return {"raw_response": response.text}


@observe(name="story_section_generator")
def generate_story_section(
    characters: list, section_type: str, previous_context: str = ""
) -> str:
    """Generate a specific section of the story"""
    model = GenerativeModel("gemini-2.0-flash")

    character_descriptions = "\n".join(
        [
            f"- {char.get('name', 'Unknown')}: {char.get('species', 'Unknown species')}, {char.get('background', 'No background')}"
            for char in characters
        ]
    )

    prompt = f"""You are writing a {section_type} for an epic story.
    
    Characters available:
    {character_descriptions}
    
    Previous context: {previous_context}
    
    Write an engaging {section_type} (200-300 words) that:
    1. Uses at least one of the characters
    2. Advances the plot
    3. Has vivid descriptions
    4. Ends with a hook for the next section
    
    Make it exciting and cinematic!"""

    response = model.generate_content(prompt)
    return response.text


@observe(name="story_analyzer")
def analyze_story_themes(full_story: str) -> dict:
    """Analyze the themes and elements in the generated story"""
    model = GenerativeModel("gemini-2.0-flash")

    prompt = f"""Analyze this epic story and identify:
    
    Story: {full_story}
    
    Return as JSON:
    {{
        "main_themes": ["theme1", "theme2"],
        "epic_elements": ["element1", "element2"],
        "emotional_tone": "tone description",
        "complexity_score": 1-10,
        "recommendations": ["suggestion1", "suggestion2"]
    }}"""

    response = model.generate_content(prompt)

    try:
        import json

        analysis = json.loads(
            response.text.strip().replace("```json", "").replace("```", "")
        )
        return analysis
    except json.JSONDecodeError:
        return {"error": "Failed to parse analysis", "raw": response.text}


@observe(name="epic_story_generator")
def create_epic_story() -> dict:
    """Create a multi-part epic story with characters and analysis"""

    print("🚀 Creating an epic story...")

    # Step 1: Generate characters
    print("👥 Generating characters...")
    hero = generate_character("hero")
    villain = generate_character("villain")
    mentor = generate_character("wise mentor")

    characters = [hero, villain, mentor]

    # Step 2: Generate story sections
    print("📖 Writing story sections...")

    opening = generate_story_section(characters, "opening scene", "")

    conflict = generate_story_section(
        characters, "conflict scene", f"Opening: {opening[:100]}..."
    )

    climax = generate_story_section(
        characters,
        "climactic battle",
        "Previous scenes established conflict. Current tension is high.",
    )

    resolution = generate_story_section(
        characters, "resolution", "After an epic battle, the story needs closure."
    )

    # Step 3: Combine and analyze
    full_story = f"{opening}\n\n{conflict}\n\n{climax}\n\n{resolution}"

    print("🔍 Analyzing story...")
    analysis = analyze_story_themes(full_story)

    result = {
        "characters": characters,
        "story_sections": {
            "opening": opening,
            "conflict": conflict,
            "climax": climax,
            "resolution": resolution,
        },
        "full_story": full_story,
        "analysis": analysis,
        "metadata": {
            "total_words": len(full_story.split()),
            "num_characters": len(characters),
            "generation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
    }

    return result


if __name__ == "__main__":
    result = create_epic_story()

    print("\n" + "=" * 80)
    print("🎭 CHARACTERS")
    print("=" * 80)
    for i, char in enumerate(result["characters"], 1):
        print(f"\n{i}. {char.get('name', 'Unknown')}")
        print(f"   Species: {char.get('species', 'Unknown')}")
        print(f"   Background: {char.get('background', 'No background')}")
        if char.get("special_abilities"):
            print(f"   Abilities: {', '.join(char['special_abilities'])}")

    print("\n" + "=" * 80)
    print("📚 FULL STORY")
    print("=" * 80)
    print(result["full_story"])

    print("\n" + "=" * 80)
    print("🔍 STORY ANALYSIS")
    print("=" * 80)
    analysis = result["analysis"]
    if "main_themes" in analysis:
        print(f"Themes: {', '.join(analysis['main_themes'])}")
        print(f"Epic Elements: {', '.join(analysis['epic_elements'])}")
        print(f"Emotional Tone: {analysis['emotional_tone']}")
        print(f"Complexity Score: {analysis['complexity_score']}/10")

    print(f"\n📊 Total words generated: {result['metadata']['total_words']}")
    print("✅ Check your Langfuse dashboard for detailed traces!")
