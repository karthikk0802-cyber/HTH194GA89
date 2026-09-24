# Curated static catalog of verified resources to prevent hallucination (RES-01)
CURATED_RESOURCES = {
    "company_basics": [
        {"title": "Welcome to Nexora Video", "type": "Video", "url": "https://intranet.nexora.local/video/welcome"},
        {"title": "Benefits Overview PDF", "type": "Document", "url": "https://intranet.nexora.local/docs/benefits"}
    ],
    "security": [
        {"title": "OWASP Top 10 Summary", "type": "SOP", "url": "https://intranet.nexora.local/sec/owasp"},
        {"title": "Incident Reporting Portal", "type": "Tool", "url": "https://security.nexora.local/report"}
    ],
    "git_workflow": [
        {"title": "Trunk-Based Development Guide", "type": "Document", "url": "https://intranet.nexora.local/eng/trunk"},
        {"title": "How to write good commit messages", "type": "Video", "url": "https://intranet.nexora.local/video/commits"}
    ],
    "tools": [
        {"title": "Slack Etiquette Guide", "type": "SOP", "url": "https://intranet.nexora.local/docs/slack"},
        {"title": "Jira Quickstart", "type": "Video", "url": "https://intranet.nexora.local/video/jira"}
    ]
}

def get_resources_for_topic(topic_id):
    """Return verified resources for a topic."""
    return CURATED_RESOURCES.get(topic_id, [])
