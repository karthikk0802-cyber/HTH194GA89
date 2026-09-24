# Voice tutor backend: text in, grounded answer out.
# Audio itself is free browser-side (Web Speech API mic + speechSynthesis);
# this side only needs to be intelligent, so modes route into the RAG brain
# instead of echoing the transcript back.

MODE_PREFIX = {
    "explain": "",
    "quiz-me": "Key idea first, then a self-check question for the learner. ",
    "explain-mistake": "Correct the likely misconception directly, then restate the rule. ",
    "give-example": "Lead with a concrete Nexora example, then the general rule. ",
    "what-next": "Answer briefly, then name the single most useful follow-up topic. ",
}


def handle_voice_interaction(voice_transcript, mode):
    """Answer a spoken (transcribed) question with RAG grounding."""
    if not voice_transcript or not voice_transcript.strip():
        return "Audio input not detected or STT unavailable. Type your question instead."
    try:
        from services.rag import generate_rag_response
        res = generate_rag_response(voice_transcript.strip(), role="all")
        answer = (res.get("answer") or "").strip()
        if not answer or "insufficient information" in answer.lower():
            return "I couldn't find that in Nexora policy documents. Try asking about core hours, security, Git workflow, deployments, or expenses."
        return MODE_PREFIX.get(mode or "explain", "") + answer
    except Exception:
        return "Voice tutor is temporarily unavailable. Type your question into the Knowledge Coach instead."
