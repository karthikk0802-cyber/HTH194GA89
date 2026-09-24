import json
from services.llm import generate_completion

def evaluate_scenario_response(scenario_text, user_response, evidence_context):
    """Evaluate a user's free-text response to a complex scenario using a rubric."""
    prompt = f"""You are an expert evaluator grading a new employee's response to a critical scenario.
You must score them on four dimensions: Policy Knowledge, Decision Quality, Procedure Adherence, and Risk Awareness.
Score each out of 10. Also provide a brief, actionable feedback summary.

Base your evaluation STRICTLY on the knowledge base evidence provided.

Scenario: {scenario_text}
Employee Response: {user_response}
Knowledge Base Evidence: {evidence_context}

Return a raw JSON object (no markdown) with these keys:
"policy_score": integer (0-10)
"decision_score": integer (0-10)
"procedure_score": integer (0-10)
"risk_score": integer (0-10)
"feedback": brief string
"""
    try:
        response = generate_completion(prompt, temperature=0.1)
        response = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(response)
        
        # Calculate overall mastery impact (0 to 100 scale based on avg)
        avg = (data["policy_score"] + data["decision_score"] + data["procedure_score"] + data["risk_score"]) / 4.0
        data["mastery_impact"] = int(avg * 10)
        return data
    except Exception as e:
        return {"error": str(e)}

SCENARIOS = {
    "security": {
        "title": "Leaked API Key",
        "text": "You realize you accidentally committed a production API key to a public GitHub repository 5 minutes ago. What do you do? Walk through your immediate steps.",
        "topic_id": "security"
    },
    "git_workflow": {
        "title": "Merge Conflict Panic",
        "text": "You are trying to merge a hotfix into production, but there is a massive merge conflict in a core file. The original author is asleep in another timezone. How do you proceed?",
        "topic_id": "git_workflow"
    }
}
