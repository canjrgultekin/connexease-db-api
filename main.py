import os
import json
import asyncpg
import uuid
import datetime
import decimal
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

app = FastAPI()

DB_CONN = os.getenv(
    "DATABASE_URL",
    "postgresql://zTRsUVcSV3jjWPOE:fj2Nm8Ra02LZzhbNJO6CNS4EUzfWDktH@connexeasedb-pg-prod.postgres.database.azure.com:5432/connexease_crm_db"
)

class QueryRequest(BaseModel):
    query: str

def json_serializer(obj):
    """PostgreSQL özel tiplerini JSON stringe çevirir"""
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, bytes):
        return obj.decode(errors="ignore")
    return str(obj)

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/run-query", response_class=PlainTextResponse)
async def run_query(req: QueryRequest):
    try:
        conn = await asyncpg.connect(DB_CONN, ssl="require")
        results = await conn.fetch(req.query)
        await conn.close()

        json_data = json.dumps(
            {"status": "success", "rows": [dict(r) for r in results]},
            ensure_ascii=False,
            default=json_serializer
        )
        # JSON'u kod bloğu içinde döndür
        return f"```json\n{json_data}\n```"

    except Exception as e:
        error_data = json.dumps(
            {"status": "error", "error": str(e)},
            ensure_ascii=False
        )
        return f"```json\n{error_data}\n```"
