# Role Definitions and Topics
ROLES = [
    "Software Engineer",
    "Product Manager",
    "DevOps Engineer",
    "Sales Representative",
    "Marketing Specialist",
    "HR Manager",
    "Data Scientist",
    "Customer Support"
]

# A basic topic catalog
TOPICS = {
    "company_basics": {"title": "Company Basics", "prerequisites": []},
    "security": {"title": "Security & Compliance", "prerequisites": ["company_basics"]},
    "tools": {"title": "Tools & Workflows", "prerequisites": ["company_basics"]},
    "git_workflow": {"title": "Git Workflow", "prerequisites": ["tools"]},
    "architecture": {"title": "Architecture Standards", "prerequisites": ["git_workflow"]},
    "product_triage": {"title": "Product Triage", "prerequisites": ["tools"]},
    "deployment": {"title": "Deployment & CI/CD", "prerequisites": ["git_workflow"]},
    "sales_playbook": {"title": "Sales Playbook", "prerequisites": ["company_basics"]},
}

def get_role_topics(role):
    """Return required topics for a role."""
    base_topics = ["company_basics", "security", "tools"]
    
    if role == "Software Engineer":
        base_topics.extend(["git_workflow", "architecture"])
    elif role == "DevOps Engineer":
        base_topics.extend(["git_workflow", "deployment", "architecture"])
    elif role == "Product Manager":
        base_topics.extend(["product_triage"])
    elif role == "Sales Representative":
        base_topics.extend(["sales_playbook"])
        
    return {topic: TOPICS[topic] for topic in base_topics}
