import networkx as nx
from datetime import datetime, timedelta
from services.roles import TOPICS

# Intervals for spaced repetition (days)
SPACED_INTERVALS = [1, 3, 7, 14, 30]

def build_competency_graph():
    """Build a NetworkX DiGraph representing topic prerequisites."""
    G = nx.DiGraph()
    for topic_id, data in TOPICS.items():
        G.add_node(topic_id, title=data["title"])
        for req in data["prerequisites"]:
            G.add_edge(req, topic_id)
    return G

def update_topic_state(state, is_correct):
    """Deterministically update mastery score, difficulty, and spaced review schedules."""
    now = datetime.utcnow()
    state.last_attempt_at = now
    
    if is_correct:
        # Increase mastery
        increment = 20 if state.difficulty == "Beginner" else 10 if state.difficulty == "Intermediate" else 5
        state.mastery_score = min(100, state.mastery_score + increment)
        
        # Difficulty adaptation
        if state.mastery_score >= 80:
            state.difficulty = "Expert"
            state.status = "Completed"
        elif state.mastery_score >= 50:
            state.difficulty = "Intermediate"
            state.status = "Current"
            
        # Spaced repetition scheduling
        if state.status == "Completed":
            # Schedule next review
            state.next_review_at = now + timedelta(days=state.review_interval_days)
            # Advance interval for next time
            idx = SPACED_INTERVALS.index(state.review_interval_days) if state.review_interval_days in SPACED_INTERVALS else 0
            state.review_interval_days = SPACED_INTERVALS[min(len(SPACED_INTERVALS)-1, idx+1)]
            
    else:
        # Decrease mastery
        decrement = 15
        state.mastery_score = max(0, state.mastery_score - decrement)
        
        # Drop difficulty if struggling
        if state.mastery_score < 40:
            state.difficulty = "Beginner"
        elif state.mastery_score < 70:
            state.difficulty = "Intermediate"
            
        # If they fail a review, reactivate the topic and reset interval
        if state.status == "Needs-Review":
            state.status = "Current"
            state.review_interval_days = 1
            state.next_review_at = None

    return state

def rank_next_topics(user_states, required_topics):
    """Rank topics based on prerequisites met, review needs, and priorities."""
    G = build_competency_graph()
    state_map = {s.topic_id: s for s in user_states}
    
    ranked = []
    
    for topic_id in required_topics:
        state = state_map.get(topic_id)
        status = state.status if state else "Locked"
        
        # 1. Review due takes highest priority
        if state and state.next_review_at and state.next_review_at <= datetime.utcnow():
            ranked.append({"topic_id": topic_id, "score": 100, "reason": "Spaced repetition review due today.", "status": "Needs-Review"})
            continue
            
        if status in ["Completed", "Needs-Review"]:
            continue
            
        # Check prerequisites
        prereqs = list(G.predecessors(topic_id))
        prereqs_met = all(state_map.get(p) and state_map[p].status in ["Completed", "Needs-Review"] for p in prereqs)
        
        if prereqs_met:
            # 2. Topics currently in progress
            if status == "Current":
                ranked.append({"topic_id": topic_id, "score": 80, "reason": "Continue mastering this current topic.", "status": status})
            # 3. New topics unlocked
            else:
                ranked.append({"topic_id": topic_id, "score": 50, "reason": "You've unlocked this by completing prerequisites.", "status": "Recommended"})
                
    # Sort by score descending
    return sorted(ranked, key=lambda x: x["score"], reverse=True)
