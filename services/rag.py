import datetime
from services.embedding import search_chroma
from services.llm import generate_completion

def determine_evidence_confidence(results):
    """Calculate confidence based on ChromaDB distance scores (lower is better for cosine) and chunk count."""
    if not results or not results.get('documents') or not results['documents'][0]:
        return "General AI Guidance"
    
    distances = results.get('distances', [[]])[0]
    if not distances:
        return "General AI Guidance"
        
    avg_dist = sum(distances) / len(distances)
    
    if avg_dist < 0.35:
        return "Strong"
    elif avg_dist < 0.60:
        return "Moderate"
    elif avg_dist < 0.85:
        return "Limited"
    else:
        return "General AI Guidance"

def generate_rag_response(query: str, role: str = "all") -> dict:
    """
    Fetch relevant chunks from ChromaDB and formulate an intelligent, comprehensive answer
    powered by Mistral AI, answering any inquiry from employees.
    """
    clean_query = query.strip()
    if not clean_query:
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "query": query,
            "confidence": "Limited",
            "chunks": [],
            "answer": "Please provide a question or topic you would like assistance with.",
            "citations": []
        }

    # 1. Retrieve relevant knowledge base chunks
    search_results = search_chroma(clean_query, n_results=4, role_filter=role)
    confidence = determine_evidence_confidence(search_results)
    
    trace = {
        "timestamp": datetime.datetime.now().isoformat(),
        "query": clean_query,
        "confidence": confidence,
        "chunks": [],
        "answer": "",
        "citations": []
    }
    
    context_text = ""
    citations_set = set()
    
    if search_results and search_results.get('documents') and search_results['documents'][0]:
        documents = search_results['documents'][0]
        metadatas = search_results['metadatas'][0]
        distances = search_results.get('distances', [[0.5] * len(documents)])[0]
        
        for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances)):
            title = meta.get('title', 'Company Guideline')
            doc_role = meta.get('role', 'all')
            context_text += f"\n--- Document [{i+1}]: {title} (Role Scope: {doc_role}) ---\n{doc}\n"
            trace["chunks"].append({
                "title": title,
                "distance": float(dist) if isinstance(dist, (int, float)) else 0.5,
                "text": (doc[:250] + "...") if len(doc) > 250 else doc
            })
            if dist < 0.75:
                citations_set.add(title)
                
    trace["citations"] = list(citations_set)
    
    # 2. Augment & Generate Prompt for Mistral AI
    prompt = f"""You are the Nexora AI Knowledge Coach, a knowledgeable, friendly, and empowering mentor for all Nexora employees.
Your objective is to provide comprehensive, clear, actionable, and accurate answers to ANY question asked by the employee.

Instructions:
1. If the question pertains to Nexora policies, tools, compensation, schedules, engineering workflows, security, or guidelines, prioritize and cite the verified Knowledge Base Context provided below.
2. If the employee asks general workplace, technical, architectural, programming, or career questions (even beyond the immediate context), provide a thorough, professional, and insightful response drawing upon modern industry best practices.
3. Structure your response clearly using bullet points or concise sections where helpful.
4. Maintain an encouraging and professional tone.

Knowledge Base Context:
{context_text if context_text.strip() else "No specific internal policy documents matched this exact query."}

Employee Question: {clean_query}

Answer:"""

    try:
        answer = generate_completion(prompt, temperature=0.3)
    except Exception as e:
        answer = f"I encountered an issue generating the answer: {str(e)}"
        
    trace["answer"] = answer
    return trace
