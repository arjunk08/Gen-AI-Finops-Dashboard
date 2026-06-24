from pathlib import Path
import chromadb

from db_end.models import invoice_rows


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_PATH = BASE_DIR / "chroma_store"

chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)

collection = chroma_client.get_or_create_collection(
    name="genai_invoice_rows"
)


def invoice_row_to_document(row):
    return (
        f"Invoice ID: {row.invoice_id} | "
        f"Row ID: {row.id} | "
        f"Billing Date: {row.billing_date} | "
        f"Provider: {row.provider} | "
        f"Application: {row.application} | "
        f"Team: {row.team} | "
        f"Business Unit: {row.business_unit} | "
        f"Model: {row.Model} | "
        f"Request Count: {row.request_count} | "
        f"Input Tokens: {row.input_tokens} | "
        f"Output Tokens: {row.output_tokens} | "
        f"Total Tokens: {row.total_tokens} | "
        f"Rate USD: {row.rate_usd} | "
        f"Amount USD: {row.amount_usd}"
    )


def index_invoice_rows(db, user_id, invoice_id):
    rows = (
        db.query(invoice_rows)
        .filter(invoice_rows.invoice_id == invoice_id)
        .all()
    )

    if not rows:
        return {
            "indexed": 0,
            "message": "No SQLite invoice rows found for this invoice."
        }

    ids = []
    documents = []
    metadatas = []

    for row in rows:
        chroma_id = f"user_{user_id}_invoice_{invoice_id}_row_{row.id}"

        ids.append(chroma_id)
        documents.append(invoice_row_to_document(row))
        metadatas.append({
            "user_id": str(user_id),
            "invoice_id": str(invoice_id),
            "row_id": str(row.id),
            "provider": str(row.provider or ""),
            "model": str(row.Model or ""),
            "application": str(row.application or ""),
            "team": str(row.team or "")
        })

    existing = collection.get(ids=ids)
    existing_ids = set(existing.get("ids", []))

    new_ids = []
    new_documents = []
    new_metadatas = []

    for idx, chroma_id in enumerate(ids):
        if chroma_id not in existing_ids:
            new_ids.append(chroma_id)
            new_documents.append(documents[idx])
            new_metadatas.append(metadatas[idx])

    if new_ids:
        collection.add(
            ids=new_ids,
            documents=new_documents,
            metadatas=new_metadatas
        )

    return {
        "indexed": len(new_ids),
        "skipped_existing": len(existing_ids),
        "total_sqlite_rows": len(rows),
        "chroma_path": str(CHROMA_PATH)
    }


def query_user_context(user_id, question, invoice_id=None, n_results=10):
    user_id = str(user_id)

    if invoice_id is not None:
        where_filter = {
            "$and": [
                {"user_id": user_id},
                {"invoice_id": str(invoice_id)}
            ]
        }
    else:
        where_filter = {
            "user_id": user_id
        }

    result = collection.query(
        query_texts=[question],
        n_results=n_results,
        where=where_filter
    )

    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]

    context_blocks = []

    for document, metadata in zip(documents, metadatas):
        context_blocks.append({
            "document": document,
            "metadata": metadata
        })

    return context_blocks


def debug_chroma_for_user(user_id):
    result = collection.get(
        where={
            "user_id": str(user_id)
        }
    )

    return {
        "chroma_path": str(CHROMA_PATH),
        "count_for_user": len(result.get("ids", [])),
        "ids": result.get("ids", [])[:10],
        "metadatas": result.get("metadatas", [])[:5],
        "documents": result.get("documents", [])[:3]
    }


def debug_chroma_all():
    result = collection.get()

    return {
        "chroma_path": str(CHROMA_PATH),
        "total_count": len(result.get("ids", [])),
        "ids": result.get("ids", [])[:10],
        "metadatas": result.get("metadatas", [])[:5]
    }