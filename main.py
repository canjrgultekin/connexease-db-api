import os
import asyncpg
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

DB_CONN = os.getenv(
    "DATABASE_URL",
    "postgresql://zTRsUVcSV3jjWPOE:fj2Nm8Ra02LZzhbNJO6CNS4EUzfWDktH@connexeasedb-pg-prod.postgres.database.azure.com:5432/connexease_crm_db"
)

class QueryRequest(BaseModel):
    query: str

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/run-query")
async def run_query(req: QueryRequest):
    try:
        conn = await asyncpg.connect(DB_CONN, ssl="require")
        results = await conn.fetch(req.query)
        await conn.close()
        return {"status": "success", "rows": [dict(r) for r in results]}
    except Exception as e:
        return {"status": "error", "error": str(e)}
