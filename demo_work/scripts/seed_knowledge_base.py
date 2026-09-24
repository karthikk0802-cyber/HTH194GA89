import os
import datetime

KNOWLEDGE_BASE_DIR = "knowledge_base"

if not os.path.exists(KNOWLEDGE_BASE_DIR):
    os.makedirs(KNOWLEDGE_BASE_DIR)

documents = [
    {"title": "Employee Handbook v1.0", "role": "all", "content": "Welcome to Nexora. Core hours are 10 AM to 3 PM EST. Unlimited PTO policy..."},
    {"title": "Security Policy v2.1", "role": "all", "content": "Always lock your workstation. Password rotation every 90 days. Phishing simulation quarterly..."},
    {"title": "Git Workflow v1.2", "role": "engineering", "content": "We use trunk-based development. All commits must be signed. PRs require 1 approval."},
    {"title": "Code Review Guidelines", "role": "engineering", "content": "Review for clarity, security, and performance. No nitpicking; use automated formatters."},
    {"title": "Jira Triage Process", "role": "product,engineering", "content": "Bugs must have reproduction steps. Epics should be sized under 2 sprints."},
    {"title": "Environment Setup", "role": "engineering", "content": "Use Docker for local dev. Production access requires VPN and MFA."},
    {"title": "Deployment SOP", "role": "devops,engineering", "content": "Deployments happen Tuesdays and Thursdays. No Friday deployments without VP approval."},
    {"title": "Incident Response Plan", "role": "all", "content": "Sev1 incidents require paging the on-call engineer via PagerDuty. Communication happens in #incidents channel."},
    {"title": "Communication Guidelines", "role": "all", "content": "Use Slack for async communication. Email for external clients. Zoom for sync meetings."},
    {"title": "Leave Policy", "role": "all", "content": "Request leave in Workday at least 2 weeks in advance for planned vacations."},
    {"title": "Expense Policy v3.0", "role": "all", "content": "Per diem is $75 for travel. All expenses over $25 require a receipt submitted via Expensify."},
    {"title": "Remote Work Policy", "role": "all", "content": "Nexora is remote-first. Ergonomic equipment stipend is $500. Internet stipend is $50/month."},
    {"title": "On-Call Compensation", "role": "engineering", "content": "Engineers get an extra $500 per on-call week."},
    {"title": "Architecture Standards", "role": "engineering", "content": "Microservices in Go, frontend in React, ML services in Python. GraphQL for API gateway."},
    {"title": "Data Privacy & GDPR", "role": "all", "content": "Never log PII. User data must be anonymized before entering analytics pipelines."}
]

for i, doc in enumerate(documents):
    filename = doc["title"].replace(" ", "_").replace("&", "and") + ".txt"
    filepath = os.path.join(KNOWLEDGE_BASE_DIR, filename)
    with open(filepath, "w") as f:
        f.write(f"Title: {doc['title']}\n")
        f.write(f"Role: {doc['role']}\n")
        f.write(f"Date: {datetime.date.today().isoformat()}\n")
        f.write("-" * 40 + "\n\n")
        f.write(doc["content"] + "\n")

print(f"Successfully generated {len(documents)} synthetic Nexora knowledge base documents in '{KNOWLEDGE_BASE_DIR}'")
