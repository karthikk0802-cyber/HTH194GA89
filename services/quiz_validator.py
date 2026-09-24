from services.llm import generate_completion

def validate_quiz_question(quiz_data, context_text):
    """
    Validation layer to block unsupported, ambiguous, or hallucinated questions.
    Returns True if valid, False if rejected.
    """
    if "error" in quiz_data:
        return False
        
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
    except:
        return False
