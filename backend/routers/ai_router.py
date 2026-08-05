import os

from fastapi import APIRouter, Depends, HTTPException
from langchain_community.chat_message_histories import SQLChatMessageHistory
from openai import OpenAI
from pydantic import BaseModel

from backend.ai_protection import check_ai_request, check_rate_limit
from backend.dependancies import Session, get_current_user, get_db
from backend.vector_store import query_user_context
from db_end.models import optimization_rec, userid

router = APIRouter()


class AIConsultRequest(BaseModel):
    question: str
    invoice_id: int | None = None
    session_id: str | None = None

class AIOptimizeRequest(BaseModel):
    question:str
    invoice_id: int | None=None


groq=OpenAI(base_url=os.getenv("GROQ_API_ENDPOINT"),
            api_key=os.getenv("GROQ_API_KEY"),
            )

@router.post("/consult/groq")
def ai_consultationg(
    payload: AIConsultRequest,
    db: Session = Depends(get_db),
    current_user: userid = Depends(get_current_user)
):
    check_ai_request(payload)

    check_rate_limit(current_user,5,15)

    context_blocks = query_user_context(
        user_id=current_user.id,
        question=payload.question,
        invoice_id=payload.invoice_id,
        n_results=15
    )

    if not context_blocks:
        return {
            "answer": "No invoice context was found. Please upload and index invoice data first.",
            "context_used": []
        }

    context_text = "\n\n".join(
        [
            f"Context Row {index + 1}:\n{item['document']}"
            for index, item in enumerate(context_blocks)
        ]
    )

    session_id = payload.session_id or "default_session"
    db_url = os.getenv("DATABASE_URL") or "sqlite:///test_runner_db.sqlite"
    chat_history_store = SQLChatMessageHistory(
        session_id=session_id,
        connection=db_url,
        table_name="message_store"
    )

    formatted_history = []
    # Keep last 10 messages (5 turns)
    for msg in chat_history_store.messages[-10:]:
        role = "user" if msg.type == "human" else "assistant"
        formatted_history.append({"role": role, "content": msg.content})

    prompt = f"""
Relevant invoice context:
{context_text}

User question:
{payload.question}

Instructions:
- You are a highly capable GenAI FinOps consultant.
- Analyze the provided invoice context to answer questions about token usage, model spend, application spend, and optimization.
- If the user asks a general question about a model (e.g., "what is Gemini Embedding used for?"), use your general knowledge to explain its typical use cases, even if it's not explicitly defined in the invoice context.
- Be conversational, direct, and helpful. Do not sound robotic.
- Do NOT apologize excessively or say "the specific use case is not explicitly stated in the invoice context". Just provide the best possible functional answer using your knowledge combined with the context.
- Do not use the phrase "based on the context provided".
- Maintain conversational continuity. If the user asks "what is the first model?", refer back to your previous responses in the chat history to deduce what they are referring to.
"""

    messages_payload = [
        {
            "role": "system",
            "content": (
                "You are an expert AI cost management consultant. "
                "You help users understand their AI usage and spending. "
                "You combine the specific invoice data provided with your broad general knowledge of AI models, providers, and FinOps best practices. "
                "Always act conversational, intuitive, and highly functional. "
                "Do not invent or hallucinate financial numbers. "
            )
        }
    ]
    
    messages_payload.extend(formatted_history)
    messages_payload.append({"role": "user", "content": prompt})

    response = groq.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages_payload
    )

    answer = response.choices[0].message.content

    # Save to LangChain SQL memory
    chat_history_store.add_user_message(payload.question)
    chat_history_store.add_ai_message(answer)

    return {
        "answer": answer,
        "context_used": context_text,
        

    }



@router.delete("/history/{session_id}")
def clear_chat_history(session_id: str):
    db_url = os.getenv("DATABASE_URL") or "sqlite:///test_runner_db.sqlite"
    chat_history_store = SQLChatMessageHistory(
        session_id=session_id,
        connection=db_url,
        table_name="message_store"
    )
    chat_history_store.clear()
    return {"message": "Session history cleared."}

@router.post("/optimize")
def ai_optimization(
    payload: AIOptimizeRequest,
    db: Session = Depends(get_db),
    current_user: userid = Depends(get_current_user)
):
    if not payload.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    context_blocks = query_user_context(
        user_id=current_user.id,
        question=payload.question,
        invoice_id=payload.invoice_id,
        n_results=50
    )

    if not context_blocks:
        return {
            "answer": "No invoice context was found. Please upload and index invoice data first.",
            "context_used": []
        }

    context_text = "\n\n".join(
        [
            f"Context Row {index + 1}:\n{item['document']}"
            for index, item in enumerate(context_blocks)
        ]
    )
    try:
        optimize_hist = (
            db.query(optimization_rec).filter(optimization_rec.invoice_id == payload.invoice_id).first())
        return{
            "invoice_id":optimize_hist.invoice_id,
            "answer":optimize_hist.steps
            }
    except Exception:
        prompt = f"""
User question:
{payload.question}

Relevant invoice context:
{context_text}

Instructions:
- Answer as a GenAI FinOps consultant.
- Be direct and specific.
- Use only the invoice context provided.
- Do not say "based on the context provided".
- If the data is insufficient, say what is missing.
"""
        response = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a GenAI cost management consultant. "
                        "You analyze AI invoices, token usage, model spend, "
                        "application spend, provider usage, and optimization opportunities."
                        "do not make calculate anything or make up data, if no cost or spend is asked directly do not provide in the answer"
                        "analyse the chat history presented to you and if the question is simillar return the answer to save time and compute"
                        "if asked about previous question return previous question and answer"
                        )
                },
                {
                "role": "user",
                "content": prompt,
                }
            ]
            
        )
        answer = response.choices[0].message.content
        optimization = optimization_rec(
            invoice_id=payload.invoice_id,
            steps=answer
            )
        db.add(optimization)
        db.commit()
        db.refresh(optimization)
        
        return {
            "answer": answer,
            "context_used": context_blocks,
            }

#def rerank(context_blocks, question):


@router.post("/rewrite")
def rewrite_prompt(
    payload: AIConsultRequest,
    db: Session = Depends(get_db),
    current_user: userid = Depends(get_current_user)
):
    response=groq.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role":"system","content":"Rewrite the user's question into 3 retrieval keywords that preserve the meaning but vary the wording and angle. One per line, no numbering."},
            {"role":"user","content":payload.question}
        ]
    )
    

    new_query=response.choices[0].message.content

    return{
        "new_query":new_query,
        "original_query":payload.question
    }


