import json
from services.llm import generate_completion

def generate_remediation(question, user_incorrect_answer, correct_answer, evidence_quote):
    """Generate a structured teaching moment explaining why the answer was wrong."""
    prompt = f"""You are a supportive corporate trainer. The learner just answered a quiz question incorrectly.
Your goal is to explain why their answer was wrong, why the correct answer is right, and provide a helpful memory hook.
Base your explanation entirely on the provided evidence.

Question: {question}
User's Incorrect Answer: {user_incorrect_answer}
Correct Answer: {correct_answer}
Policy Evidence: {evidence_quote}

Return a raw JSON object with these keys (no markdown formatting):
"why_incorrect": A gentle explanation of why the user's answer doesn't fit the policy.
"why_correct": An explanation of the correct policy based on the evidence.
"memory_hook": A short, catchy tip to help them remember this for next time.
"""
    try:
        response = generate_completion(prompt, temperature=0.3)
        response = response.replace("```json", "").replace("```", "").strip()
        return json.loads(response)
    except Exception as e:
        return {"error": str(e)}

def generate_explain_again(question, user_incorrect_answer, correct_answer, previous_explanation):
    """Generate a simpler, alternate-mode explanation that acknowledges the previous confusion."""
    prompt = f"""The learner is still confused after your first explanation.
They missed this question: "{question}"
They guessed: "{user_incorrect_answer}"
Correct answer: "{correct_answer}"

Previous explanation given:
{previous_explanation}

Provide a MUCH simpler, analogy-based, or ELI5 (Explain Like I'm 5) explanation to help them grasp the concept.
Keep it encouraging and brief. Return just the plain text explanation.
"""
    try:
        return generate_completion(prompt, temperature=0.5)
    except Exception as e:
        return f"Error generating alternate explanation: {str(e)}"
