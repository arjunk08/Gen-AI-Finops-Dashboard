from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import pandas as pd 
import re
from db_end.models import invoice, userid,invoice_rows, chathistory
from backend.dependancies import get_db, get_current_user
from sqlalchemy import func
import json
import io
import hashlib
from backend.vector_store import index_invoice_rows
from backend.vector_store import index_invoice_rows, debug_chroma_for_user, debug_chroma_all

router = APIRouter()


def normalize_col_name(col):
    return re.sub(r"[^a-z0-9]", "", str(col).lower().strip())

def find_col(df, possible_names):
  
    if df is None or df.empty:
        return None

    df_cols = {
        normalize_col_name(col): col
        for col in df.columns
    }

    for name in possible_names:
        Newname = normalize_col_name(name)

        if Newname in df_cols:
            return df_cols[Newname]

    return None


def safe_int(value, default=0):
    converted = pd.to_numeric(value, errors="coerce")

    if pd.isna(converted):
        return default

    return int(converted)


def safe_float(value, default=0.0):
    converted = pd.to_numeric(value, errors="coerce")

    if pd.isna(converted):
        return default

    return float(converted)


def save_file(df, file_name, file_hash="", db: Session = None, user_id: int = None):
    try:
        amount_col = find_col(df, [
            "AmountUSD",
            "Amount",
            "CostUSD",
            "Cost",
            "TotalCost",
            "Total_cost",
            "totalcost"
        ])

        token_col = find_col(df, [
            "total_tokens",
            "QuantityTokens",
            "Quantity",
            "TokenCount",
            "Tokens",
            "token",
            "tokens",
            "totaltokens"
        ])

        request_col = find_col(df, [
            "request_count",
            "RequestCount",
            "Requests",
            "requests"
        ])

        input_token_col = find_col(df, [
            "input_tokens",
            "InputTokens",
            "PromptTokens"
        ])

        output_token_col = find_col(df, [
            "output_tokens",
            "OutputTokens",
            "CompletionTokens"
        ])

        model_col = find_col(df, [
            "Models",
            "Model",
            "ModelOrTool",
            "llms",
            "tools",
            "model"
        ])

        date_col = find_col(df, [
            "BillingPeriod",
            "Date",
            "UsageDate",
            "InvoiceDate",
            "week"
        ])

        provider_col = find_col(df, [
            "provider",
            "Provider",
            "CloudProvider"
        ])

        app_col = find_col(df, [
            "application",
            "Application",
            "Workspace",
            "Project"
        ])

        team_col = find_col(df, [
            "team",
            "Team",
            "Department",
            "business_unit",
            "Business Unit",
            "workspace"
        ])

        business_unit_col = find_col(df, [
            "business_unit",
            "Business Unit",
            "Department"
        ])

        if amount_col:
            total_cost = float(pd.to_numeric(df[amount_col], errors="coerce").fillna(0).sum())
        else:
            total_cost = 0.0

        if token_col:
            total_tokens = int(pd.to_numeric(df[token_col], errors="coerce").fillna(0).sum())
        else:
            total_tokens = 0

        new_invoice = invoice(
            file_name=file_name,
            file_hashid=str(file_hash),
            invoice_id=user_id,
            total_cost=total_cost,
            total_tokens=total_tokens,
            row_count=len(df)
        )

        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)

        for index, row in df.iterrows():
            raw_data = row.fillna("").astype(str).to_dict()

            row_amount = safe_float(row[amount_col]) if amount_col and pd.notna(row[amount_col]) else 0.0
            row_tokens = safe_int(row[token_col]) if token_col and pd.notna(row[token_col]) else 0
            row_requests = safe_int(row[request_col]) if request_col and pd.notna(row[request_col]) else 0
            row_input_tokens = safe_int(row[input_token_col]) if input_token_col and pd.notna(row[input_token_col]) else 0
            row_output_tokens = safe_int(row[output_token_col]) if output_token_col and pd.notna(row[output_token_col]) else 0

            new_row = invoice_rows(
                invoice_id=new_invoice.id,

                billing_date=str(row[date_col]) if date_col and pd.notna(row[date_col]) else None,
                provider=str(row[provider_col]) if provider_col and pd.notna(row[provider_col]) else None,
                application=str(row[app_col]) if app_col and pd.notna(row[app_col]) else None,
                team=str(row[team_col]) if team_col and pd.notna(row[team_col]) else None,
                business_unit=str(row[business_unit_col]) if business_unit_col and pd.notna(row[business_unit_col]) else None,
                Model=str(row[model_col]) if model_col and pd.notna(row[model_col]) else None,

                request_count=row_requests,
                input_tokens=row_input_tokens,
                output_tokens=row_output_tokens,
                total_tokens=row_tokens,

                amount_usd=row_amount,

                raw_data=json.dumps(raw_data),
                chroma_id=f"{new_invoice.id}_{index}"
            )

            db.add(new_row)

        db.commit()
        db.refresh(new_invoice)

        for index, row in df.iterrows():
            raw_data = row.fillna("").astype(str).to_dict()

            row_amount = safe_float(row[amount_col]) if amount_col and pd.notna(row[amount_col]) else 0.0
            row_tokens = safe_int(row[token_col]) if token_col and pd.notna(row[token_col]) else 0
            row_requests = safe_int(row[request_col]) if request_col and pd.notna(row[request_col]) else 0
            row_input_tokens = safe_int(row[input_token_col]) if input_token_col and pd.notna(row[input_token_col]) else 0
            row_output_tokens = safe_int(row[output_token_col]) if output_token_col and pd.notna(row[output_token_col]) else 0

            new_row = invoice_rows(
                invoice_id=new_invoice.id,

                billing_date=str(row[date_col]) if date_col and pd.notna(row[date_col]) else None,
                provider=str(row[provider_col]) if provider_col and pd.notna(row[provider_col]) else None,
                application=str(row[app_col]) if app_col and pd.notna(row[app_col]) else None,
                team=str(row[team_col]) if team_col and pd.notna(row[team_col]) else None,
                business_unit=str(row[business_unit_col]) if business_unit_col and pd.notna(row[business_unit_col]) else None,
                Model=str(row[model_col]) if model_col and pd.notna(row[model_col]) else None,

                request_count=row_requests,
                input_tokens=row_input_tokens,
                output_tokens=row_output_tokens,
                total_tokens=row_tokens,

                amount_usd=row_amount,

                raw_data=json.dumps(raw_data),
                chroma_id=f"{new_invoice.id}_{index}"
            )

            db.add(new_row)

        db.commit()
        index_result = index_invoice_rows(
            db=db,
            user_id=userid.id,
            invoice_id=new_invoice.id
              )

        return new_invoice.id

    except Exception as e:
        if db is not None:
            try:
                db.rollback()
            except Exception:
                pass
        raise e



def model_to_dict(record):
    return {
        column.name: getattr(record, column.name)
        for column in record.__table__.columns
    }




@router.post("/upload-invoice")
async def upload_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: userid = Depends(get_current_user),
):
    """Upload an invoice file (CSV, XLS, XLSX, JSON) and persist rows to the DB linked to the current user."""
    try:
        contents = await file.read()
        file_hash = hashlib.sha256(contents).hexdigest()
        filename = file.filename or "uploaded"
        ext = filename.split(".")[-1].lower() if "." in filename else ""

        # Read file into DataFrame
        try:
            if ext in ("csv", "txt"):
                df = pd.read_csv(io.BytesIO(contents))
            elif ext in ("xls", "xlsx"):
                df = pd.read_excel(io.BytesIO(contents))
            elif ext in ("json",):
                df = pd.read_json(io.BytesIO(contents))
            else:
                # fallback to csv
                df = pd.read_csv(io.BytesIO(contents))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Unable to parse uploaded file: {e}")

        invoice_id = save_file(df, filename, file_hash=file_hash, db=db, user_id=current_user.id)

        return {"invoice_id": invoice_id, "file_name": filename, "file_hash": file_hash}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))






@router.get("/my-invoices")
def get_my_invoices(
    db: Session = Depends(get_db),
    current_user: userid = Depends(get_current_user)
):
    invoices = (
        db.query(invoice)
        .filter(invoice.invoice_id == current_user.id)
        .order_by(invoice.invoice_id.desc())
        .all()
    )

    return [
        {
            "id": item.id,
            "file_name": item.file_name,
            "file_hashid": item.file_hashid,
            "total_cost": float(item.total_cost or 0),
            "total_tokens": int(item.total_tokens or 0),
            "row_count": int(item.row_count or 0)
        }
        for item in invoices
    ]


@router.get("/dashboard-summary")
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: userid = Depends(get_current_user)
):
    user_invoices = (
        db.query(invoice)
        .filter(invoice.invoice_id == current_user.id)
        .order_by(invoice.id.desc())
        .all()
    )

    if not user_invoices:
        return {
            "invoice_count": 0,
            "paycycle_start": None,
            "paycycle_end": None,
            "total_cost": 0,
            "total_tokens": 0
        }

    invoice_ids = [item.id for item in user_invoices]

    
    invoice_summary = (
        db.query(
            func.sum(invoice.total_cost).label("total_cost"),
            func.sum(invoice.total_tokens).label("total_tokens")
        )
        .filter(invoice.invoice_id == current_user.id)
        .first()
    )
    latest_invoice = (
    db.query(invoice)
    .filter(invoice.invoice_id== current_user.id)
    .order_by(invoice.id.desc())
    .first()
    )

    per_invoice_summary = (
        db.query(
            invoice.total_cost.label("total_cost1"),
            invoice.total_tokens.label("total_tokens1")
            )
            .filter(invoice.id == latest_invoice.id)
            .first()
        )

    # Use invoice_rows only for date range
    date_summary = (
        db.query(
            func.min(invoice_rows.billing_date).label("paycycle_start"),
            func.max(invoice_rows.billing_date).label("paycycle_end")
        )
        .filter(invoice_rows.invoice_id.in_(invoice_ids))
        .first()
    )

    return {
        "invoice_count": int(len(user_invoices)),
        "current_invoice":latest_invoice.id,
        "paycycle_start": date_summary.paycycle_start if date_summary else None,
        "paycycle_end": date_summary.paycycle_end if date_summary else None,
        "total_cost": float(invoice_summary.total_cost or 0),
        "total_tokens": int(invoice_summary.total_tokens or 0),
        "total_cost_perinvoice":float(per_invoice_summary.total_cost1),
        "total_tokens_perinvoice":int(per_invoice_summary.total_tokens1),
    }

@router.get("/models-summary")
def get_models_summary(
    db: Session = Depends(get_db),
    current_user: userid = Depends(get_current_user)
):
    user_invoices = (
        db.query(invoice)
        .filter(invoice.invoice_id == current_user.id)
        .all()
    )

    if not user_invoices:
        return {
            "models": [],
            "providers": []
        }

    invoice_ids = [item.id for item in user_invoices]

    model_rows = (
        db.query(invoice_rows.Model)
        .filter(invoice_rows.invoice_id.in_(invoice_ids))
        .all()
    )

    provider_rows = (
        db.query(invoice_rows.provider)
        .filter(invoice_rows.invoice_id.in_(invoice_ids))
        .distinct()
        .all()
    )

    models = [
        row[0]
        for row in model_rows
        if row[0] is not None and row[0] != ""
    ]

    providers = [
        row[0]
        for row in provider_rows
        if row[0] is not None and row[0] != ""
    ]

    return {
        "models": models,
        "providers": providers
    }

@router.post("/reindex")
def reindex_user_invoices(
    db: Session = Depends(get_db),
    current_user: userid = Depends(get_current_user)
):
    user_invoices = (
        db.query(invoice)
        .filter(invoice.invoice_id == current_user.id)
        .all()
    )

    results = []

    for inv in user_invoices:
        result = index_invoice_rows(
            db=db,
            user_id=current_user.id,
            invoice_id=inv.id
        )

        results.append({
            "invoice_id": inv.id,
            "result": result
        })

    return {
        "message": "Reindex completed",
        "invoice_count": len(user_invoices),
        "results": results
    }


@router.get("/debug-chroma")
def debug_chroma(
    current_user: userid = Depends(get_current_user)
):
    return debug_chroma_for_user(current_user.id)


@router.get("/debug-chroma-all")
def debug_chroma_all_route():
    return debug_chroma_all()


@router.get("/{invoice_id}")
def get_invoice_by_id(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: userid = Depends(get_current_user)
):
    
    selected_invoice = (
        db.query(invoice)
        .filter(
            invoice.id == invoice_id,
            invoice.invoice_id == current_user.id
        )
        .first()
    )

    if selected_invoice is None:
        raise HTTPException(
            status_code=404,
            detail="Invoice not found"
        )


    unique_invoice_row_records = (
        db.query(invoice_rows.id)
        .filter(invoice_rows.invoice_id==selected_invoice.id)
        .distinct()
        .all()
    )

    unique_invoice_row_records = [row_id[0] for row_id in unique_invoice_row_records]

    unique_row_records=(
        db.query(invoice_rows)
        .filter(invoice_rows.id.in_(unique_invoice_row_records))
        .order_by(invoice_rows.id)
        .all()
    )


    return {
        "invoice": {
            "id": selected_invoice.id,
            "file_name": selected_invoice.file_name,
            "file_hashid": selected_invoice.file_hashid,
            "total_cost": float(selected_invoice.total_cost or 0),
            "total_tokens": int(selected_invoice.total_tokens or 0),
            "row_count": int(selected_invoice.row_count or 0)
        },
        "rows": [
            {
                "id": row.id,
                "invoice_id": row.invoice_id,
                "provider": row.provider,
                "Model": row.Model,
                "total_tokens": int(row.total_tokens or 0),
                "application": row.application,
                "business_unit": row.business_unit,
                "team": row.team,
                "billing_date": row.billing_date,
                "amount_usd": float(row.amount_usd or 0),
                "request_count": int(row.request_count or 0),
                "input_tokens": int(row.input_tokens or 0),
                "output_tokens": int(row.output_tokens or 0),
                "rate_usd": float(row.rate_usd or 0),
                "raw_data": row.raw_data,
                "chroma_id": row.chroma_id
            }
            for row in unique_row_records
        ]
    }

@router.delete("/del/{Invoice_id}")
def del_invoice(
    Invoice_id:int,
    db:Session=Depends(get_db),
    current_user:userid=Depends(get_current_user)
):

    db.query(invoice_rows).filter(invoice_rows.invoice_id==Invoice_id).delete()
    db.commit()
    db.query(invoice).filter(invoice.id==Invoice_id).delete()
    db.commit()

    return{
        "Message":"Invoice Deleted Succesfully"
    }


@router.get("/rd/{user_id}")
def get_raw_data_by_user(
    user_id : int,
    db: Session = Depends(get_db),
    current_user: userid= Depends(get_current_user)
):
       user_invoices = (
        db.query(invoice)
        .filter(invoice.invoice_id == current_user.id)
        .first()
        )
       raw_data=(
           db.query(invoice_rows)
           .filter(invoice_rows.raw_data.in_(user_invoices))
           .all()
       )
       return{
           "raw_data":raw_data
       }


@router.get("/chat/{Invoice_id}")
def get_chat(
    Invoice_id : str,
    db: Session=Depends(get_db),
    current_user: userid= Depends(get_current_user)
):
    
    chat_hist=(db.query(chathistory).filter(chathistory.invoice_id==Invoice_id).all())

    return{
        "Invoice_id":chat_hist.invoice_id,
        "answer":chat_hist.answer,
        "question": chat_hist.question,
        "retrieved_context":chat_hist.retrieved_context
    }


