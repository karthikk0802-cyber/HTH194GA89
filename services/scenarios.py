import json
import re
from services.llm import generate_completion, clean_json_response
from services.embedding import search_chroma

SCENARIOS = {
    "company_basics": {
        "title": "Core Hours & Expense Conflict",
        "text": "A newly hired remote engineer on your team wants to schedule a mandatory 3-hour team sync at 7:00 AM EST and also submits a $120 lunch receipt with no itemization from their local cafe. As a teammate/lead, how do you handle this according to Nexora policy?",
        "topic_id": "company_basics"
    },
    "security": {
        "title": "Leaked Production API Key",
        "text": "You realize you accidentally committed a production API key to a public GitHub repository 5 minutes ago. What do you do? Walk through your immediate containment steps, communication channels, and rotation procedures.",
        "topic_id": "security"
    },
    "git_workflow": {
        "title": "Merge Conflict & Urgent Hotfix",
        "text": "You are preparing to merge a critical production hotfix, but there is a merge conflict in a core service. The original author is offline in another timezone. How do you safely resolve, test, and merge this change according to Nexora Git and PR approval standards?",
        "topic_id": "git_workflow"
    },
    "deployment": {
        "title": "Friday Release Pressure",
        "text": "A product stakeholder is urgently pressuring you to deploy a major unverified feature release to production on Friday at 4:30 PM EST before the weekend. How do you respond and what procedures do you follow?",
        "topic_id": "deployment"
    },
    "architecture": {
        "title": "Microservices Communication Dilemma",
        "text": "A new service requires real-time synchronous communication with 4 other microservices during checkout. An engineer proposes chaining HTTP REST calls directly. What architectural guidance and alternative patterns do you propose?",
        "topic_id": "architecture"
    },
    "tools": {
        "title": "Secrets Sharing via Direct Message",
        "text": "A colleague asks you to send the database master password over Slack direct message because they cannot access Vault. How do you respond and assist them safely?",
        "topic_id": "tools"
    }
}

def evaluate_scenario_response(scenario_text: str, user_response: str, evidence_context: str = "", topic_id: str = "security") -> dict:
    """Evaluate a user's free-text response to a complex scenario using a grounded 4-pillar rubric strictly against company policy documents."""
    
    clean_user_resp = (user_response or "").strip()
    
    # Fast path for empty or trivial responses
    if len(clean_user_resp) < 15:
        return {
            "policy_score": 1,
            "decision_score": 1,
            "procedure_score": 1,
            "risk_score": 1,
            "feedback": "Your response is too brief or incomplete to demonstrate compliance with company policies. Please provide a detailed action plan outlining specific containment steps and protocols.",
            "mastery_impact": 10
        }
    
    # 1. Fetch live ChromaDB context from PDF/Document Knowledge Base if not passed or brief
    if not evidence_context or len(evidence_context) < 50:
        search_query = f"{scenario_text} {topic_id} official policies, rules, and incident handling guidelines"
        search_res = search_chroma(search_query, n_results=4)
        if search_res and search_res.get('documents') and search_res['documents'][0]:
            docs = search_res['documents'][0]
            evidence_context = "\n---\n".join(docs)
        else:
            evidence_context = "Official Nexora policy mandates immediate communication in private Slack channels, password/credential rotation, peer review, itemized expense receipts, and adherence to core hours."

    prompt = f"""You are a strict, impartial corporate compliance and technical assessor grading an employee's response to an applied scenario at Nexora.

CRITICAL ASSESSMENT INSTRUCTIONS:
1. Thoroughly analyze the Employee Response below.
2. Cross-verify the response against the official Knowledge Base Document Context provided.
3. STRICT EVALUATION:
   - If the response is incorrect, dangerous, ignores company policy, or omits mandatory steps (such as specific reporting channels, rotation timelines, expense itemization rules, or core hours), award LOW scores (1 to 5 out of 10) on relevant pillars.
   - If the response adheres to official Nexora policy and outlines effective, step-by-step procedures and risk mitigations, award appropriate scores (6 to 10 out of 10).
   - DO NOT award default passing or high scores for vague, incorrect, or incomplete answers.
4. Provide a 2-3 sentence feedback summary explaining what was correct, what was wrong, and what specific policy steps were missing based on the document context.

Scenario: {scenario_text}
Employee Response: {clean_user_resp}
Official Knowledge Base Document Context:
{evidence_context}

SCORING DIMENSIONS (Scale 1 to 10 as integers):
- policy_score: Adherence to official company guidelines, hours, SLAs, and escalation channels.
- decision_score: Soundness, safety, and logical reasoning of proposed actions.
- procedure_score: Following step-by-step containment, rotation, or approval protocols.
- risk_score: Identification and mitigation of security, operational, financial, or legal risks.

Return ONLY a raw JSON object with no markdown code fences:
{{
  "policy_score": <1-10 integer>,
  "decision_score": <1-10 integer>,
  "procedure_score": <1-10 integer>,
  "risk_score": <1-10 integer>,
  "feedback": "<concise feedback referencing official document policy requirements>"
}}
"""
    try:
        response_text = generate_completion(prompt, temperature=0.1)
        clean_text = clean_json_response(response_text)
        
        json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
        else:
            data = json.loads(clean_text)
            
        p_score = max(1, min(10, int(data.get("policy_score", 3))))
        d_score = max(1, min(10, int(data.get("decision_score", 3))))
        pr_score = max(1, min(10, int(data.get("procedure_score", 3))))
        r_score = max(1, min(10, int(data.get("risk_score", 3))))
        
        avg = (p_score + d_score + pr_score + r_score) / 4.0
        data["policy_score"] = p_score
        data["decision_score"] = d_score
        data["procedure_score"] = pr_score
        data["risk_score"] = r_score
        data["feedback"] = str(data.get("feedback", "Evaluation completed against company policy documents."))
        data["mastery_impact"] = int(avg * 10)
        return data
    except Exception as e:
        print(f"[ScenarioEval Error] {e}")
        return {
            "policy_score": 3,
            "decision_score": 3,
            "procedure_score": 3,
            "risk_score": 3,
            "feedback": f"Could not fully verify response against policy documents due to an evaluation processing issue ({str(e)}). Please ensure your response outlines complete step-by-step procedures.",
            "mastery_impact": 30
        }

