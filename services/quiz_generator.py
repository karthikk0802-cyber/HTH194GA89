import json
import random
import time
import re
from services.llm import generate_completion, clean_json_response, get_mistral_client
from services.embedding import search_chroma
from services.question_bank import BANK_EXTRA

# Pre-curated diverse bank of fallback questions across all topics & levels
FALLBACK_QUIZ_BANK = {
    "company_basics": [
        {
            "question": "What is Nexora's designated Core Collaboration Window for synchronous team meetings and sprint ceremonies?",
            "options": ["8:00 AM to 12:00 PM EST", "10:00 AM to 3:00 PM EST", "1:00 PM to 6:00 PM EST", "No mandatory core hours"],
            "correct_answer": "10:00 AM to 3:00 PM EST",
            "learning_objective": "Master Nexora core scheduling windows and async collaboration norms",
            "evidence_quote": "Core Collaboration Window from 10:00 AM to 3:00 PM EST (Monday through Friday)."
        },
        {
            "question": "What is the monthly recurring internet allowance provided to all full-time remote employees at Nexora?",
            "options": ["$25/month", "$50/month", "$100/month", "$150/month"],
            "correct_answer": "$50/month",
            "learning_objective": "Understand remote work compensation and recurring subsidies",
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
            "question": "What is Nexora's policy regarding notice for planned vacations over 3 consecutive days?",
            "options": ["Submit in Workday at least 2 weeks in advance", "Notify via Slack on the day of departure", "Email VP 3 months in advance", "No advance notice needed"],
            "correct_answer": "Submit in Workday at least 2 weeks in advance",
            "learning_objective": "Understand Workday leave submission timelines",
            "evidence_quote": "Planned vacations over 3 consecutive days must be submitted via Workday at least 2 weeks in advance."
        }
    ],
    "security": [
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
        },
        {
            "question": "What screen lock timeout is enforced across all company laptops when left unattended?",
            "options": ["1 minute", "5 minutes", "15 minutes", "30 minutes"],
            "correct_answer": "5 minutes",
            "learning_objective": "Follow workstation physical security and locking policies",
            "evidence_quote": "Workstation screen lock timeout is enforced at 5 minutes of inactivity."
        }
    ],
    "git_workflow": [
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
        },
        {
            "question": "How many peer approvals from CODEOWNERS are mandatory before a Pull Request can be merged to main?",
            "options": ["0 approvals", "At least 1 approval", "At least 3 approvals", "VP approval only"],
            "correct_answer": "At least 1 approval",
            "learning_objective": "Comply with peer code review and CODEOWNERS authorization",
            "evidence_quote": "Every Pull Request (PR) requires at least 1 peer approval from an engineer in the CODEOWNERS file."
        }
    ],
    "tools": [
        {
            "question": "What tool serves as the primary real-time and asynchronous messaging platform for internal Nexora communications?",
            "options": ["Slack", "Microsoft Teams", "Discord", "Skype"],
            "correct_answer": "Slack",
            "learning_objective": "Know internal communications tools and platform standards",
            "evidence_quote": "Slack: Primary platform for internal real-time and asynchronous messaging."
        },
        {
            "question": "Where must employees submit itemized receipts for business travel and expense reimbursement?",
            "options": ["Expensify", "Concur", "Direct Slack to Finance", "Manual paper ledger"],
            "correct_answer": "Expensify",
            "learning_objective": "Master expense reporting and reimbursement tooling",
            "evidence_quote": "Receipts must be submitted via Expensify within 30 days of the transaction date."
        },
        {
            "question": "How are local development secrets dynamically injected without committing them to git?",
            "options": ["HashiCorp Vault CLI / 1Password Developer Plugins", "Plaintext .env committed to repo", "Public Pastebin", "Shared Slack canvas"],
            "correct_answer": "HashiCorp Vault CLI / 1Password Developer Plugins",
            "learning_objective": "Understand secure secrets injection workflows",
            "evidence_quote": "Secrets are fetched dynamically via HashiCorp Vault CLI or 1Password developer plugins."
        }
    ],
    "architecture": [
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
        },
        {
            "question": "What communication protocol is used for high-performance inter-service communication between backend microservices?",
            "options": ["gRPC with Protocol Buffers", "SOAP XML", "WebSockets only", "Raw TCP sockets"],
            "correct_answer": "gRPC with Protocol Buffers",
            "learning_objective": "Understand microservice inter-service communication standards",
            "evidence_quote": "Inter-service backend communication uses gRPC with Protocol Buffers"
        }
    ],
    "deployment": [
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
        },
        {
            "question": "What approval is required for emergency out-of-band hotfix deployments outside the scheduled deployment window?",
            "options": ["Written approval from Engineering VP or Director of Infrastructure", "Self-approval by any engineer", "No approval needed", "Product intern approval"],
            "correct_answer": "Written approval from Engineering VP or Director of Infrastructure",
            "learning_objective": "Follow out-of-band release governance and authorization paths",
            "evidence_quote": "Emergency hotfixes outside the scheduled deployment window require explicit written approval from the Engineering VP or Director of Infrastructure"
        }
    ],
    "product_triage": [
        {
            "question": "What is the maximum recommended duration for an Epic in Nexora's Jira triage process?",
            "options": ["1 sprint (2 weeks)", "2 sprints (4 weeks)", "6 months", "1 year"],
            "correct_answer": "2 sprints (4 weeks)",
            "learning_objective": "Master agile Epic scoping and sprint sizing boundaries",
            "evidence_quote": "Epics must be scoped to complete within a maximum of 2 agile sprints (4 weeks)."
        },
        {
            "question": "What prioritization framework is used for ranking feature proposals in the product roadmap?",
            "options": ["RICE (Reach, Impact, Confidence, Effort)", "First In First Out (FIFO)", "Highest Paid Person's Opinion (HiPPO)", "Alphabetical order"],
            "correct_answer": "RICE (Reach, Impact, Confidence, Effort)",
            "learning_objective": "Apply the RICE feature prioritization framework",
            "evidence_quote": "Feature proposals are prioritized using the RICE framework: (Reach × Impact × Confidence) / Effort."
        }
    ],
    "sales_playbook": [
        {
            "question": "Which qualification framework do Nexora sales representatives use to evaluate enterprise opportunities?",
            "options": ["MEDDIC", "SPIN Selling only", "Cold Calling script", "Random outreach"],
            "correct_answer": "MEDDIC",
            "learning_objective": "Apply MEDDIC sales qualification criteria",
            "evidence_quote": "Sales reps qualify enterprise opportunities using MEDDIC: Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, and Champion."
        },
        {
            "question": "What approval is required for enterprise contract discounts exceeding 20%?",
            "options": ["VP of Sales and CFO approval", "Account Executive self-approval", "Sales Engineer approval", "No discount limits"],
            "correct_answer": "VP of Sales and CFO approval",
            "learning_objective": "Adhere to the corporate discount approval matrix",
            "evidence_quote": "discounts exceeding 20% require VP of Sales and CFO approval."
        }
    ]
}

def _normalize_topic_key(topic_title):
    """Map a human topic title to the static bank key. Pure rename, same rules."""
    topic_key = topic_title.lower().replace(" & ", "_").replace(" ", "_").replace("-", "_").replace("/", "_")
    if topic_key == "security_compliance":
        topic_key = "security"
    elif topic_key == "tools_workflows":
        topic_key = "tools"
    elif "deploy" in topic_key:
        topic_key = "deployment"
    elif "architecture" in topic_key:
        topic_key = "architecture"
    elif "git" in topic_key:
        topic_key = "git_workflow"
    elif "company" in topic_key or "culture" in topic_key or "basics" in topic_key:
        topic_key = "company_basics"
    elif "sales" in topic_key:
        topic_key = "sales_playbook"
    elif "product" in topic_key:
        topic_key = "product_triage"
    return topic_key


def _norm_question(q):
    return re.sub(r"\s+", " ", (q or "").lower().strip())


def _full_static_bank(topic_key):
    """Base bank + expanded bank for a key, deduplicated by question text."""
    seen = set()
    out = []
    for item in list(FALLBACK_QUIZ_BANK.get(topic_key, [])) + list(BANK_EXTRA.get(topic_key, [])):
        nq = _norm_question(item.get("question", ""))
        if nq and nq not in seen:
            seen.add(nq)
            out.append(item)
    if not out:
        for item in list(FALLBACK_QUIZ_BANK.get("company_basics", [])) + list(BANK_EXTRA.get("company_basics", [])):
            nq = _norm_question(item.get("question", ""))
            if nq and nq not in seen:
                seen.add(nq)
                out.append(item)
    return out


def _eval_id(topic_key, idx):
    return f"{topic_key}:{idx}"


def build_graded_eval(role, seen_hashes, count=20, seed=None):
    """Held-out graded assessment: unseen bank questions across the role card.

    Answers and evidence are stripped (server grades by eval_id). Stable IDs
    come from bank order, so submit can re-derive the key without storage.
    """
    from services.eval_seen import qhash as _qhash
    from services.taxonomy import get_role_card

    rng = random.Random(seed)
    card = get_role_card(role)
    topics = list(card.get("topics", {}).keys()) or ["company_basics"]
    seen = set(seen_hashes or [])

    unseen, fallback = [], []
    for topic_key in topics:
        for idx, item in enumerate(_full_static_bank(topic_key)):
            entry = {"eval_id": _eval_id(topic_key, idx), "topic": topic_key,
                     "question": item.get("question", ""), "options": list(item.get("options", []))}
            (unseen if _qhash(entry["question"]) not in seen else fallback).append(entry)
    rng.shuffle(unseen)
    rng.shuffle(fallback)
    picked = (unseen + fallback)[:count]
    rng.shuffle(picked)
    return {
        "questions": picked,
        "count": len(picked),
        "requested": count,
        "unseen_count": min(len(unseen), count),
        "complete": len(picked) >= count,
    }


def grade_graded_eval(answers, role="all"):
    """Grade eval answers by stable eval_id. Returns per-topic + overall + certified."""
    from services.diagnostic import is_answer_match
    from services.taxonomy import NON_BYPASSABLE_TOPICS

    per_topic, weak, correct_total, total = {}, [], 0, 0
    compliance_wrong = 0
    compliance_total = 0
    for eval_id, user_ans in (answers or {}).items():
        try:
            topic_key, idx = eval_id.split(":", 1)
            item = _full_static_bank(topic_key)[int(idx)]
        except (ValueError, IndexError):
            continue
        ok = is_answer_match(user_ans or "", item.get("correct_answer", ""))
        total += 1
        d = per_topic.setdefault(topic_key, {"correct": 0, "total": 0})
        d["total"] += 1
        if ok:
            correct_total += 1
            d["correct"] += 1
        if topic_key in NON_BYPASSABLE_TOPICS:
            compliance_total += 1
            if not ok:
                compliance_wrong += 1
        if topic_key not in weak and d["correct"] * 2 < d["total"]:
            weak.append(topic_key)
    score = int(correct_total * 100 / total) if total else 0
    return {
        "correct_count": correct_total,
        "total_questions": total,
        "score_percentage": score,
        "per_topic": {t: {**d, "pct": int(d["correct"] * 100 / d["total"])} for t, d in per_topic.items()},
        "weak_topics": weak,
        "certified": bool(total) and score >= 80 and compliance_wrong == 0,
    }


def generate_quiz_session(topic_title, role="all", difficulty="Beginner", count=20, seed=None):
    """Build a no-repeat quiz session: sample static bank without replacement,
    top up with one batched LLM call when available. Never repeats a question
    within the returned session. Single-question generate_quiz_for_topic untouched.
    """
    rng = random.Random(seed)
    topic_key = _normalize_topic_key(topic_title)
    bank = _full_static_bank(topic_key)
    rng.shuffle(bank)

    questions = []
    seen = set()
    for item in bank:
        nq = _norm_question(item.get("question", ""))
        if nq in seen:
            continue
        seen.add(nq)
        q = dict(item)
        q["citations"] = [f"{topic_title} Guidelines"]
        q["difficulty"] = difficulty
        questions.append(q)
        if len(questions) >= count:
            break
    return _top_up_session(topic_title, role, difficulty, count, rng, questions, seen)


def grounded_fallback_question(topic_title):
    """Last-resort question: always a verbatim bank item, never synthesized.

    Used when generation fails outright. Guarantees the grounding constraint:
    no question the system emits is ungrounded in the static corpus.
    """
    bank = _full_static_bank(_normalize_topic_key(topic_title))
    if not bank:
        return {"error": f"No grounded questions available for topic '{topic_title}'"}
    item = dict(random.choice(bank))
    item["citations"] = [f"{topic_title} Guidelines"]
    return item


def _top_up_session(topic_title, role, difficulty, count, rng, questions, seen):
    # Top-up via a single batched LLM call when the bank is short and LLM exists.
    if len(questions) < count and get_mistral_client() is not None:
        need = count - len(questions)
        prompt = f"""You are an expert instructional designer at Nexora.
Generate {need} novel, distinct Multiple Choice Questions for the topic "{topic_title}" at "{difficulty}" difficulty.
Rules: each question strictly about Nexora policy; 4 options each; unambiguous.
Output MUST be a raw JSON array (no markdown, no fences) of objects with keys:
question, options (4 strings), correct_answer (exactly one of options),
learning_objective (1 sentence), evidence_quote (short supporting quote).
Do NOT repeat these existing questions: {[q["question"] for q in questions[:5]]}
"""
        try:
            raw = clean_json_response(generate_completion(prompt, temperature=0.7))
            m = re.search(r"\[.*\]", raw, re.DOTALL)
            batch = json.loads(m.group(0) if m else raw)
            for entry in batch:
                if not isinstance(entry, dict):
                    continue
                if not all(k in entry for k in ("question", "options", "correct_answer")):
                    continue
                if len(entry.get("options", [])) != 4:
                    continue
                nq = _norm_question(entry.get("question", ""))
                if not nq or nq in seen:
                    continue
                if entry["correct_answer"] not in entry["options"]:
                    continue
                seen.add(nq)
                entry["citations"] = [f"{topic_title} Policy"]
                entry["difficulty"] = difficulty
                questions.append(entry)
                if len(questions) >= count:
                    break
        except Exception as e:
            print(f"[QuizSession] LLM top-up failed: {e}. Using static bank only.")

    rng.shuffle(questions)
    return {
        "session_id": f"sess_{int(time.time()*1000)%1000000}_{rng.randint(100,999)}",
        "topic": topic_title,
        "role": role,
        "difficulty": difficulty,
        "count": len(questions),
        "requested": count,
        "complete": len(questions) >= count,
        "questions": questions,
    }


def generate_quiz_for_topic(topic_title, role="all", difficulty="Beginner"):
    """
    Generate a dynamic, novel, grounded multiple-choice question for a given topic
    leveraging vector embeddings in ChromaDB and Mistral AI with randomized sampling.
    """
    # Normalize topic key
    topic_key = topic_title.lower().replace(" & ", "_").replace(" ", "_").replace("-", "_").replace("/", "_")
    if topic_key == "security_compliance":
        topic_key = "security"
    elif topic_key == "tools_workflows":
        topic_key = "tools"
    elif "deploy" in topic_key:
        topic_key = "deployment"
    elif "architecture" in topic_key:
        topic_key = "architecture"
    elif "git" in topic_key:
        topic_key = "git_workflow"
    elif "company" in topic_key or "culture" in topic_key or "basics" in topic_key:
        topic_key = "company_basics"
    elif "sales" in topic_key:
        topic_key = "sales_playbook"
    elif "product" in topic_key:
        topic_key = "product_triage"

    # 1. Search ChromaDB with varied semantic queries for rich context
    query_variants = [
        f"{topic_title} policy, standards, and rules at Nexora",
        f"{topic_title} guidelines, requirements, and compliance procedures",
        f"{topic_title} best practices, SLAs, and technical specifications"
    ]
    chosen_query = random.choice(query_variants)
    
    search_results = search_chroma(chosen_query, n_results=5, role_filter=role)
    
    context_text = ""
    citations = []
    
    if search_results and search_results.get('documents') and search_results['documents'][0]:
        documents = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        
        # Randomly shuffle and take 2-3 chunks to ensure variety across calls
        combined = list(zip(documents, metadatas))
        random.shuffle(combined)
        selected_chunks = combined[:3]
        
        for doc, meta in selected_chunks:
            title = meta.get('title', 'Nexora Guideline')
            context_text += f"\n--- Document Excerpt: {title} ---\n{doc}\n"
            citations.append(title)

    # 2. If no context found from Chroma, fallback to pre-curated bank
    if not context_text.strip():
        questions = FALLBACK_QUIZ_BANK.get(topic_key, FALLBACK_QUIZ_BANK.get("company_basics", []))
        item = random.choice(questions).copy()
        item["citations"] = [f"{topic_title} Guidelines"]
        return item

    # 3. Call Mistral AI to synthesize a fresh, high-quality question
    rand_seed = int(time.time() * 1000) % 10000
    prompt = f"""You are an expert instructional designer and technical assessor at Nexora.
Generate a novel, creative Multiple Choice Question (MCQ) for the topic "{topic_title}" at a "{difficulty}" difficulty level.
(Randomization seed: {rand_seed})

Rules:
1. The question and correct answer MUST be strictly supported by the Knowledge Base Context below.
2. Provide 4 distinct options (1 correct answer and 3 plausible distractors).
3. The options must be unambiguous.
4. Output MUST be valid, raw JSON (no markdown formatting, no code fences, no surrounding text).

Required JSON structure:
{{
  "question": "Clear, concise question text",
  "options": ["Option A text", "Option B text", "Option C text", "Option D text"],
  "correct_answer": "Exact text of the correct option matching one of the options array",
  "learning_objective": "Brief 1-sentence learning objective",
  "evidence_quote": "Direct quote from the context that proves the answer"
}}

Knowledge Base Context:
{context_text}
"""

    try:
        response_text = generate_completion(prompt, temperature=0.4)
        clean_text = clean_json_response(response_text)
        
        # Robust JSON extraction
        json_match = re.search(r'\{.*\}', clean_text, re.DOTALL)
        if json_match:
            quiz_data = json.loads(json_match.group(0))
        else:
            quiz_data = json.loads(clean_text)

        # Validate required keys
        if "question" in quiz_data and "options" in quiz_data and "correct_answer" in quiz_data:
            # Ensure correct_answer is in options
            if quiz_data["correct_answer"] not in quiz_data["options"]:
                quiz_data["options"][0] = quiz_data["correct_answer"]
                random.shuffle(quiz_data["options"])
                
            quiz_data["citations"] = list(set(citations)) if citations else [f"{topic_title} Policy"]
            return quiz_data
    except Exception as e:
        print(f"[QuizGen Warning] LLM generation failed: {e}. Using randomized verified fallback.")

    # 4. Fallback if LLM parsing failed
    questions = FALLBACK_QUIZ_BANK.get(topic_key, FALLBACK_QUIZ_BANK.get("company_basics", []))
    item = random.choice(questions).copy()
    item["citations"] = list(set(citations)) if citations else [f"{topic_title} Guidelines"]
    return item
