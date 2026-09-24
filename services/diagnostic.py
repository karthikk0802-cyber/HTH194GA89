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

def evaluate_diagnostic(answers):
    """
    Evaluate the diagnostic and return topics that can be bypassed (skipped).
    Threshold for skipping a topic: 100% correct in that topic's questions.
    """
    topic_scores = {}
    topic_totals = {}
    
    for q in DIAGNOSTIC_QUESTIONS:
        topic = q["topic"]
        topic_totals[topic] = topic_totals.get(topic, 0) + 1
        
        if q["id"] in answers and answers[q["id"]] == q["answer"]:
            topic_scores[topic] = topic_scores.get(topic, 0) + 1
            
    bypassed_topics = []
    for topic, total in topic_totals.items():
        if topic_scores.get(topic, 0) == total:
            bypassed_topics.append(topic)
            
    return bypassed_topics
