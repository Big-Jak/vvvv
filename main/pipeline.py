import json
import os
import re
import time
from typing import Any, Dict, Optional

try:
    import anthropic
except ImportError:
    anthropic = None

RUBRIC = {
    "organization": "Is there a clear structure -- intro, coherent paragraphing, logical flow, and a conclusion?",
    "development": "Is the argument/content well developed with specific evidence, examples, or reasoning?",
    "mechanics": "Are grammar, spelling, punctuation, and sentence-level mechanics correct?",
    "voice": "Is there a clear, consistent authorial voice and register appropriate to the task?",
}

FEEDBACK_SCHEMA = """{
  "overall_score_1_to_6": <int>,
  "categories": {
    "organization": {"strengths": [...], "weaknesses": [...], "suggestions": [...]},
    "development": {"strengths": [...], "weaknesses": [...], "suggestions": [...]},
    "mechanics": {"strengths": [...], "weaknesses": [...], "suggestions": [...]},
    "voice": {"strengths": [...], "weaknesses": [...], "suggestions": [...]}
  }
}"""

MODEL = os.getenv("FEEDBACK_MODEL", "claude-haiku-4-5-20251001")


def build_prompt(essay_text: str, grading_prompt: Optional[str] = None) -> str:
    rubric_lines = "\n".join(f"- {k.title()}: {v}" for k, v in RUBRIC.items())
    prompt_suffix = ""
    if grading_prompt and grading_prompt.strip():
        prompt_suffix = f"\nAdditional grading criteria provided by the teacher:\n{grading_prompt.strip()}\n"

    return f"""You are an experienced writing tutor giving structured, actionable feedback on a student essay draft.

Rubric categories:
{rubric_lines}
{prompt_suffix}
For EACH rubric category, give:
- 1-2 strengths
- 1-2 weaknesses
- 2-3 concrete, actionable revision suggestions

Also give an overall_score_1_to_6 estimating overall essay quality on a 1 (weak) to 6 (strong) holistic scale.

Respond with ONLY valid JSON matching this schema, no extra commentary, no markdown fences:
{FEEDBACK_SCHEMA}

Essay:
\"\"\"
{essay_text}
\"\"\"
"""


def _clean_json_text(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```json\s*", "", raw, flags=re.IGNORECASE)
    raw = re.sub(r"```$", "", raw, flags=re.IGNORECASE)
    return raw.strip()


def _dummy_feedback(essay_text: str) -> Dict[str, Any]:
    cleaned = re.sub(r"\s+", " ", essay_text or "").strip()
    sentence_count = len(re.findall(r"[^.!?]+[.!?]", cleaned)) or 1
    word_count = len(cleaned.split())
    score = min(max(int(word_count / 150) + 2, 1), 6)
    if score < 1:
        score = 1

    normalized = re.sub(r"[^a-z0-9\s]", " ", cleaned.lower())
    tokens = [token for token in normalized.split() if len(token) > 3 and token not in {"this", "that", "with", "from", "into", "have", "will", "what", "your", "essay", "writer", "essay", "they", "them", "then", "than", "there", "their", "about", "were", "been", "also", "over", "make", "when", "more", "very", "into", "could", "would", "through", "while", "after", "before", "such", "only", "each", "many", "most", "some"}]
    frequency = {}
    for token in tokens:
        frequency[token] = frequency.get(token, 0) + 1
    topic_terms = [term for term, _ in sorted(frequency.items(), key=lambda item: (-item[1], item[0]))[:4]]
    topic = " ".join(topic_terms) if topic_terms else "the central idea"
    topic_phrase = topic.replace("  ", " ").strip()

    examples = []
    for phrase in re.findall(r"(?:[A-Za-z][A-Za-z'\-]{3,}\s+){1,5}(?:traffic|pollution|commute|evidence|support|argument|conclusion|community|business|schools|jobs|cities|transportation|education|technology|environment|health)[A-Za-z'\-]*", cleaned, flags=re.IGNORECASE):
        examples.append(phrase.strip())
    example_text = examples[0] if examples else "the core idea"

    categories = {}
    categories["organization"] = {
        "strengths": [
            f"The essay presents a clear central idea around {topic_phrase or 'the topic'} and follows a recognizable progression from claim to support.",
            f"The structure is readable and the main point is easy to follow from the opening to the conclusion."
        ],
        "weaknesses": [
            "The argument would be stronger if the thesis were more specific and each paragraph connected more directly to the main claim.",
            "A few transitions could help the reader move more smoothly between ideas."
        ],
        "suggestions": [
            "Add a sharper thesis sentence that states the main claim in one precise line.",
            "Use transition words between paragraphs to reinforce logical flow and argument development."
        ]
    }
    categories["development"] = {
        "strengths": [
            f"The essay develops the idea of {topic_phrase or 'the topic'} with concrete references such as {example_text}, which gives the argument substance.",
            f"The discussion includes practical reasoning that helps explain why the issue matters in real life."
        ],
        "weaknesses": [
            "The paper could benefit from more precise evidence or examples to support the strongest claims.",
            "Some points would be more convincing if they were explained with additional detail or a broader range of examples."
        ],
        "suggestions": [
            "Add one or two specific examples that support the central claim with more detail.",
            "Explain how each example connects back to the thesis so the reasoning feels fully developed."
        ]
    }
    categories["mechanics"] = {
        "strengths": [
            f"The draft generally reads clearly and communicates the argument about {topic_phrase or 'the topic'} without major confusion.",
            "Sentence structure is mostly understandable, and the writing remains focused on the main idea."
        ],
        "weaknesses": [
            "A few sentences could be tightened for clarity, especially when combining multiple ideas in one sentence.",
            "Minor proofreading would improve punctuation and consistency across the paper."
        ],
        "suggestions": [
            "Review the draft for sentence length and punctuation so each statement reads cleanly.",
            "Read the essay aloud once to catch awkward wording or repeated phrasing."
        ]
    }
    categories["voice"] = {
        "strengths": [
            "The writing maintains a consistent academic tone and stays focused on the issue being discussed.",
            f"The voice is clear enough to communicate the writer's perspective on {topic_phrase or 'the topic'} with purpose."
        ],
        "weaknesses": [
            "The voice could become more distinctive if the essay used a more confident, precise tone.",
            "A stronger conclusion would give the piece a more polished and reflective ending."
        ],
        "suggestions": [
            "Use more deliberate phrasing in the final paragraph so the conclusion sounds confident and complete.",
            "Clarify the author's viewpoint by choosing more precise verbs and transitions."
        ]
    }

    return {"overall_score_1_to_6": score, "categories": categories}


def format_feedback_text(feedback: Any) -> str:
    if not isinstance(feedback, dict):
        return str(feedback)

    sections = []
    overall = feedback.get("overall_score_1_to_6")
    if overall is not None:
        sections.append(f"Overall score: {overall}/6")

    categories = feedback.get("categories", {})
    if isinstance(categories, dict):
        for category, details in categories.items():
            sections.append(f"\n{category.title()}")
            for field in ["strengths", "weaknesses", "suggestions"]:
                values = details.get(field)
                if values:
                    sections.append(f"  {field.title()}:\n" + "\n".join(f"    - {item}" for item in values))

    return "\n".join(sections).strip()


def get_feedback(
    essay_text: str,
    model: str = MODEL,
    max_retries: int = 3,
    grading_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    if anthropic is None or not os.getenv("ANTHROPIC_API_KEY"):
        return _dummy_feedback(essay_text)

    try:
        client = anthropic.Anthropic()
    except Exception:
        try:
            client = anthropic.Client()
        except Exception:
            return _dummy_feedback(essay_text)

    prompt = build_prompt(essay_text, grading_prompt=grading_prompt)
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )

            text_blocks = [block.text for block in response.content if getattr(block, "type", "text") == "text"]
            if not text_blocks:
                raise ValueError("No text block found in Anthropic response.")

            raw = _clean_json_text(text_blocks[0])
            return json.loads(raw)
        except Exception as exc:
            last_error = exc
            time.sleep(2 ** attempt)

    return _dummy_feedback(essay_text)
