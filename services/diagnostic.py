import random
import re
from services.roles import TOPICS, get_role_topics

# Comprehensive Master Diagnostic Question Catalog
MASTER_DIAGNOSTIC_BANK = [
    # Company Basics & Culture
    {
        "id": "cb_1",
        "topic": "company_basics",
        "question": "What are the core collaboration hours at Nexora for synchronous meetings?",
        "options": ["9:00 AM to 5:00 PM EST", "10:00 AM to 3:00 PM EST", "No core hours (100% async)", "8:00 AM to 1:00 PM EST"],
        "answer": "10:00 AM to 3:00 PM EST",
        "explanation": "Nexora enforces a Core Collaboration Window from 10:00 AM to 3:00 PM EST Monday through Friday."
    },
    {
        "id": "cb_2",
        "topic": "company_basics",
        "question": "What is the monthly internet allowance for full-time remote employees?",
        "options": ["$25/month", "$50/month", "$100/month", "$150/month"],
        "answer": "$50/month",
        "explanation": "Nexora provides a monthly recurring $50 USD internet stipend on payroll."
    },
    {
        "id": "cb_3",
        "topic": "company_basics",
        "question": "What is the one-time ergonomic home office setup stipend for new employees?",
        "options": ["$250 USD", "$500 USD", "$1,000 USD", "$1,500 USD"],
        "answer": "$500 USD",
        "explanation": "Every full-time employee receives a one-time $500 USD Ergonomic Home Office Stipend."
    },
    {
        "id": "cb_4",
        "topic": "company_basics",
        "question": "What is the minimum recommended annual PTO days employees are encouraged to take?",
        "options": ["5 days", "10 days", "20 days (4 weeks)", "Unlimited (no minimum recommended)"],
        "answer": "20 days (4 weeks)",
        "explanation": "Under the flexible PTO policy, employees are encouraged to take at least 20 PTO days annually."
    },

    # Security & Compliance
    {
        "id": "sec_1",
        "topic": "security",
        "question": "How often must you rotate your corporate SSO password?",
        "options": ["Every 30 days", "Every 60 days", "Every 90 days", "Never"],
        "answer": "Every 90 days",
        "explanation": "Mandatory password rotation occurs every 90 days with a minimum of 16 characters."
    },
    {
        "id": "sec_2",
        "topic": "security",
        "question": "Within what timeframe must suspected security incidents or leaked credentials be reported?",
        "options": ["Within 15 minutes of discovery", "Within 2 hours", "By end of the business day", "During weekly 1-on-1"],
        "answer": "Within 15 minutes of discovery",
        "explanation": "Suspected breaches must be reported to security@nexora.com and in #security-alerts within 15 minutes."
    },
    {
        "id": "sec_3",
        "topic": "security",
        "question": "How often are phishing simulations conducted by the InfoSec team?",
        "options": ["Monthly", "Quarterly", "Bi-Annually", "Yearly"],
        "answer": "Quarterly",
        "explanation": "Phishing simulations and awareness drills are conducted quarterly."
    },
    {
        "id": "sec_4",
        "topic": "security",
        "question": "What screen lock timeout is enforced when a workstation is left unattended?",
        "options": ["1 minute", "5 minutes", "15 minutes", "30 minutes"],
        "answer": "5 minutes",
        "explanation": "Screen lock timeout is automatically enforced at 5 minutes of inactivity."
    },

    # Tools & Workflows
    {
        "id": "tools_1",
        "topic": "tools",
        "question": "What tool is the primary platform for internal real-time and asynchronous messaging?",
        "options": ["Email", "Zoom", "Slack", "Jira"],
        "answer": "Slack",
        "explanation": "Slack is the primary internal messaging tool; threads are mandatory for topical discussions."
    },
    {
        "id": "tools_2",
        "topic": "tools",
        "question": "Where should planned vacation leave (over 3 days) be officially requested?",
        "options": ["Slack message", "Workday", "Jira ticket", "Email to CEO"],
        "answer": "Workday",
        "explanation": "Leave must be logged in Workday at least 2 weeks in advance for planned vacations."
    },
    {
        "id": "tools_3",
        "topic": "tools",
        "question": "What platform is used to submit itemized receipts for travel and expense reimbursements?",
        "options": ["Expensify", "Concur", "Workday", "QuickBooks"],
        "answer": "Expensify",
        "explanation": "All business expenses exceeding $25 USD require itemized receipts submitted via Expensify."
    },

    # Git Workflow
    {
        "id": "git_1",
        "topic": "git_workflow",
        "question": "What development branching methodology does Nexora engineering enforce?",
        "options": ["GitFlow", "Trunk-based development", "Feature branching without main", "Direct commits to production"],
        "answer": "Trunk-based development",
        "explanation": "Nexora strictly enforces Trunk-Based Development with short-lived feature branches."
    },
    {
        "id": "git_2",
        "topic": "git_workflow",
        "question": "How many peer approvals from CODEOWNERS are mandatory for a Pull Request to merge?",
        "options": ["0", "1", "2", "3"],
        "answer": "1",
        "explanation": "PRs require at least 1 peer approval from an engineer in CODEOWNERS."
    },
    {
        "id": "git_3",
        "topic": "git_workflow",
        "question": "What cryptographic requirement is mandatory for all Git commits at Nexora?",
        "options": ["GPG or SSH commit signing", "MD5 commit tags", "Plain unverified commit", "HTTPS basic auth"],
        "answer": "GPG or SSH commit signing",
        "explanation": "All commits must be cryptographically signed using GPG or SSH keys verified in GitHub."
    },
    {
        "id": "git_4",
        "topic": "git_workflow",
        "question": "What is the minimum unit test coverage threshold required for new code in PRs?",
        "options": [">50%", ">65%", ">80%", "100%"],
        "answer": ">80%",
        "explanation": "Automated CI gates require at least 80% test coverage on newly added code."
    },

    # Deployment & CI/CD
    {
        "id": "dep_1",
        "topic": "deployment",
        "question": "On which days are standard production deployments scheduled?",
        "options": ["Mondays and Wednesdays", "Tuesdays and Thursdays", "Fridays", "Everyday including weekends"],
        "answer": "Tuesdays and Thursdays",
        "explanation": "Production deployments occur Tuesdays and Thursdays between 10:00 AM and 2:00 PM EST."
    },
    {
        "id": "dep_2",
        "topic": "deployment",
        "question": "What is the error rate threshold that triggers an automated canary rollback?",
        "options": [">0.1%", ">0.5%", ">5.0%", ">10.0%"],
        "answer": ">0.5%",
        "explanation": "If error rates exceed 0.5% during canary rollout, automated rollback is triggered immediately."
    },

    # Architecture Standards
    {
        "id": "arch_1",
        "topic": "architecture",
        "question": "What programming language is standardized for high-throughput backend microservices?",
        "options": ["Go", "PHP", "Ruby", "C#"],
        "answer": "Go",
        "explanation": "Microservices are written in Go for performance, with ML pipelines in Python and UI in React."
    },
    {
        "id": "arch_2",
        "topic": "architecture",
        "question": "What database powers primary transactional persistence at Nexora?",
        "options": ["PostgreSQL 16", "MongoDB", "Cassandra", "Neo4j"],
        "answer": "PostgreSQL 16",
        "explanation": "Transactional persistence uses PostgreSQL 16 with read replicas and PgBouncer."
    },

    # Product Triage
    {
        "id": "prod_1",
        "topic": "product_triage",
        "question": "In Jira, Epics should be sized to complete within how many sprints?",
        "options": ["1 sprint (2 weeks)", "2 sprints (4 weeks)", "4 sprints (8 weeks)", "6 sprints (12 weeks)"],
        "answer": "2 sprints (4 weeks)",
        "explanation": "Epics must be scoped to complete within a maximum of 2 agile sprints (4 weeks)."
    },
    {
        "id": "prod_2",
        "topic": "product_triage",
        "question": "What framework is used for prioritizing feature backlog requests?",
        "options": ["RICE (Reach, Impact, Confidence, Effort)", "FIFO (First In First Out)", "MoSCoW only", "Random selection"],
        "answer": "RICE (Reach, Impact, Confidence, Effort)",
        "explanation": "Feature requests are ranked using the RICE scoring model."
    },

    # Sales Playbook
    {
        "id": "sales_1",
        "topic": "sales_playbook",
        "question": "Which qualification framework is standard for Nexora sales representatives?",
        "options": ["MEDDIC", "Cold Calling script", "BANT only", "SPIN only"],
        "answer": "MEDDIC",
        "explanation": "Sales reps qualify enterprise accounts using the MEDDIC sales qualification framework."
    },
    {
        "id": "sales_2",
        "topic": "sales_playbook",
        "question": "What approvals are required for enterprise contract discounts exceeding 20%?",
        "options": ["VP of Sales and CFO approval", "Account Executive approval", "No approval required", "Engineering Director approval"],
        "answer": "VP of Sales and CFO approval",
        "explanation": "Discounts above 20% require formal sign-off from both the VP of Sales and CFO."
    }
]

# Legacy alias for backward compatibility with existing tests
DIAGNOSTIC_QUESTIONS = [
    {"id": "q1", "topic": "company_basics", "question": "What are the core hours at Nexora?", "options": ["9 AM to 5 PM", "10 AM to 3 PM EST", "No core hours", "8 AM to 4 PM"], "answer": "10 AM to 3 PM EST"},
    {"id": "q2", "topic": "security", "question": "How often must you rotate your password?", "options": ["Every 30 days", "Every 60 days", "Every 90 days", "Never"], "answer": "Every 90 days"},
    {"id": "q3", "topic": "tools", "question": "What tool is used for async communication?", "options": ["Email", "Zoom", "Slack", "Jira"], "answer": "Slack"},
    {"id": "q4", "topic": "git_workflow", "question": "What development style does Nexora use?", "options": ["GitFlow", "Trunk-based development", "Feature branching", "Centralized"], "answer": "Trunk-based development"},
    {"id": "q5", "topic": "deployment", "question": "When do deployments happen?", "options": ["Mondays", "Tuesdays and Thursdays", "Fridays", "Everyday"], "answer": "Tuesdays and Thursdays"},
    {"id": "q6", "topic": "company_basics", "question": "What is the internet stipend?", "options": ["$50/month", "$100/month", "$25/month", "None"], "answer": "$50/month"},
    {"id": "q7", "topic": "security", "question": "How often is the phishing simulation?", "options": ["Monthly", "Quarterly", "Bi-Annually", "Yearly"], "answer": "Quarterly"},
    {"id": "q8", "topic": "product_triage", "question": "Epics should be sized under how many sprints?", "options": ["1 sprint", "2 sprints", "3 sprints", "4 sprints"], "answer": "2 sprints"},
    {"id": "q9", "topic": "git_workflow", "question": "How many approvals are required for a PR?", "options": ["0", "1", "2", "3"], "answer": "1"},
    {"id": "q10", "topic": "tools", "question": "Where should planned leave be requested?", "options": ["Slack", "Workday", "Jira", "Email"], "answer": "Workday"}
]

def normalize_text(text: str) -> str:
    """Normalize string for robust answer comparison (trim, lowercase, strip punctuation, normalize times)."""
    if not isinstance(text, str):
        return ""
    clean = text.lower().strip()
    clean = re.sub(r'^[a-d]\s*[\)\.\:\-]\s*', '', clean)  # Remove option prefix like "A) "
    clean = re.sub(r':00\b', '', clean)  # Normalize 10:00 AM -> 10 AM
    clean = re.sub(r'[^a-z0-9\$\% ]', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def is_answer_match(user_answer: str, correct_answer: str) -> bool:
    """Check if the user's answer matches the correct answer flexibly."""
    if not user_answer or not correct_answer:
        return False
    u = user_answer.strip()
    c = correct_answer.strip()
    if u == c or u.lower() == c.lower():
        return True
    
    # Normalized comparison
    nu = normalize_text(u)
    nc = normalize_text(c)
    if nu == nc:
        return True
    
    # Check if one is a substring of another when length is significant
    if len(nu) > 4 and len(nc) > 4 and (nu in nc or nc in nu):
        return True
        
    return False

def get_diagnostic_questions_for_role(role: str = "Software Engineer", count: int = 10):
    """
    Dynamically select and return diagnostic questions tailored to the role's topics.
    Ensures even distribution and varied questions across sessions.
    """
    role_topics = get_role_topics(role)
    topic_keys = list(role_topics.keys())
    
    # Group available questions by topic
    topic_map = {}
    for q in MASTER_DIAGNOSTIC_BANK:
        t = q["topic"]
        topic_map.setdefault(t, []).append(q)
        
    selected_questions = []
    
    # Ensure at least 1-2 questions from each role topic
    for t in topic_keys:
        pool = topic_map.get(t, [])
        if pool:
            # Pick a sample
            selected_questions.append(random.choice(pool))
            
    # Fill remaining count with other questions from role topics or general bank
    remaining_needed = count - len(selected_questions)
    if remaining_needed > 0:
        other_candidates = [
            q for q in MASTER_DIAGNOSTIC_BANK 
            if q not in selected_questions and q["topic"] in topic_keys
        ]
        if len(other_candidates) < remaining_needed:
            other_candidates = [q for q in MASTER_DIAGNOSTIC_BANK if q not in selected_questions]
            
        random.shuffle(other_candidates)
        selected_questions.extend(other_candidates[:remaining_needed])
        
    # Return formatted questions (stripping answer field for safe client delivery)
    safe_output = []
    for q in selected_questions[:count]:
        topic_info = TOPICS.get(q["topic"], {})
        safe_output.append({
            "id": q["id"],
            "topic": q["topic"],
            "topic_title": topic_info.get("title", q["topic"].replace("_", " ").title()),
            "question": q["question"],
            "options": q["options"]
        })
    return safe_output

def evaluate_diagnostic(answers: dict, role: str = "Software Engineer", question_list: list = None):
    """
    Thoroughly evaluate the diagnostic answers across all topics (including company_basics).
    Returns bypassed topics, detailed per-question marks, score breakdown, and calculated XP points.
    """
    # Build a lookup dictionary of all potential questions
    all_q_dict = {q["id"]: q for q in MASTER_DIAGNOSTIC_BANK}
    for q in DIAGNOSTIC_QUESTIONS:
        all_q_dict[q["id"]] = q
        
    role_topics = get_role_topics(role)
    
    topic_scores = {}
    topic_totals = {}
    evaluations = []
    correct_count = 0
    total_questions = len(answers) if answers else 0
    
    for q_id, user_ans in answers.items():
        q_obj = all_q_dict.get(q_id)
        if not q_obj:
            # Fallback search if id not found
            for item in MASTER_DIAGNOSTIC_BANK:
                if item["id"] == q_id:
                    q_obj = item
                    break
                    
        if not q_obj:
            continue
            
        topic = q_obj["topic"]
        correct_ans = q_obj["answer"]
        topic_totals[topic] = topic_totals.get(topic, 0) + 1
        
        is_correct = is_answer_match(user_ans, correct_ans)
        if is_correct:
            correct_count += 1
            topic_scores[topic] = topic_scores.get(topic, 0) + 1
            
        topic_title = TOPICS.get(topic, {}).get("title", topic.replace("_", " ").title())
        evaluations.append({
            "id": q_id,
            "topic": topic,
            "topic_title": topic_title,
            "question": q_obj["question"],
            "user_answer": user_ans,
            "correct_answer": correct_ans,
            "is_correct": is_correct,
            "explanation": q_obj.get("explanation", f"The correct policy answer is: {correct_ans}")
        })
        
    # Determine bypassed topics: topics where the user scored 100% or at least 80%
    bypassed_topics = []
    for topic, total in topic_totals.items():
        score = topic_scores.get(topic, 0)
        if total > 0 and (score / total) >= 0.8:
            bypassed_topics.append(topic)
            
    # Calculate XP marks: 10 XP per mark/correct answer + 50 XP completion bonus
    score_pct = int((correct_count / max(1, len(answers))) * 100) if answers else 0
    xp_to_award = (correct_count * 10) + 50
    
    return {
        "bypassed_topics": bypassed_topics,
        "correct_count": correct_count,
        "total_questions": len(answers),
        "score_percentage": score_pct,
        "xp_to_award": xp_to_award,
        "evaluations": evaluations
    }
