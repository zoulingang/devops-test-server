from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app import db

FIELDS = ("name", "email", "phone", "company", "notes")


class CustomerIn(BaseModel):
    name: str = Field(min_length=1)
    email: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    notes: Optional[str] = None


class Customer(CustomerIn):
    id: int
    created_at: str


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Simple CRM", lifespan=lifespan)

# No auth: allow any origin so the static frontend can call the API.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def get_or_404(conn, customer_id: int) -> dict:
    row = conn.execute("SELECT * FROM customers WHERE id = ?", (customer_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return dict(row)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/customers", response_model=list[Customer])
def list_customers():
    with db.connect() as conn:
        rows = conn.execute("SELECT * FROM customers ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


@app.post("/api/customers", response_model=Customer, status_code=201)
def create_customer(data: CustomerIn):
    with db.connect() as conn:
        cur = conn.execute(
            f"INSERT INTO customers ({', '.join(FIELDS)}) VALUES (?, ?, ?, ?, ?)",
            tuple(getattr(data, f) for f in FIELDS),
        )
        return get_or_404(conn, cur.lastrowid)


@app.get("/api/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: int):
    with db.connect() as conn:
        return get_or_404(conn, customer_id)


@app.put("/api/customers/{customer_id}", response_model=Customer)
def update_customer(customer_id: int, data: CustomerIn):
    with db.connect() as conn:
        get_or_404(conn, customer_id)
        conn.execute(
            f"UPDATE customers SET {', '.join(f + ' = ?' for f in FIELDS)} WHERE id = ?",
            (*(getattr(data, f) for f in FIELDS), customer_id),
        )
        return get_or_404(conn, customer_id)


@app.delete("/api/customers/{customer_id}", status_code=204)
def delete_customer(customer_id: int):
    with db.connect() as conn:
        get_or_404(conn, customer_id)
        conn.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
