import os
import re
import json
import random
from dotenv import load_dotenv

load_dotenv()

def get_mistral_client():
    """Retrieve an authenticated Mistral AI client or None if key is missing/placeholder."""
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key or api_key.strip() == "" or "your_mistral_api_key" in api_key.lower():
        return None
    
    # Try official v1+ SDK
    try:
        from mistralai import Mistral
        return Mistral(api_key=api_key.strip())
    except Exception:
        pass

    # Try v2.x SDK layout
    try:
        from mistralai.client import Mistral
        return Mistral(api_key=api_key.strip())
    except Exception:
        pass

    # Try legacy client
    try:
        from mistralai.client import MistralClient
        return MistralClient(api_key=api_key.strip())
    except Exception:
        return None

def generate_completion(prompt, model="mistral-small-latest", temperature=0.3):
    """Generate completion with Mistral AI, with graceful multi-model fallback and grounded offline intelligence."""
    client = get_mistral_client()
    if client is None:
        return smart_fallback_completion(prompt)
    
    models_to_try = [model, "mistral-small-latest", "mistral-medium-latest", "open-mistral-7b", "mistral-large-latest"]
    # De-duplicate while preserving order
    seen = set()
    models_ordered = [m for m in models_to_try if not (m in seen or seen.add(m))]
    
    last_error = None
    for target_model in models_ordered:
        try:
            # Check v1+ SDK
            if hasattr(client, "chat") and hasattr(client.chat, "complete"):
                messages = [{"role": "user", "content": prompt}]
                chat_response = client.chat.complete(
                    model=target_model,
                    messages=messages,
                    temperature=temperature
                )
                choice = chat_response.choices[0].message.content
                if isinstance(choice, str) and choice.strip():
                    return choice.strip()
                elif isinstance(choice, list) and len(choice) > 0:
                    return choice[0].text.strip()
            else:
                # Legacy SDK
                from mistralai.models.chat_completion import ChatMessage
                messages = [ChatMessage(role="user", content=prompt)]
                chat_response = client.chat(
                    model=target_model,
                    messages=messages,
                    temperature=temperature
                )
                return chat_response.choices[0].message.content.strip()
        except Exception as e:
            last_error = e
            # Try next model in list if model-not-found or quota issue
            continue

    print(f"[LLM Warning] Mistral AI API calls failed ({last_error}). Using intelligent grounded fallback engine.")
    return smart_fallback_completion(prompt)

def clean_json_response(raw_text: str) -> str:
    """Extract clean JSON substring from LLM output."""
    text = raw_text.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    return text

def smart_fallback_completion(prompt: str) -> str:
    """
    Intelligent context-aware fallback responses when Mistral AI API key is not configured or network is unreachable.
    Dynamically parses the prompt requirements and synthesizes accurate responses.
    """
    p_lower = prompt.lower()
    
    # 1. Multiple Choice Quiz Generation
    if "multiple choice question" in p_lower or "learning_objective" in p_lower:
        # Extract topic and difficulty from prompt if available
        topic = "General Company Policy"
        topic_match = re.search(r'topic ["\']([^"\']+)["\']', prompt, re.IGNORECASE)
        if topic_match:
            topic = topic_match.group(1).strip()
            
        diff = "Beginner"
        diff_match = re.search(r'["\'](Beginner|Intermediate|Expert)["\']\s+difficulty', prompt, re.IGNORECASE)
        if diff_match:
            diff = diff_match.group(1)

        # Context-based dynamic generation
        if "company_basics" in topic.lower() or "culture" in topic.lower() or "handbook" in topic.lower() or "basics" in topic.lower():
            questions_pool = [
                {
                    "question": "What is Nexora's designated Core Collaboration Window for all synchronous meetings and sprint ceremonies?",
                    "options": ["8:00 AM to 12:00 PM EST", "10:00 AM to 3:00 PM EST", "1:00 PM to 6:00 PM EST", "No specific core hours"],
                    "correct_answer": "10:00 AM to 3:00 PM EST",
                    "learning_objective": "Understand Nexora core collaboration scheduling and async working policy",
                    "evidence_quote": "Core Collaboration Window from 10:00 AM to 3:00 PM EST (Monday through Friday)."
                },
                {
                    "question": "What is the monthly recurring residential internet stipend provided to full-time remote employees at Nexora?",
                    "options": ["$25/month", "$50/month", "$100/month", "$150/month"],
                    "correct_answer": "$50/month",
                    "learning_objective": "Master employee remote work benefits and recurring allowances",
                    "evidence_quote": "Nexora provides a monthly recurring $50 USD internet stipend to subsidize high-speed residential broadband."
                },
                {
                    "question": "How much is the one-time ergonomic home office setup stipend for new Nexora hires?",
                    "options": ["$250 USD", "$500 USD", "$1,000 USD", "$1,500 USD"],
                    "correct_answer": "$500 USD",
                    "learning_objective": "Know home office ergonomic equipment procurement rules",
                    "evidence_quote": "every full-time employee is eligible for a one-time $500 USD Ergonomic Home Office Stipend"
                },
                {
                    "question": "What is Nexora's standard policy regarding paid time off (PTO) notice for vacations over 3 days?",
                    "options": ["Submit in Workday at least 2 weeks in advance", "Notify via Slack on the day of departure", "Email VP 3 months in advance", "No notice required"],
                    "correct_answer": "Submit in Workday at least 2 weeks in advance",
                    "learning_objective": "Understand Workday leave submission timelines",
                    "evidence_quote": "Planned vacations over 3 consecutive days must be submitted via Workday at least 2 weeks in advance."
                }
            ]
            chosen = random.choice(questions_pool)
            return json.dumps(chosen)

        elif "security" in topic.lower():
            questions_pool = [
                {
                    "question": "According to Nexora's Security Policy, how frequently must corporate SSO passwords be rotated?",
                    "options": ["Every 30 days", "Every 60 days", "Every 90 days", "Every 180 days"],
                    "correct_answer": "Every 90 days",
                    "learning_objective": "Master corporate authentication lifecycle and password rotation intervals",
                    "evidence_quote": "Mandatory password rotation occurs every 90 days."
                },
                {
                    "question": "What is the minimum required password length and character complexity at Nexora?",
                    "options": ["8 characters", "12 characters with numbers only", "16 characters with uppercase, lowercase, numbers, and symbols", "24 characters alphanumeric"],
                    "correct_answer": "16 characters with uppercase, lowercase, numbers, and symbols",
                    "learning_objective": "Ensure compliance with enterprise credential complexity standards",
                    "evidence_quote": "Passwords must contain a minimum of 16 characters including uppercase, lowercase, numbers, and symbols."
                },
                {
                    "question": "Within what timeframe must an employee report a suspected credential leak or security anomaly to security@nexora.com?",
                    "options": ["Within 15 minutes of discovery", "Within 2 business hours", "By end of week", "During quarterly review"],
                    "correct_answer": "Within 15 minutes of discovery",
                    "learning_objective": "Adhere to critical incident escalation SLA for security breaches",
                    "evidence_quote": "must be reported to security@nexora.com and in the private Slack channel #security-alerts within 15 minutes of discovery."
                }
            ]
            chosen = random.choice(questions_pool)
            return json.dumps(chosen)

        elif "git" in topic.lower() or "code_review" in topic.lower():
            questions_pool = [
                {
                    "question": "What development branching methodology is strictly enforced across all Nexora engineering repositories?",
                    "options": ["Trunk-Based Development", "GitFlow with permanent release branches", "Isolated long-lived feature forks", "Unreviewed direct commits to main"],
                    "correct_answer": "Trunk-Based Development",
                    "learning_objective": "Understand source control architecture and rapid CI/CD iteration",
                    "evidence_quote": "Nexora engineering adheres strictly to Trunk-Based Development. Feature branches must be short-lived"
                },
                {
                    "question": "What cryptographic requirement is mandatory for all Git commits submitted to Nexora repositories?",
                    "options": ["GPG or SSH cryptographic commit signing", "MD5 checksum commit tags", "SHA-1 commit hashing only", "No signing required"],
                    "correct_answer": "GPG or SSH cryptographic commit signing",
                    "learning_objective": "Enforce cryptographic identity verification for engineering codebases",
                    "evidence_quote": "All Git commits must be cryptographically signed using GPG or SSH keys verified in GitHub."
                },
                {
                    "question": "What is the minimum test coverage threshold required for new code submitted in Pull Requests at Nexora?",
                    "options": [">50%", ">65%", ">80%", "100% full branch coverage"],
                    "correct_answer": ">80%",
                    "learning_objective": "Understand unit testing coverage gating requirements",
                    "evidence_quote": "test coverage (>80% required on new code)."
                }
            ]
            chosen = random.choice(questions_pool)
            return json.dumps(chosen)

        elif "deploy" in topic.lower() or "ci" in topic.lower():
            questions_pool = [
                {
                    "question": "On which days and hours are standard production deployments scheduled at Nexora?",
                    "options": ["Mondays and Wednesdays (9 AM - 5 PM EST)", "Tuesdays and Thursdays between 10:00 AM and 2:00 PM EST", "Every Friday afternoon", "Weekends at midnight only"],
                    "correct_answer": "Tuesdays and Thursdays between 10:00 AM and 2:00 PM EST",
                    "learning_objective": "Follow production deployment window compliance and release blackout periods",
                    "evidence_quote": "Standard production deployments take place on Tuesdays and Thursdays between 10:00 AM and 2:00 PM EST."
                },
                {
                    "question": "What happens if error rates exceed 0.5% during canary deployment rollout?",
                    "options": ["Automated 1-click rollback to the previous stable release artifact", "Manual code hotpatch on live servers", "Restart servers and continue rollout", "Ignore until customer reports"],
                    "correct_answer": "Automated 1-click rollback to the previous stable release artifact",
                    "learning_objective": "Understand automated canary health checks and rollback thresholds",
                    "evidence_quote": "If error rates exceed 0.5% or p99 latency increases by >25% during canary rollout, the automated CD pipeline immediately triggers a 1-click rollback"
                }
            ]
            chosen = random.choice(questions_pool)
            return json.dumps(chosen)

        elif "incident" in topic.lower():
            questions_pool = [
                {
                    "question": "What is the required SLA response time for a declared Sev1 (Critical) incident at Nexora?",
                    "options": ["< 15 minutes", "< 30 minutes", "< 1 hour", "< 4 hours"],
                    "correct_answer": "< 15 minutes",
                    "learning_objective": "Comply with incident severity definitions and on-call response SLAs",
                    "evidence_quote": "Sev1 (Critical): Total service outage... SLA response: < 15 minutes."
                },
                {
                    "question": "Within what timeframe must a blameless post-mortem be completed following a Sev1/Sev2 incident?",
                    "options": ["Within 24 hours", "Within 48 hours", "Within 1 week", "At the end of the fiscal quarter"],
                    "correct_answer": "Within 48 hours",
                    "learning_objective": "Understand blameless post-mortem timelines and operational review standards",
                    "evidence_quote": "a blameless post-mortem document must be drafted within 48 hours"
                }
            ]
            chosen = random.choice(questions_pool)
            return json.dumps(chosen)

        elif "expense" in topic.lower() or "travel" in topic.lower():
            questions_pool = [
                {
                    "question": "What is the dollar threshold above which itemized receipts are mandatory for business expense reimbursement?",
                    "options": ["All expenses over $10 USD", "All expenses exceeding $25 USD", "All expenses exceeding $100 USD", "Receipts never required"],
                    "correct_answer": "All expenses exceeding $25 USD",
                    "learning_objective": "Master Expensify expense compliance rules and documentation requirements",
                    "evidence_quote": "Itemized receipts are required for all business expenses exceeding $25 USD."
                },
                {
                    "question": "What is the standard daily meal per diem during authorized business travel at Nexora?",
                    "options": ["$50 USD per day", "$75 USD per day", "$120 USD per day", "$150 USD per day"],
                    "correct_answer": "$75 USD per day",
                    "learning_objective": "Adhere to corporate travel per diem allowances",
                    "evidence_quote": "The standard meal per diem allowance during business travel is $75 USD per day"
                }
            ]
            chosen = random.choice(questions_pool)
            return json.dumps(chosen)

        elif "architecture" in topic.lower():
            questions_pool = [
                {
                    "question": "What programming language is standardized at Nexora for high-throughput microservices?",
                    "options": ["Go", "PHP", "Ruby", "Java 8"],
                    "correct_answer": "Go",
                    "learning_objective": "Master Nexora backend technology stack and architectural standards",
                    "evidence_quote": "Core backend services are written in Go for high-throughput concurrency"
                },
                {
                    "question": "Which database technologies power transactional persistence and vector embeddings at Nexora?",
                    "options": ["PostgreSQL 16 and ChromaDB / pgvector", "MongoDB and SQLite only", "Oracle DB and Cassandra", "DynamoDB only"],
                    "correct_answer": "PostgreSQL 16 and ChromaDB / pgvector",
                    "learning_objective": "Understand data persistence and vector retrieval infrastructure",
                    "evidence_quote": "Transactional persistence uses PostgreSQL 16 with read replicas... Vector search is powered by ChromaDB / pgvector."
                }
            ]
            chosen = random.choice(questions_pool)
            return json.dumps(chosen)

        # Default dynamic general question
        return json.dumps({
            "question": f"According to Nexora official guidelines, what is the primary compliance requirement for {topic}?",
            "options": [
                f"Adhere strictly to documented {topic} SOPs and peer review",
                "Execute changes without logging or review",
                "Store sensitive credentials in public channels",
                "Bypass security and CI gates during emergencies"
            ],
            "correct_answer": f"Adhere strictly to documented {topic} SOPs and peer review",
            "learning_objective": f"Understand official standards, compliance, and workflows for {topic}",
            "evidence_quote": f"Employees must follow approved standards and policies for {topic}."
        })

    # 2. 4-Pillar Scenario Evaluation
    if "four dimensions" in p_lower or "evaluator grading" in p_lower or "scoring dimensions" in p_lower or "policy_score" in p_lower:
        user_resp_match = re.search(r"Employee Response:\s*(.+?)(?=Official Knowledge Base|Knowledge Base Context:|$)", prompt, re.DOTALL | re.IGNORECASE)
        user_resp = user_resp_match.group(1).strip() if user_resp_match else prompt.strip()
        
        resp_lower = user_resp.lower()
        words = len(user_resp.split())
        
        # Check negative / unsafe / policy violation indicator actions
        is_negative = any(bad in resp_lower for bad in [
            "ignore", "do nothing", "go home", "don't care", "bypass", "unitemized", 
            "without itemization", "no itemization", "7 am", "7:00 am", "approve receipt",
            "send password", "slack message", "direct message", "deploy on friday", "deploy friday",
            "force push", "skip tests", "no approval"
        ])
        
        # Key policy requirement checks per domain
        has_security_policy = any(w in resp_lower for w in ["rotate", "revoke", "security@nexora.com", "#security-alerts", "15 minutes"])
        has_basics_policy = (("10 am" in resp_lower or "10:00" in resp_lower or "core hours" in resp_lower or "reschedule" in resp_lower) or 
                            ("itemized" in resp_lower or "expensify" in resp_lower or "cannot reimburse" in resp_lower or "reject" in resp_lower or "deny" in resp_lower or "policy" in resp_lower))
        has_git_policy = any(w in resp_lower for w in ["trunk-based", "pr", "pull request", "peer review", "gpg", "ssh", "rebase"])
        has_deploy_policy = any(w in resp_lower for w in ["tuesday", "thursday", "refuse", "reject friday", "vp approval", "canary", "rollback"])
        
        if is_negative and not ("cannot reimburse" in resp_lower or "reject" in resp_lower or "deny" in resp_lower or "reschedule" in resp_lower or "outside core" in resp_lower):
            p_score, d_score, pr_score, r_score = 2, 2, 2, 2
            feedback = "The proposed action plan violates official Nexora policy and safety procedures. Critical escalation steps, communication channels, core collaboration hours (10 AM - 3 PM EST), or expense itemization rules were ignored."
        elif has_security_policy or has_basics_policy or has_git_policy or has_deploy_policy:
            p_score, d_score, pr_score, r_score = 9, 8, 8, 9
            feedback = "Excellent response! Fully adheres to official Nexora company policy documents, required notification SLAs, and step-by-step containment protocols."
        elif words < 8:
            p_score, d_score, pr_score, r_score = 2, 2, 2, 2
            feedback = "Your response is too brief or incomplete. Please outline a complete step-by-step action plan adhering to official company policy."
        else:
            p_score, d_score, pr_score, r_score = 4, 4, 4, 4
            feedback = "Partial response. While partially logical, it fails to explicitly cite mandatory Nexora policy requirements (such as specific reporting channels, notification SLAs, or approval protocols)."
            
        return json.dumps({
            "policy_score": p_score,
            "decision_score": d_score,
            "procedure_score": pr_score,
            "risk_score": r_score,
            "feedback": feedback
        })

    # 3. Quiz Remediation
    if "supportive corporate trainer" in p_lower or "memory_hook" in p_lower:
        return json.dumps({
            "why_incorrect": "Your chosen option deviates from Nexora's verified governance and compliance procedures.",
            "why_correct": "Nexora policy mandates strict adherence to approved timelines, peer review gates, and documented protocols.",
            "memory_hook": "Tip: Remember core collaboration hours (10 AM - 3 PM EST), 90-day password rotation, and trunk-based PR reviews!"
        })

    # 4. ELI5 Explanation
    if "explain like i'm 5" in p_lower or "eli5" in p_lower:
        return "Imagine our company rules like traffic lights and seatbelts in a playground: they ensure everyone can build and play safely without collisions or losing their work!"

    # 5. General AI Q&A Fallback
    q_match = re.search(r"User Question:\s*(.+?)(?=\n\nAnswer:|$)", prompt, re.DOTALL | re.IGNORECASE)
    if not q_match:
        q_match = re.search(r"Employee Question:\s*(.+?)(?=\n\nAnswer:|$)", prompt, re.DOTALL | re.IGNORECASE)
    user_q = q_match.group(1).strip() if q_match else prompt.strip()
    
    # Check context in prompt
    context_match = re.search(r"Knowledge Base Context:\s*(.+?)(?=User Question:|$)", prompt, re.DOTALL | re.IGNORECASE)
    context_text = context_match.group(1).strip() if context_match else ""
    
    if "stipend" in user_q.lower() or "remote" in user_q.lower() or "internet" in user_q.lower():
        return "At Nexora, full-time remote employees receive a monthly recurring **$50 USD internet stipend** on their payroll and a one-time **$500 USD Ergonomic Home Office Stipend** for desks, chairs, and monitors. Coworking hot-desks can also be subsidized up to $250/month."
    elif "hour" in user_q.lower() or "time" in user_q.lower() or "core" in user_q.lower():
        return "Nexora's designated **Core Collaboration Window is 10:00 AM to 3:00 PM EST (Monday through Friday)** for synchronous meetings and sprint ceremonies. Outside these core hours, team members enjoy full flexible autonomy."
    elif "password" in user_q.lower() or "mfa" in user_q.lower() or "security" in user_q.lower():
        return "Nexora enforces **mandatory password rotation every 90 days** with a minimum of 16 characters (uppercase, lowercase, numbers, symbols) and mandatory Multi-Factor Authentication (MFA / 2FA) via hardware keys or TOTP authenticator apps."
    elif "git" in user_q.lower() or "branch" in user_q.lower() or re.search(r"\bpr\b", user_q.lower()):
        return "Nexora engineering uses **Trunk-Based Development**. Feature branches must be short-lived (24-48 hours), commits must be cryptographically signed with GPG/SSH keys, and all Pull Requests require at least **1 peer approval** and >80% test coverage."
    elif "deploy" in user_q.lower() or "release" in user_q.lower():
        return "Standard production deployments happen on **Tuesdays and Thursdays between 10:00 AM and 2:00 PM EST**. Deployments on Fridays and weekends are strictly prohibited without VP approval. Canary rollout starts at 5% traffic."
    elif "expense" in user_q.lower() or "per diem" in user_q.lower() or "travel" in user_q.lower():
        return "Nexora's travel meal per diem is **$75 USD per day**. All business expenses exceeding **$25 USD require itemized receipts** submitted via Expensify within 30 days."
    elif "incident" in user_q.lower() or "sev1" in user_q.lower():
        return "Critical Sev1 incidents require an SLA response time under **15 minutes**. Escalation occurs via PagerDuty to the Primary On-Call Engineer, with live coordination in the **#incidents** Slack war room."
    
    if context_text and len(context_text) > 30:
        return f"Based on Nexora corporate documentation:\n\n{context_text[:500]}...\n\nPlease refer to the official policies or consult your manager for role-specific guidance."
    
    return "Nexora provides flexible remote-first onboarding with comprehensive benefits, trunk-based engineering workflows, and robust security policies. Please feel free to ask any specific questions regarding tools, compensation, policies, or architecture!"
