from services.llm import generate_completion, get_mistral_client

def _structural_check(quiz_data):
    """Deterministic validity: shape + answer-in-options + evidence present."""
    if not isinstance(quiz_data, dict) or "error" in quiz_data:
        return False
    question = (quiz_data.get("question") or "").strip()
    options = quiz_data.get("options") or []
    answer = (quiz_data.get("correct_answer") or "").strip()
    evidence = (quiz_data.get("evidence_quote") or "").strip()
    if not question or len(options) != 4 or not answer or not evidence:
        return False
    if quiz_data["correct_answer"] not in options:
        return False
    if len({o.strip().lower() for o in options}) != 4:
        return False
    return True


def validate_quiz_question(quiz_data, context_text):
    """
    Two-tier validation gate.
    Tier 1 (always): structural check — shape, 4 distinct options,
    answer among options, non-empty evidence quote.
    Tier 2 (Mistral key configured): strict LLM groundedness audit.
    Offline, Tier 1 alone passes curated bank items instead of failing
    everything (previous behavior: fallback text never said VALID).
    Returns True if valid, False if rejected.
    """
    if not _structural_check(quiz_data):
        return False

    if get_mistral_client() is None:
        return True

    prompt = f"""You are a strict QA auditor. Review the following quiz question against the provided evidence.
You must reject the question if:
1. The correct answer is NOT explicitly supported by the evidence.
2. The question is ambiguous or confusing.
3. The evidence contradicts the answer.

Question: {quiz_data.get('question')}
Options: {quiz_data.get('options')}
Declared Correct Answer: {quiz_data.get('correct_answer')}
Evidence Quote Provided: {quiz_data.get('evidence_quote')}

Is this question 100% valid and supported? Answer ONLY with "VALID" or "INVALID".
"""
    try:
        response = generate_completion(prompt, temperature=0.0).strip().upper()
        if "VALID" in response and "INVALID" not in response:
            return True
        return False
    except Exception:
        return False
