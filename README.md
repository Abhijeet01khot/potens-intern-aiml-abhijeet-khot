# Smart Ticket Triage Agent

AI/ML Engineer Intern Take-Home Assignment for Potens Internship Hiring 2026.

This project implements an agentic support-ticket triage system. It takes a free-text complaint, request, or support ticket and returns a structured triage decision with visible reasoning and real callable tools.

---

## Live Demo

Streamlit app: https://smart-ticket-triage-agent.streamlit.app/

Note: The live demo runs using fallback mode unless a valid Gemini API key is configured securely in the deployment environment.

## Problem Statement

The system accepts:

- Free-text ticket input
- Optional metadata such as customer tier, source channel, and previous ticket count

It returns a structured output:

```json
{
  "category": "billing",
  "priority": "P1",
  "next_tool": "lookup_policy_tool",
  "reasoning": "The user reports a payment deduction issue, which belongs to billing and needs quick support.",
  "why": "Money-related issues should be handled quickly because the user is financially affected."
}
```

---

## Categories

The agent classifies tickets into six categories:

1. Billing
2. Technical
3. Account
4. Delivery
5. Refund
6. General

---

## Priority Scheme

| Priority | Meaning |
|---|---|
| P0 | Critical issue that needs immediate human attention, such as fraud, security risk, complete outage, or severe customer impact |
| P1 | Important issue that should be handled quickly, such as payment deducted, account blocked, repeated failure, or delayed service |
| P2 | Normal request or low-risk issue, such as a general question, plan information, or simple update request |

---

## Implemented Tools

The assignment required at least three callable tools. This project implements four real Python tools.

### 1. `lookup_policy_tool`

Looks up the internal handling policy for the selected ticket category.

Returns:

- SLA
- Responsible team
- Handling rule

### 2. `search_similar_ticket_tool`

Searches a mock database of past tickets and returns the most similar previous case.

For this 24-hour assignment version, similarity is calculated using simple word overlap.

### 3. `draft_acknowledgement_tool`

Creates a customer-facing acknowledgement draft based on the ticket category and priority.

### 4. `human_escalation_tool`

Stretch feature.

Escalates tickets to a human support lead when:

- Priority is P0
- Confidence is below 0.60
- The agent selects human escalation as the next tool

---

## Reasoning Trace

Every decision includes a visible reasoning trace.

The trace shows:

1. Input received
2. LLM or fallback decision
3. Triage decision created
4. Policy lookup tool call
5. Similar ticket search tool call
6. Acknowledgement draft tool call
7. Human escalation tool call, if required

The Streamlit UI displays this trace step by step using expandable sections.

---

## Tech Stack

- Python
- Streamlit
- Google Gemini API
- python-dotenv
- Git and GitHub

---

## Project Structure

```text
potens-intern-aiml-abhijeet-khot/
│
├── app.py
├── agent.py
├── tools.py
├── baseline.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
└── examples/
    ├── example_01.json
    ├── example_02.json
    ├── example_03.json
    ├── example_04.json
    ├── example_05.json
    ├── example_06.json
    ├── example_07.json
    ├── example_08.json
    ├── example_09.json
    └── example_10.json
```

---

## How to Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Abhijeet01khot/potens-intern-aiml-abhijeet-khot.git
cd potens-intern-aiml-abhijeet-khot
```


### 2. Create virtual environment

```bash
python -m venv venv
```

### 3. Activate virtual environment

For Windows PowerShell:

```bash
.\venv\Scripts\Activate.ps1
```

If script execution is blocked, run:

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```bash
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

Note: `requirements.txt` is intentionally kept minimal for Streamlit Cloud deployment. It includes only the direct dependencies needed to run the app.

### 5. Add environment variable

Create a `.env` file in the root folder:

```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

A sample file is provided as `.env.example`.

### 6. Run the app

```bash
streamlit run app.py
```

Open the local URL shown in the terminal. Usually it is:

```text
http://localhost:8501
```

---

## Deployment

The app is deployed on Streamlit Community Cloud.

Live demo:

```text
https://smart-ticket-triage-agent.streamlit.app/
```

Deployment settings:

```text
Repository: Abhijeet01khot/potens-intern-aiml-abhijeet-khot
Branch: master
Main file path: app.py
```

`requirements.txt` was simplified to direct dependencies only so Streamlit Cloud can resolve packages reliably.

## How the Agent Works

The system follows this flow:

1. User enters a ticket and optional metadata.
2. If a valid Gemini API key is configured, the agent can send the ticket to Gemini for classification.
3. If no API key is configured, the fallback triage mode returns structured JSON with category, priority, confidence, next tool, reasoning, and why.
4. Python executes real callable tools.
5. Tool outputs are attached to the final response.
6. A visible reasoning trace is shown in the UI.
7. If the issue is critical or low-confidence, the human escalation tool is triggered.

---

## Fallback Mode

If the Gemini API key is missing or unavailable, the system still works using a fallback rule-based triage path.

This was added so the reviewer can still test the project even without configuring an API key.

The fallback mode is not the main intelligence layer, but it keeps the demo reliable.

---

## Example Tickets

### Example 1

Input:

```text
My payment was deducted but my order is not showing in the app.
```

Expected:

```json
{
  "category": "billing",
  "priority": "P1"
}
```

### Example 2

Input:

```text
I think my account is hacked and someone changed my email.
```

Expected:

```json
{
  "category": "account",
  "priority": "P0"
}
```

### Example 3

Input:

```text
Can you tell me the available plans and pricing?
```

Expected:

```json
{
  "category": "general",
  "priority": "P2"
}
```

More examples are available in the `/examples` folder.

---

## Baseline Comparison

The project includes a simple baseline classifier in `baseline.py`.

The baseline uses basic keyword checks and does not:

- Call tools
- Produce a full reasoning trace
- Draft acknowledgement messages
- Escalate low-confidence cases

The agentic version is better because it combines model judgment, structured output, tool execution, and visible traceability.

---

## Design Decisions

### 1. Customer support triage domain

I chose customer support ticket triage because it is practical, easy to test, and close to real business workflows.

### 2. Six categories only

I limited the system to six categories so the output remains focused and reliable.

### 3. P0 / P1 / P2 priority scheme

The priority scheme is simple enough for a 24-hour assignment but still reflects real support operations.

### 4. Tool execution outside the LLM

The LLM decides the triage result, but Python functions execute the actual tools.

This avoids fake tool calling and makes the flow easier to audit.

### 5. Fallback mode

A fallback path was added because API keys can fail during review.

The app still runs from a clean clone even without the Gemini API key.

---

## What Works

- Free-text ticket input
- Optional metadata input
- Structured output
- Six-category classification
- P0 / P1 / P2 priority assignment
- Four real callable tools
- Visible reasoning trace
- Streamlit UI
- Streamlit Cloud live demo
- Ten example test inputs
- Fallback mode when Gemini API is unavailable
- Basic baseline comparison

---

## What Is Broken or Unfinished

- The similar ticket search uses simple word overlap instead of embeddings.
- The mock policy database is hardcoded.
- The past ticket database is hardcoded.
- The baseline comparison is implemented in code but not visualised as a full evaluation dashboard.
- The system is not connected to a real CRM, database, or ticketing tool.
- The reasoning trace is a transparent operational trace, not hidden chain-of-thought from the model.
- Gemini API integration is implemented, but the submitted repository does not include a real API key. Reviewers can add their own key in `.env`, or use the fallback mode.
- `requirements.txt` is intentionally minimal for deployment reliability instead of being a full `pip freeze` export.

---

## What I Would Build Next

Given more time, I would add:

1. Embedding-based similar ticket search using FAISS or Chroma.
2. A real database for tickets, policies, and previous resolutions.
3. Authentication for support agents.
4. A dashboard showing baseline vs agent performance on all examples.
5. Human review workflow for P0 and low-confidence tickets.
6. Unit tests for every tool.
7. Export to CSV or JSON for operations teams.
8. More production-ready deployment with authentication, monitoring, and secure secret management.

---

## AI Use Log

### ChatGPT

Approximate usage: 35-45 messages.

Used for:

- Understanding the assignment requirements
- Choosing the AI/ML Q2 Triage Agent problem
- Planning the project structure
- Writing initial code for the Streamlit app, agent flow, callable tools, examples, and README
- Debugging Python setup, Streamlit run issues, Git commands, and GitHub upload
- Improving the README and submission content

### Google Gemini API

Gemini API support is implemented in the code as the optional LLM decision layer.

However, the repository does not include a real API key because `.env` is intentionally ignored for security. If a reviewer adds a valid `GEMINI_API_KEY` in a local `.env` file, the app can call Gemini for structured triage decisions.

For reliability during review, I also implemented a fallback rule-based triage mode. This allows the Streamlit app to run even when no Gemini API key is configured.

### Honesty Note

I used AI assistance heavily for planning, code generation, debugging, and README writing. I reviewed the generated code, tested it locally, committed it to GitHub, and kept the project focused on the assignment requirements.

---

## Author

Abhijeet Khot

Repository name:

```text
potens-intern-aiml-abhijeet-khot
```