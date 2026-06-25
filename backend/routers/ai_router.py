import os
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from openai import AzureOpenAI
import requests

from db_end.models import userid,chathistory,invoice_rows,invoice,optimization_rec
from backend.dependancies import get_current_user,get_db,Session
from backend.vector_store import query_user_context
from backend.ai_protection import check_rate_limit,check_ai_request


router = APIRouter()


class AIConsultRequest(BaseModel):
    question: str
    invoice_id: Optional[int] = None

class AIOptimizeRequest(BaseModel):
    question:str
    invoice_id: Optional[int]=None


client = AzureOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION")
)

 



@router.post("/consult")
def ai_consultation(
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

    chat_hist = (
    db.query(chathistory)
    .filter(chathistory.invoice_id == payload.invoice_id)
    .all())

    history = [
    {
        "Invoice_id": item.invoice_id,
        "answer": item.answer,
        "question": item.question,
        "retrieved_context": item.retrieved_context
    }
    for item in chat_hist
    ]
    history_text = "\n\n".join(
        [
            f"Previous Question: {item['question']}\nPrevious Answer: {item['answer']}"
            for item in history
            ]
            )

    prompt = f"""
User question:
{payload.question}

Relevant invoice context:
{context_text}

chat_history_for invoice:
{history_text}

Instructions:
- Answer as a GenAI FinOps consultant.
- Be direct and specific.
- Use only the invoice context provided.
- Do not say "based on the context provided".
- If the data is insufficient, say what is missing.
"""

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
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
        ],
        temperature=0.2,
        max_completion_tokens=400
    )

    answer = response.choices[0].message.content

    if payload.invoice_id is not None:
        chat_history = chathistory(
            invoice_id=payload.invoice_id,
            question=payload.question,
            answer=answer,
            retrieved_context=json.dumps(context_blocks),
        )
        db.add(chat_history)
        db.commit()
        db.refresh(chat_history)

    return {
        "answer": answer,
        "context_used": context_blocks,
        

    }



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
    except:
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
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
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
            ],
            temperature=0.2
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