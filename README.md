# Datastraw CRM

A full-stack Customer Support Ticketing CRM system built with FastAPI, SQLite, and Vanilla JS/Tailwind CSS.

## Features
- Create, view, search, and filter support tickets.
- Update ticket status and add internal notes.

## Setup Instructions
1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Initialize the database: `python database.py`
6. Run the backend server: `uvicorn main:app --reload`
7. Open `index.html` in your web browser.