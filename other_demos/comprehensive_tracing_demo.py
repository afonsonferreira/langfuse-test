import os
from langfuse import observe, get_client
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


@observe()
def generate_story_with_rich_information():
    """Demonstrates how to add rich information to Langfuse traces in v3"""

    # Get the Langfuse client
    langfuse = get_client()

    print("🔍 Generating story with comprehensive trace information...")

    # Method 1: Update the current trace with rich metadata
    langfuse.update_current_trace(
        name="Rich Story Generation Demo",
        user_id="demo_user_123",
        session_id=f"session_{int(time.time())}",
        tags=["creative_writing", "demo", "metadata_showcase", "gemini"],
        metadata={
            "experiment": {
                "name": "rich_metadata_demo",
                "version": "1.0",
                "hypothesis": "Rich metadata improves trace analysis",
            },
            "user_preferences": {
                "genre": "science_fiction",
                "style": "descriptive",
                "length": "medium",
            },
            "system_info": {
                "model": "gemini-2.0-flash",
                "location": LOCATION,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
        },
        input={
            "task": "Generate a creative story with analysis",
            "requirements": ["creative", "well-structured", "engaging"],
        },
    )

    # Method 2: Update the current span with detailed information
    langfuse.update_current_span(
        metadata={
            "function_purpose": "Main story generation orchestrator",
            "expected_steps": ["premise", "story", "analysis"],
            "performance_target": "< 30 seconds",
        }
    )

    # Generate story components with rich sub-traces
    premise = generate_premise_with_tracking()
    print(f"📝 Premise: {premise[:80]}...")

    story = write_story_with_details(premise)
    print(f"📖 Story: {story[:80]}...")

    analysis = analyze_story_comprehensively(story)
    print(f"📊 Analysis Score: {analysis['overall_score']}/100")

    # Method 3: Update trace output with comprehensive results
    final_result = {
        "premise": premise,
        "story": story,
        "analysis": analysis,
        "metadata": {
            "total_words": len(story.split()),
            "generation_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "quality_metrics": {
                "creativity": analysis.get("creativity_score", 75),
                "structure": analysis.get("structure_score", 80),
                "engagement": analysis.get("engagement_score", 85),
            },
        },
    }

    langfuse.update_current_trace(output=final_result)

    return final_result


@observe()
def generate_premise_with_tracking():
    """Generate story premise with detailed tracking"""
    langfuse = get_client()

    # Add rich metadata to this specific function
    langfuse.update_current_span(
        metadata={
            "step": "premise_generation",
            "purpose": "Create compelling story foundation",
            "target_length": "1-2 sentences",
            "creativity_focus": "high",
        }
    )

    model = GenerativeModel("gemini-2.0-flash")

    prompt = """Generate a unique and compelling science fiction story premise in 1-2 sentences.
    Include an interesting character, setting, and conflict that would make readers want to continue reading."""

    # Log the exact input
    langfuse.update_current_span(
        input={
            "prompt": prompt,
            "model": "gemini-2.0-flash",
            "generation_type": "creative_premise",
        }
    )

    response = model.generate_content(prompt)
    premise = response.text.strip()

    # Analyze the premise quality
    word_count = len(premise.split())
    has_character = any(
        word in premise.lower()
        for word in [
            "scientist",
            "engineer",
            "pilot",
            "commander",
            "doctor",
            "researcher",
        ]
    )
    has_setting = any(
        word in premise.lower()
        for word in ["space", "planet", "station", "galaxy", "future", "colony"]
    )
    has_conflict = any(
        word in premise.lower()
        for word in ["discover", "must", "face", "fight", "survive", "escape"]
    )

    quality_score = (
        50
        + (word_count * 2)
        + (has_character * 15)
        + (has_setting * 15)
        + (has_conflict * 20)
    )
    quality_score = min(100, quality_score)

    # Log detailed output and analysis
    langfuse.update_current_span(
        output={
            "premise": premise,
            "quality_analysis": {
                "word_count": word_count,
                "has_character": has_character,
                "has_setting": has_setting,
                "has_conflict": has_conflict,
                "quality_score": quality_score,
            },
        },
        metadata={
            "analysis_complete": True,
            "quality_indicators": {
                "character_present": has_character,
                "setting_present": has_setting,
                "conflict_present": has_conflict,
            },
        },
    )

    return premise


@observe()
def write_story_with_details(premise: str):
    """Write the main story with comprehensive tracking"""
    langfuse = get_client()

    start_time = time.time()

    # Rich metadata for story writing
    langfuse.update_current_span(
        metadata={
            "step": "story_writing",
            "premise_length": len(premise.split()),
            "target_length": "300-400 words",
            "style_requirements": ["vivid_descriptions", "dialogue", "clear_structure"],
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        input={
            "premise": premise,
            "writing_instructions": "Expand into full story with beginning, middle, end",
        },
    )

    model = GenerativeModel("gemini-2.0-flash")

    prompt = f"""Based on this premise: {premise}
    
    Write a complete science fiction story of 300-400 words that includes:
    - Vivid descriptions of the setting
    - Engaging dialogue between characters  
    - A clear beginning, middle, and end
    - Emotional depth and character development
    
    Make it compelling and well-paced."""

    response = model.generate_content(prompt)
    story = response.text.strip()

    generation_time = time.time() - start_time
    word_count = len(story.split())

    # Detailed analysis of the generated story
    has_dialogue = '"' in story or "'" in story
    paragraph_count = len([p for p in story.split("\n\n") if p.strip()])
    avg_sentence_length = len(story.split()) / max(
        1, story.count(".") + story.count("!") + story.count("?")
    )

    # Performance scoring
    length_score = (
        100 if 300 <= word_count <= 400 else max(50, 100 - abs(350 - word_count))
    )
    speed_score = max(0, 100 - (generation_time * 10))  # Penalize slow generation

    langfuse.update_current_span(
        output={
            "story": story,
            "performance_metrics": {
                "word_count": word_count,
                "generation_time_seconds": round(generation_time, 2),
                "paragraph_count": paragraph_count,
                "has_dialogue": has_dialogue,
                "avg_sentence_length": round(avg_sentence_length, 1),
                "length_score": length_score,
                "speed_score": speed_score,
            },
        },
        metadata={
            "generation_completed": True,
            "quality_indicators": {
                "meets_length_target": 300 <= word_count <= 400,
                "includes_dialogue": has_dialogue,
                "well_structured": paragraph_count >= 3,
            },
            "performance": {
                "fast_generation": generation_time < 10,
                "within_target_length": 300 <= word_count <= 400,
            },
        },
    )

    return story


@observe()
def analyze_story_comprehensively(story: str):
    """Perform comprehensive story analysis with multiple dimensions"""
    langfuse = get_client()

    word_count = len(story.split())

    # Set up comprehensive analysis metadata
    langfuse.update_current_span(
        metadata={
            "step": "comprehensive_analysis",
            "analysis_dimensions": [
                "creativity",
                "structure",
                "engagement",
                "technical",
            ],
            "story_word_count": word_count,
            "analysis_method": "multi_dimensional_scoring",
        },
        input={
            "story": story,
            "analysis_request": "Comprehensive quality assessment across multiple dimensions",
        },
    )

    # Perform multiple types of analysis
    creativity_analysis = analyze_creativity(story)
    structure_analysis = analyze_structure(story)
    engagement_analysis = analyze_engagement(story)

    # Calculate overall score with weighted dimensions
    overall_score = round(
        creativity_analysis["score"] * 0.3  # 30% creativity
        + structure_analysis["score"] * 0.4  # 40% structure
        + engagement_analysis["score"] * 0.3  # 30% engagement
    )

    comprehensive_result = {
        "overall_score": overall_score,
        "creativity_score": creativity_analysis["score"],
        "structure_score": structure_analysis["score"],
        "engagement_score": engagement_analysis["score"],
        "detailed_analysis": {
            "creativity": creativity_analysis,
            "structure": structure_analysis,
            "engagement": engagement_analysis,
        },
        "summary": f"Story scored {overall_score}/100 overall with creativity: {creativity_analysis['score']}, structure: {structure_analysis['score']}, engagement: {engagement_analysis['score']}",
    }

    langfuse.update_current_span(
        output=comprehensive_result,
        metadata={
            "analysis_complete": True,
            "scoring_algorithm": "weighted_multi_dimensional",
            "score_weights": {"creativity": 0.3, "structure": 0.4, "engagement": 0.3},
            "performance_level": (
                "excellent"
                if overall_score >= 85
                else "good"
                if overall_score >= 70
                else "fair"
                if overall_score >= 55
                else "needs_improvement"
            ),
        },
    )

    return comprehensive_result


@observe()
def analyze_creativity(story: str):
    """Analyze creative elements in the story"""
    langfuse = get_client()

    langfuse.update_current_span(
        metadata={
            "analysis_type": "creativity_assessment",
            "criteria": ["originality", "imagination", "unique_elements"],
        }
    )

    # Simple creativity indicators
    sci_fi_elements = len(
        [
            word
            for word in [
                "quantum",
                "neural",
                "hologram",
                "plasma",
                "cybernetic",
                "android",
                "telepathic",
                "wormhole",
            ]
            if word.lower() in story.lower()
        ]
    )
    unique_concepts = len(
        [
            phrase
            for phrase in [
                "never seen",
                "first time",
                "discovered",
                "breakthrough",
                "revolutionary",
            ]
            if phrase.lower() in story.lower()
        ]
    )

    creativity_score = min(100, 60 + (sci_fi_elements * 8) + (unique_concepts * 10))

    result = {
        "score": creativity_score,
        "sci_fi_elements_count": sci_fi_elements,
        "unique_concepts_count": unique_concepts,
        "assessment": "High creativity"
        if creativity_score > 80
        else "Moderate creativity"
        if creativity_score > 60
        else "Standard creativity",
    }

    langfuse.update_current_span(output=result)
    return result


@observe()
def analyze_structure(story: str):
    """Analyze narrative structure"""
    langfuse = get_client()

    langfuse.update_current_span(
        metadata={
            "analysis_type": "narrative_structure",
            "criteria": ["beginning", "middle", "end", "flow", "pacing"],
        }
    )

    paragraphs = [p.strip() for p in story.split("\n\n") if p.strip()]
    sentences = story.count(".") + story.count("!") + story.count("?")

    # Structure indicators
    has_clear_beginning = len(paragraphs) > 0 and len(paragraphs[0]) > 50
    has_development = len(paragraphs) >= 3
    has_resolution = any(
        word in story.lower()
        for word in ["finally", "realized", "understood", "decided", "concluded"]
    )

    structure_score = 50
    if has_clear_beginning:
        structure_score += 15
    if has_development:
        structure_score += 20
    if has_resolution:
        structure_score += 15
    structure_score = min(100, structure_score)

    result = {
        "score": structure_score,
        "paragraph_count": len(paragraphs),
        "sentence_count": sentences,
        "has_clear_beginning": has_clear_beginning,
        "has_development": has_development,
        "has_resolution": has_resolution,
    }

    langfuse.update_current_span(output=result)
    return result


@observe()
def analyze_engagement(story: str):
    """Analyze reader engagement factors"""
    langfuse = get_client()

    langfuse.update_current_span(
        metadata={
            "analysis_type": "engagement_assessment",
            "criteria": [
                "emotional_impact",
                "dialogue",
                "descriptive_language",
                "tension",
            ],
        }
    )

    # Engagement indicators
    has_dialogue = '"' in story or "'" in story
    emotional_words = len(
        [
            word
            for word in [
                "fear",
                "hope",
                "excitement",
                "wonder",
                "relief",
                "tension",
                "surprise",
            ]
            if word.lower() in story.lower()
        ]
    )
    descriptive_adjectives = len(
        [
            word
            for word in [
                "shimmering",
                "vast",
                "mysterious",
                "gleaming",
                "towering",
                "ethereal",
            ]
            if word.lower() in story.lower()
        ]
    )

    engagement_score = 50
    if has_dialogue:
        engagement_score += 20
    engagement_score += min(20, emotional_words * 5)
    engagement_score += min(10, descriptive_adjectives * 3)
    engagement_score = min(100, engagement_score)

    result = {
        "score": engagement_score,
        "has_dialogue": has_dialogue,
        "emotional_words_count": emotional_words,
        "descriptive_elements": descriptive_adjectives,
        "engagement_level": "High"
        if engagement_score > 80
        else "Medium"
        if engagement_score > 60
        else "Low",
    }

    langfuse.update_current_span(output=result)
    return result


if __name__ == "__main__":
    print("🚀 Rich Information Demo - Comprehensive Langfuse Tracing")
    print("=" * 80)

    start_time = time.time()
    result = generate_story_with_rich_information()
    total_time = time.time() - start_time

    print("\n" + "=" * 60)
    print("📚 GENERATED STORY")
    print("=" * 60)
    print(result["story"])

    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE ANALYSIS")
    print("=" * 60)
    analysis = result["analysis"]
    print(f"Overall Score: {analysis['overall_score']}/100")
    print(f"• Creativity: {analysis['creativity_score']}/100")
    print(f"• Structure: {analysis['structure_score']}/100")
    print(f"• Engagement: {analysis['engagement_score']}/100")

    print(f"\nWord Count: {result['metadata']['total_words']} words")
    print(f"Total Generation Time: {total_time:.2f} seconds")

    print("\n" + "=" * 60)
    print("✨ WHAT YOU'LL SEE IN LANGFUSE")
    print("=" * 60)
    print("🎯 Trace-level information:")
    print("  • User ID and session tracking")
    print("  • Rich metadata with experiment details")
    print("  • Comprehensive input/output logging")
    print("  • Multiple tags for filtering")

    print("\n📊 Span-level information:")
    print("  • Function-specific metadata and purposes")
    print("  • Detailed input/output for each step")
    print("  • Performance metrics and timing")
    print("  • Quality indicators and analysis")

    print("\n🔍 Analysis features:")
    print("  • Multi-dimensional scoring system")
    print("  • Detailed quality assessments")
    print("  • Performance benchmarking")
    print("  • Comprehensive metadata for debugging")

    print("\n📈 Advanced features demonstrated:")
    print("  • Nested trace hierarchy")
    print("  • Custom scoring algorithms")
    print("  • Rich metadata at multiple levels")
    print("  • Comprehensive performance tracking")
    print("  • Detailed analysis breakdowns")
