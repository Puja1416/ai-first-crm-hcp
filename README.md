# AI-First CRM — HCP Log Interaction

A full-stack healthcare-professional interaction module for pharmaceutical field representatives.

## Assignment coverage

- React UI using Redux Toolkit
- Structured HCP interaction form
- Conversational AI assistant
- Python FastAPI backend
- MySQL database through SQLAlchemy
- LangGraph workflow
- Groq LLM integration
- Five LangGraph tools:
  1. Search HCP
  2. Summarize interaction
  3. Recommend follow-up
  4. Log interaction
  5. Edit interaction

## Project structure

```text
ai-first-crm-hcp/
├── backend/
│   ├── app/
│   ├── create_database.sql
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   ├── package.json
│   └── .env.example
└── README.md
```

## 1. Create the MySQL database

Run this in MySQL Workbench or the MySQL command line:

```sql
CREATE DATABASE IF NOT EXISTS ai_crm
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

## 2. Backend setup

```cmd
cd backend
python -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
copy .env.example .env
```

Edit `backend/.env`:

```env
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost:3306/ai_crm
GROQ_API_KEY=YOUR_GROQ_API_KEY
GROQ_MODEL=gemma2-9b-it
FRONTEND_ORIGIN=http://localhost:5173
```

Start FastAPI:

```cmd
venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Open:

- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`

## 3. Frontend setup

```cmd
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## Example AI assistant prompts

### Search HCP

```text
Search HCPs in Pune
```

### Summarize interaction

```text
Summarize: Dr. Sharma discussed patient adherence challenges, requested the latest outcomes study, and agreed to reconnect next Tuesday.
```

### Recommend follow-up

```text
Recommend follow-up for a positive interaction about adherence concerns and a request for clinical evidence.
```

### Log interaction

```text
Log a Meeting with HCP ID 1 on 2026-07-14 at 17:30:00. We discussed adherence challenges. Attendees were Shubham and Dr. Sharma. Sentiment was Positive. Follow-up is to send the outcomes study.
```

### Edit interaction

```text
Edit interaction 1. Change follow_up_actions to Send the outcomes study by Friday.
```

## LangGraph agent role

The LangGraph workflow acts as the orchestration layer between the conversational user interface, Groq LLM, business tools, and database. It classifies the user's request, selects one of the five permitted tools, validates tool arguments, executes the operation, and converts the result into a concise response.

## Video demonstration plan

1. Explain the assignment and architecture.
2. Show the React structured form.
3. Save an interaction and show it under Recent Interactions.
4. Demonstrate each of the five LangGraph tools through chat.
5. Open FastAPI Swagger and briefly explain endpoints.
6. Show MySQL records.
7. Explain the key project folders.
8. Conclude with the role of LangGraph and Groq.
