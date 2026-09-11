from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import Optional

app = FastAPI()

# CORS fix: Allows frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    conn = sqlite3.connect('crm.db')
    conn.row_factory = sqlite3.Row
    return conn

class TicketCreate(BaseModel):
    customer_name: str
    customer_email: str
    subject: str
    description: str

class TicketUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

@app.post("/api/tickets")
def create_ticket(ticket: TicketCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM tickets")
    count = cursor.fetchone()[0]
    ticket_id = f"TKT-{(count + 1):03d}"
    
    cursor.execute('''
        INSERT INTO tickets (ticket_id, customer_name, customer_email, subject, description)
        VALUES (?, ?, ?, ?, ?)
    ''', (ticket_id, ticket.customer_name, ticket.customer_email, ticket.subject, ticket.description))
    
    conn.commit()
    cursor.execute("SELECT created_at FROM tickets WHERE ticket_id = ?", (ticket_id,))
    created_at = cursor.fetchone()['created_at']
    conn.close()
    
    return {"ticket_id": ticket_id, "created_at": created_at}

@app.get("/api/tickets")
def get_tickets(status: Optional[str] = None, search: Optional[str] = None):
    conn = get_db_connection()
    query = "SELECT ticket_id, customer_name, subject, status, created_at FROM tickets WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if search:
        query += " AND (customer_name LIKE ? OR ticket_id LIKE ? OR customer_email LIKE ? OR description LIKE ?)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term, search_term, search_term])
        
    cursor = conn.execute(query, params)
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tickets

@app.get("/api/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    conn = get_db_connection()
    ticket = conn.execute("SELECT ticket_id, customer_name, customer_email, subject, description, status, created_at FROM tickets WHERE ticket_id = ?", (ticket_id,)).fetchone()
    
    if not ticket:
        conn.close()
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    notes = conn.execute("SELECT note_text, created_at FROM notes WHERE ticket_id = ?", (ticket_id,)).fetchall()
    conn.close()
    
    result = dict(ticket)
    result["notes"] = [dict(n) for n in notes]
    return result

@app.put("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: str, ticket_update: TicketUpdate):
    conn = get_db_connection()
    
    cursor = conn.execute("UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE ticket_id = ?", (ticket_update.status, ticket_id))
    
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Ticket not found")
        
    if ticket_update.notes:
        conn.execute("INSERT INTO notes (ticket_id, note_text) VALUES (?, ?)", (ticket_id, ticket_update.notes))
        
    conn.commit()
    cursor.execute("SELECT updated_at FROM tickets WHERE ticket_id = ?", (ticket_id,))
    updated_at = cursor.fetchone()['updated_at']
    conn.close()
    
    return {"success": True, "updated_at": updated_at}