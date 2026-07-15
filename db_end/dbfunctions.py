import json
import re
import pandas as pd

from db_end.db1 import SessionLocal
from db_end.models import invoice, invoice_rows


def get_db_session():
    return SessionLocal()


def normalize_col_name(col):
    return re.sub(r"[^a-z0-9]", "", str(col).lower().strip())


def find_col(df, possible_names):
    if df is None or df.empty:
        return None

    normalized_cols = {
        normalize_col_name(col): col
        for col in df.columns
    }

    for name in possible_names:
        normalized_name = normalize_col_name(name)

        if normalized_name in normalized_cols:
            return normalized_cols[normalized_name]

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


def save_file(df, file_name, file_hash=""):
    db = get_db_session()

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

        return new_invoice.id

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()



def model_to_dict(record):
    return {
        column.name: getattr(record, column.name)
        for column in record.__table__.columns
    }



def get_records(model_class):
    db = get_db_session()

    try:
        records = db.query(model_class).all()
        return [model_to_dict(record) for record in records]

    except Exception as e:
        print("Error in get_records:", e)
        return []

    finally:
        db.close()



