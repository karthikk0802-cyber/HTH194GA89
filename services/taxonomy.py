# Nexora demo company taxonomy — specific role cards for adaptive baseline.
# v1 code (roles.py, diagnostic.py, quiz_generator.py) never imports this.
# v2 sidecars read this; v1 behavior is unchanged.

DEPARTMENTS = {
    "Engineering - Core Platform": ["Frontend Engineer", "Backend Engineer", "ML Engineer"],
    "Engineering - Infrastructure": ["DevOps Engineer", "SRE"],
    "Product & Design": ["Product Manager", "Product Designer"],
    "Data & AI": ["Data Scientist"],
    "Sales": ["Account Executive"],
    "Marketing": ["Marketing Specialist"],
    "People & Culture": ["HR Manager"],
    "Customer Success": ["Support Engineer"],
    "IT & SecOps": ["IT Administrator"],
}

# depth meaning: Beginner=recall, Intermediate=apply, Expert=troubleshoot/tradeoffs
# baseline_count = general questions for that topic in Phase 1 baseline.
ROLE_CARDS = {
    "Frontend Engineer": {
        "department": "Engineering - Core Platform",
        "topics": {
            "company_basics": {"depth": "Beginner", "baseline_count": 2},
            "tools": {"depth": "Expert", "baseline_count": 4},
            "git_workflow": {"depth": "Expert", "baseline_count": 4},
            "architecture": {"depth": "Intermediate", "baseline_count": 3},
            "security": {"depth": "Intermediate", "baseline_count": 3},
        },
    },
    "Backend Engineer": {
        "department": "Engineering - Core Platform",
        "topics": {
            "company_basics": {"depth": "Beginner", "baseline_count": 2},
            "tools": {"depth": "Intermediate", "baseline_count": 2},
            "git_workflow": {"depth": "Expert", "baseline_count": 5},
            "architecture": {"depth": "Expert", "baseline_count": 5},
            "deployment": {"depth": "Intermediate", "baseline_count": 3},
            "security": {"depth": "Intermediate", "baseline_count": 3},
        },
    },
    "ML Engineer": {
        "department": "Engineering - Core Platform",
        "topics": {
            "company_basics": {"depth": "Beginner", "baseline_count": 2},
            "tools": {"depth": "Expert", "baseline_count": 4},
            "architecture": {"depth": "Expert", "baseline_count": 5},
            "security": {"depth": "Intermediate", "baseline_count": 3},
        },
    },
    "DevOps Engineer": {
        "department": "Engineering - Infrastructure",
        "topics": {
            "company_basics": {"depth": "Beginner", "baseline_count": 2},
            "tools": {"depth": "Intermediate", "baseline_count": 2},
            "git_workflow": {"depth": "Expert", "baseline_count": 4},
            "deployment": {"depth": "Expert", "baseline_count": 5},
            "architecture": {"depth": "Intermediate", "baseline_count": 3},
            "security": {"depth": "Intermediate", "baseline_count": 3},
        },
    },
    "SRE": {
        "department": "Engineering - Infrastructure",
        "topics": {
            "company_basics": {"depth": "Beginner", "baseline_count": 2},
            "deployment": {"depth": "Expert", "baseline_count": 5},
            "security": {"depth": "Intermediate", "baseline_count": 3},
            "tools": {"depth": "Intermediate", "baseline_count": 2},
        },
    },
    "Product Manager": {
        "department": "Product & Design",
        "topics": {
            "company_basics": {"depth": "Expert", "baseline_count": 4},
            "tools": {"depth": "Intermediate", "baseline_count": 3},
            "product_triage": {"depth": "Expert", "baseline_count": 5},
        },
    },
    "Product Designer": {
        "department": "Product & Design",
        "topics": {
            "company_basics": {"depth": "Intermediate", "baseline_count": 3},
            "tools": {"depth": "Intermediate", "baseline_count": 3},
            "product_triage": {"depth": "Beginner", "baseline_count": 2},
        },
    },
    "Data Scientist": {
        "department": "Data & AI",
        "topics": {
            "company_basics": {"depth": "Beginner", "baseline_count": 2},
            "tools": {"depth": "Expert", "baseline_count": 4},
            "architecture": {"depth": "Expert", "baseline_count": 4},
            "security": {"depth": "Intermediate", "baseline_count": 3},
        },
    },
    "Account Executive": {
        "department": "Sales",
        "topics": {
            "company_basics": {"depth": "Intermediate", "baseline_count": 4},
            "tools": {"depth": "Beginner", "baseline_count": 2},
            "sales_playbook": {"depth": "Expert", "baseline_count": 6},
        },
    },
    "Marketing Specialist": {
        "department": "Marketing",
        "topics": {
            "company_basics": {"depth": "Intermediate", "baseline_count": 3},
            "tools": {"depth": "Intermediate", "baseline_count": 3},
            "sales_playbook": {"depth": "Beginner", "baseline_count": 2},
        },
    },
    "HR Manager": {
        "department": "People & Culture",
        "topics": {
            "company_basics": {"depth": "Expert", "baseline_count": 5},
            "tools": {"depth": "Intermediate", "baseline_count": 3},
        },
    },
    "Support Engineer": {
        "department": "Customer Success",
        "topics": {
            "company_basics": {"depth": "Expert", "baseline_count": 4},
            "tools": {"depth": "Expert", "baseline_count": 4},
            "product_triage": {"depth": "Intermediate", "baseline_count": 3},
        },
    },
    "IT Administrator": {
        "department": "IT & SecOps",
        "topics": {
            "company_basics": {"depth": "Intermediate", "baseline_count": 2},
            "tools": {"depth": "Expert", "baseline_count": 3},
            "security": {"depth": "Expert", "baseline_count": 4},
        },
    },
    # Legacy aliases so v2 also works with old generic titles.
    "Software Engineer": {
        "department": "Engineering - Core Platform",
        "topics": {
            "company_basics": {"depth": "Beginner", "baseline_count": 2},
            "tools": {"depth": "Intermediate", "baseline_count": 2},
            "git_workflow": {"depth": "Expert", "baseline_count": 4},
            "architecture": {"depth": "Intermediate", "baseline_count": 3},
            "security": {"depth": "Intermediate", "baseline_count": 3},
        },
    },
    "Sales Representative": {
        "department": "Sales",
        "topics": {
            "company_basics": {"depth": "Intermediate", "baseline_count": 4},
            "tools": {"depth": "Beginner", "baseline_count": 2},
            "sales_playbook": {"depth": "Expert", "baseline_count": 6},
        },
    },
}


def get_role_card(role: str):
    """Return the role card for a role, falling back to a generic card."""
    if role in ROLE_CARDS:
        return ROLE_CARDS[role]
    return {
        "department": "General",
        "topics": {
            "company_basics": {"depth": "Beginner", "baseline_count": 2},
            "security": {"depth": "Beginner", "baseline_count": 2},
            "tools": {"depth": "Beginner", "baseline_count": 2},
        },
    }


# Compliance topics can never be bypassed: everyone completes the full
# baseline for them regardless of score. Lucky guesses must not certify
# safety training.
NON_BYPASSABLE_TOPICS = frozenset({"security"})


def apply_bypass_policy(bypassed_topics) -> list:
    """Filter claimed bypasses through the compliance policy. Shape-preserving."""
    return [t for t in (bypassed_topics or []) if t not in NON_BYPASSABLE_TOPICS]


# Doc title -> topics whose mastery expires when the doc is re-approved.
# Scores built on old SOP versions must not survive a rewrite.
DOC_TOPIC_OVERRIDES = {
    "employee_handbook": "company_basics",
    "leave_policy": "company_basics",
    "expense_policy": "company_basics",
    "remote_work": "company_basics",
    "code_review": "git_workflow",
    "jira_triage": "git_workflow",
    "data_privacy": "security",
    "incident_response": "deployment",
    "on_call": "deployment",
    "communication_guidelines": "tools",
    "environment_setup": "tools",
}


def doc_topics_for_title(title: str) -> list:
    """Map a doc title to affected topic keys (stable, no LLM)."""
    t = (title or "").lower().replace(" & ", "_").replace(" ", "_").replace("-", "_")
    for prefix, topic in DOC_TOPIC_OVERRIDES.items():
        if prefix in t:
            return [topic]
    for key in ("company_basics", "security", "tools", "git_workflow",
                "architecture", "product_triage", "deployment", "sales_playbook"):
        if key in t or t.replace("_", "") in key.replace("_", ""):
            return [key]
    if "deploy" in t:
        return ["deployment"]
    if "architecture" in t:
        return ["architecture"]
    if "sales" in t:
        return ["sales_playbook"]
    if "product" in t:
        return ["product_triage"]
    return []
