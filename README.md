# Loan Assistant Console

Modern Streamlit UI that wraps a CrewAI-powered loan assistant. The app answers general questions, runs structured customer evaluations, and captures the human loan officer’s final decision with compliance notes. Policy guidance is enforced through a FAISS RAG index built from the PDF policies supplied in `policies/`.

## Features
- **Unified AI pipeline** – A single CrewAI agent with customer lookup and policy-search tools returns structured JSON (`qa`, `loan_application`, or `error`) every time.
- **Officer workflow** – Pending applications surface a detailed summary, AI memo, and require the officer to record an Approve/Reject decision plus justification.
- **Live decision stats** – Sidebar cards track approvals, rejections, totals, and display a green approval-rate bar that updates immediately after each recorded decision.
- **Cached data + prompts** – Customer CSV slices, prompts, and policies load once per session via `lru_cache`, keeping the app snappy while ensuring consistent responses.

## Project Structure
```
Assn2/
├── app.py                 # Streamlit UI + officer workflow
├── agents.py              # CrewAI pipeline, RAG tooling, validation
├── data/                  # CSV slices for credit, account, PR status
├── policies/              # PDF policy manuals indexed for RAG
├── prompts/               # Prompt templates used by the agent
├── tests/                 # Pytest suite covering key helpers
└── doc/                   # Test reports and notes
```

## Requirements
- Python 3.11 (tested) with `pip`
- Valid `OPENAI_API_KEY`
- Local policy PDFs in `policies/` (two sample PDFs provided)

Install dependencies inside your virtual environment:

```bash
pip install streamlit crewai langchain langchain-community langchain-openai sentence-transformers faiss-cpu python-dotenv pytest
```

## Configuration
1. Copy `.env.example` to `.env` (if provided) and add:
   ```
   OPENAI_API_KEY=<your-key>
   ```
2. CSV files in `data/` must include the columns used by `load_customer_data` (`ID`, `Name`, `Email`, `Nationality`, `AccountStatus`, etc.).
3. Place any additional policy PDFs in `policies/`. They will be indexed the next time the app starts.
4. Optional overrides:
   - `LOAN_LLM_MODEL` – model name passed to `ChatOpenAI` (defaults to `gpt-4o-mini`).
   - `LOAN_LLM_TEMPERATURE` – float between 0 and 2 controlling generation temperature (defaults to `0.1`).

> **Note:** Because CSVs, prompts, and policies are cached with `functools.lru_cache`, restart Streamlit after changing those files.

## Running the App
```bash
streamlit run app.py
```
1. Ask a general policy or loan question → the assistant replies in the “Answer” card.
2. Ask for a customer evaluation (by ID or exact name) → the app shows the AI assessment, policy evidence, and memo.
3. Record the officer’s final decision with justification → sidebar stats update immediately.

## Testing
```bash
pytest tests/test_agents.py
```
The suite stubs optional dependencies so core helpers (`load_customer_data`, `safe_json_loads`, `normalize_loan_response`) stay covered even without CrewAI/LangChain installed.

## Troubleshooting
- **“Policy database is unavailable”** – Ensure the `policies/` directory exists and contains at least one PDF, then restart the app.
- **“Required data file missing”** – Confirm the CSV files under `data/` haven’t been moved or renamed.
- **Approval rate stuck** – Decisions only register after the “Record Final Decision” button succeeds with a justification provided.

Feel free to extend the prompts, add new policy documents, or hook in alternative embeddings—just keep the structured JSON contract so the UI continues to function. Happy lending!
