import json
from services.llm import generate_completion
from services.embedding import search_chroma

def generate_quiz_for_topic(topic_title, role="all", difficulty="Beginner"):
    """Generate a single grounded quiz question for a given topic."""
    
    # 1. Retrieve evidence
    search_results = search_chroma(f"{topic_title} guidelines and policies", n_results=3, role_filter=role)
    
    if not search_results or not search_results['documents'] or not search_results['documents'][0]:
        return {"error": "INSUFFICIENT_EVIDENCE"}
        
    documents = search_results['documents'][0]
    metadatas = search_results['metadatas'][0]
    
    context_text = ""
    citations = []
    for doc, meta in zip(documents, metadatas):
        title = meta.get('title', 'Unknown')
        context_text += f"\n--- Document: {title} ---\n{doc}\n"
        citations.append(title)
        
    prompt = f"""You are an instructional designer. Generate a single Multiple Choice Question (MCQ) 
for the topic "{topic_title}" at a "{difficulty}" difficulty level.
You MUST base the question and correct answer STRICTLY on the provided Knowledge Base Context.
Do not hallucinate.

Return the result as a raw JSON object with NO markdown formatting, NO backticks. The JSON must have these exact keys:
"question": the question text
"options": an array of 4 string options
"correct_answer": the exact string of the correct option
"learning_objective": a short string explaining what this tests
"evidence_quote": a direct quote from the context that proves the answer

Knowledge Base Context:
{context_text}
"""
    try:
        response_text = generate_completion(prompt, temperature=0.2)
        # clean possible markdown
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        quiz_data = json.loads(response_text)
        quiz_data["citations"] = list(set(citations))
        return quiz_data
    except Exception as e:
        return {"error": f"Failed to generate: {str(e)}"}
