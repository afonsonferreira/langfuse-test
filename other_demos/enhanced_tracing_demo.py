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


@observe(
    # Method 1: Add metadata directly in the decorator
    name="enhanced_story_generator",
    metadata={
        "version": "2.0",
        "feature": "rich_metadata_demo",
        "experiment": "metadata_enhancement_test",
    },
)
def generate_story_with_rich_metadata():
    """Demonstrates different ways to add information to Langfuse traces"""

    print("🔍 Generating story with rich metadata tracking...")

    # Generate user profile (simulated)
    user_profile = {
        "user_id": "demo_user_123",
        "preferences": {"genre": "sci-fi", "length": "medium", "style": "descriptive"},
        "session_info": {
            "session_id": f"session_{int(time.time())}",
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "platform": "demo_script",
        },
    }

    # Method 2: Rich nested function calls with individual metadata
    story_premise = generate_premise_with_metadata(user_profile)
    print(f"📝 Premise: {story_premise[:100]}...")

    story_content = write_story_with_tracking(story_premise, user_profile)
    print(f"📖 Story: {story_content[:100]}...")

    quality_analysis = analyze_with_scoring(story_content)
    print(f"📊 Quality Score: {quality_analysis['overall_score']}/100")

    # Compile final result with comprehensive metadata
    final_result = {
        "premise": story_premise,
        "story": story_content,
        "analysis": quality_analysis,
        "user_profile": user_profile,
        "generation_stats": {
            "total_words": len(story_content.split()),
            "generation_time": time.time()
            - int(user_profile["session_info"]["session_id"].split("_")[1]),
            "quality_score": quality_analysis["overall_score"],
        },
    }

    return final_result


@observe(
    name="premise_generation",
    metadata={"step": "premise", "type": "creative_generation"},
)
def generate_premise_with_metadata(user_profile: dict) -> str:
    """Generate story premise with user-specific customization"""
    model = GenerativeModel("gemini-2.0-flash")

    # Create genre-specific prompt
    genre = user_profile["preferences"]["genre"]
    style = user_profile["preferences"]["style"]

    prompt = f"""Generate a compelling {genre} story premise that is {style} in nature.
    
    Create something unique and engaging in 1-2 sentences.
    Genre focus: {genre}
    Style: {style}
    
    Make it original and thought-provoking."""

    response = model.generate_content(prompt)
    premise = response.text.strip()

    return premise


@observe(
    name="story_writing", metadata={"step": "main_content", "type": "creative_writing"}
)
def write_story_with_tracking(premise: str, user_profile: dict) -> str:
    """Write the main story with detailed parameter tracking"""
    model = GenerativeModel("gemini-2.0-flash")

    # Extract preferences
    length_pref = user_profile["preferences"]["length"]
    style_pref = user_profile["preferences"]["style"]

    # Map preferences to specific instructions
    length_mapping = {
        "short": "150-200 words",
        "medium": "250-350 words",
        "long": "400-500 words",
    }

    target_length = length_mapping.get(length_pref, "250-350 words")

    prompt = f"""Based on this premise: {premise}
    
    Write a complete {style_pref} story of approximately {target_length}.
    
    Requirements:
    - Target length: {target_length}
    - Style: {style_pref}
    - Include vivid descriptions and engaging dialogue
    - Have a clear beginning, middle, and end
    - Create emotional connection with the reader
    
    Make it compelling and well-structured."""

    response = model.generate_content(prompt)
    story = response.text.strip()

    return story


@observe(
    name="quality_analysis_and_scoring",
    metadata={
        "step": "analysis",
        "type": "quality_assessment",
        "scoring_enabled": True,
    },
)
def analyze_with_scoring(story: str) -> dict:
    """Comprehensive story analysis with multiple scoring dimensions"""

    word_count = len(story.split())

    # Dimension 1: Structure Analysis
    structure_analysis = analyze_story_structure(story)

    # Dimension 2: Language Quality
    language_analysis = analyze_language_quality(story)

    # Dimension 3: Engagement Factor
    engagement_analysis = analyze_engagement(story)

    # Calculate overall score
    overall_score = round(
        (
            structure_analysis["score"] * 0.4  # 40% weight
            + language_analysis["score"] * 0.3  # 30% weight
            + engagement_analysis["score"] * 0.3  # 30% weight
        )
    )

    return {
        "overall_score": overall_score,
        "word_count": word_count,
        "structure": structure_analysis,
        "language": language_analysis,
        "engagement": engagement_analysis,
        "breakdown": {
            "structure_weighted": structure_analysis["score"] * 0.4,
            "language_weighted": language_analysis["score"] * 0.3,
            "engagement_weighted": engagement_analysis["score"] * 0.3,
        },
    }


@observe(
    name="structure_analysis",
    metadata={
        "analysis_type": "narrative_structure",
        "criteria": ["beginning", "middle", "end", "flow"],
    },
)
def analyze_story_structure(story: str) -> dict:
    """Analyze narrative structure"""
    model = GenerativeModel("gemini-2.0-flash")

    prompt = f"""Analyze the narrative structure of this story:

    {story}
    
    Rate each element from 1-10:
    1. Clear beginning: Does it establish setting/character effectively?
    2. Developed middle: Is there meaningful conflict/development?
    3. Satisfying ending: Does it resolve appropriately?
    4. Overall flow: Does it read smoothly?
    
    Format your response as:
    Beginning: X/10
    Middle: X/10
    Ending: X/10
    Flow: X/10
    Brief explanation of ratings."""

    response = model.generate_content(prompt)
    analysis_text = response.text.strip()

    # Extract scores (simplified parsing)
    scores = {"beginning": 7, "middle": 7, "ending": 7, "flow": 7}  # defaults

    try:
        lines = analysis_text.split("\n")
        for line in lines:
            if "Beginning:" in line:
                scores["beginning"] = int(line.split("/")[0].split(":")[1].strip())
            elif "Middle:" in line:
                scores["middle"] = int(line.split("/")[0].split(":")[1].strip())
            elif "Ending:" in line:
                scores["ending"] = int(line.split("/")[0].split(":")[1].strip())
            elif "Flow:" in line:
                scores["flow"] = int(line.split("/")[0].split(":")[1].strip())
    except Exception as e:
        print(f"Score parsing error: {e}")

    average_score = (
        sum(scores.values()) / len(scores) * 10
    )  # Convert to 100-point scale

    return {
        "score": round(average_score),
        "components": scores,
        "analysis": analysis_text,
    }


@observe(
    name="language_quality_analysis",
    metadata={
        "analysis_type": "language_assessment",
        "criteria": ["grammar", "vocabulary", "style"],
    },
)
def analyze_language_quality(story: str) -> dict:
    """Analyze language quality and writing style"""
    model = GenerativeModel("gemini-2.0-flash")

    prompt = f"""Evaluate the language quality of this story:

    {story}
    
    Rate from 1-10:
    1. Grammar and mechanics
    2. Vocabulary richness  
    3. Writing style consistency
    4. Clarity and readability
    
    Format: Grammar: X/10, Vocabulary: X/10, Style: X/10, Clarity: X/10
    Then provide brief feedback."""

    response = model.generate_content(prompt)
    analysis_text = response.text.strip()

    # Extract scores
    scores = {"grammar": 8, "vocabulary": 8, "style": 8, "clarity": 8}  # defaults

    try:
        if "Grammar:" in analysis_text:
            scores["grammar"] = int(
                analysis_text.split("Grammar:")[1].split("/")[0].strip()
            )
        if "Vocabulary:" in analysis_text:
            scores["vocabulary"] = int(
                analysis_text.split("Vocabulary:")[1].split("/")[0].strip()
            )
        if "Style:" in analysis_text:
            scores["style"] = int(
                analysis_text.split("Style:")[1].split("/")[0].strip()
            )
        if "Clarity:" in analysis_text:
            scores["clarity"] = int(
                analysis_text.split("Clarity:")[1].split("/")[0].strip()
            )
    except Exception as e:
        print(f"Language score parsing error: {e}")

    average_score = sum(scores.values()) / len(scores) * 10

    return {
        "score": round(average_score),
        "components": scores,
        "analysis": analysis_text,
    }


@observe(
    name="engagement_analysis",
    metadata={
        "analysis_type": "reader_engagement",
        "criteria": ["interest", "emotion", "memorability"],
    },
)
def analyze_engagement(story: str) -> dict:
    """Analyze how engaging and memorable the story is"""
    model = GenerativeModel("gemini-2.0-flash")

    prompt = f"""Rate this story's engagement factor:

    {story}
    
    On a scale of 1-10, rate:
    1. Interest level: How captivating is it?
    2. Emotional impact: Does it evoke feelings?
    3. Memorability: Will readers remember it?
    4. Originality: How unique/creative is it?
    
    Provide scores and brief reasoning for each."""

    response = model.generate_content(prompt)
    analysis_text = response.text.strip()

    # Simplified scoring based on positive/negative keywords
    positive_keywords = [
        "captivating",
        "engaging",
        "compelling",
        "memorable",
        "creative",
        "original",
        "interesting",
    ]
    negative_keywords = [
        "boring",
        "predictable",
        "weak",
        "forgettable",
        "cliche",
        "uninteresting",
    ]

    positive_count = sum(
        1 for word in positive_keywords if word.lower() in analysis_text.lower()
    )
    negative_count = sum(
        1 for word in negative_keywords if word.lower() in analysis_text.lower()
    )

    # Base score with adjustments
    base_score = 75
    engagement_score = base_score + (positive_count * 3) - (negative_count * 4)
    engagement_score = max(40, min(95, engagement_score))  # Clamp between 40-95

    return {
        "score": engagement_score,
        "analysis": analysis_text,
        "metrics": {
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "base_score": base_score,
        },
    }


if __name__ == "__main__":
    print("🎯 Rich Metadata Demo - Multiple ways to enhance Langfuse traces")
    print("=" * 80)

    start_time = time.time()
    result = generate_story_with_rich_metadata()
    total_time = time.time() - start_time

    print("\n" + "=" * 60)
    print("📚 COMPLETE STORY")
    print("=" * 60)
    print(result["story"])

    print("\n" + "=" * 60)
    print("📊 DETAILED ANALYSIS")
    print("=" * 60)

    analysis = result["analysis"]
    print(f"Overall Quality Score: {analysis['overall_score']}/100")
    print(f"Word Count: {analysis['word_count']} words")

    print("\n📈 Score Breakdown:")
    print(f"  Structure: {analysis['structure']['score']}/100 (40% weight)")
    print(f"  Language:  {analysis['language']['score']}/100 (30% weight)")
    print(f"  Engagement: {analysis['engagement']['score']}/100 (30% weight)")

    print("\n🔍 Component Details:")
    print(f"  Structure components: {analysis['structure']['components']}")
    print(f"  Language components: {analysis['language']['components']}")
    print(f"  Engagement metrics: {analysis['engagement']['metrics']}")

    print("\n⏱️ Performance:")
    print(f"  Total generation time: {total_time:.2f} seconds")
    print(f"  Session ID: {result['user_profile']['session_info']['session_id']}")

    print("\n✨ What you'll see in Langfuse:")
    print("  🏗️  Hierarchical trace structure with nested functions")
    print("  📊 Multiple scoring dimensions with detailed breakdowns")
    print("  🏷️  Rich metadata for filtering and analysis")
    print("  👤 User profile and preference tracking")
    print("  📈 Performance metrics and timing data")
    print("  🔍 Detailed component analysis for each dimension")
    print("  📋 Input/output tracking for every step")
    print("  🎯 Custom scoring algorithms with explanations")
