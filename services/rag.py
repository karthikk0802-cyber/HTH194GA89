import datetime
from services.embedding import search_chroma
from services.llm import generate_completion
import json

def determine_evidence_confidence(results):
    """Calculate confidence based on ChromaDB distance scores (lower is better for cosine) and chunk count."""
    if not results or not results['documents'] or not results['documents'][0]:
        return "Insufficient"
    
    distances = results['distances'][0]
    
    # Naive scoring based on distances
    avg_dist = sum(distances) / len(distances)
    
    if avg_dist < 0.3:
        return "Strong"
    elif avg_dist < 0.5:
        return "Moderate"
    elif avg_dist < 0.7:
        return "Limited"
    else:
        return "Insufficient"

def generate_rag_response(query, role="all"):
    """Fetch chunks and answer query with strict grounding."""
    # 1. Retrieve
    search_results = search_chroma(query, n_results=5, role_filter=role)
    confidence = determine_evidence_confidence(search_results)
    
    trace = {
        "timestamp": datetime.datetime.now().isoformat(),
        "query": query,
        "confidence": confidence,
        "chunks": [],
        "answer": "",
        "citations": []
    }
    
    if confidence == "Insufficient":
        trace["answer"] = "I have insufficient information in the approved knowledge base to answer this question."
        return trace
        
    documents = search_results['documents'][0]
    metadatas = search_results['metadatas'][0]
    distances = search_results['distances'][0]
    
    context_text = ""
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
        title = meta.get('title', 'Unknown')
        doc_role = meta.get('role', 'all')
        context_text += f"\n--- Document [{i+1}]: {title} (Role: {doc_role}) ---\n{doc}\n"
        trace["chunks"].append({"title": title, "distance": dist, "text": doc[:200] + "..."})
        trace["citations"].append(title)
        
    # 2. Augment & Generate
    prompt = f"""You are the Nexora corporate onboarding assistant. 
Answer the user's question STRICTLY based on the provided Knowledge Base context.
If the context does not contain the answer, reply ONLY with: "I have insufficient information in the approved knowledge base to answer this question."
Do not hallucinate external information or policies. Always cite the document title you used to answer.

Knowledge Base Context:
{context_text}

User Question: {query}

Answer:"""
    
    try:
        answer = generate_completion(prompt)
    except Exception as e:
        answer = f"Error generating answer: {str(e)}"
        
    # Handle LLM refusal fallback 
    if "insufficient information" in answer.lower():
        trace["confidence"] = "Insufficient"
        trace["citations"] = []
        
    trace["answer"] = answer
    
    return trace
