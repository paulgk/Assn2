# Loan Assistant Architecture

## 1. Context Overview
The system is an internal-facing Streamlit application that routes every user request through a single CrewAI agent. The agent can access two internal tools: customer data lookup (CSV-backed) and a FAISS-powered Retrieval-Augmented Generation (RAG) index over policy PDFs. The agent produces structured JSON that Streamlit renders along with human-review controls.

```mermaid
C4Context
    title Loan Assistant Context
    Person(user,"Loan Officer","Asks loan questions and evaluates applications")
    System(app,"Streamlit Loan Assistant","UI + state management")
    System_Boundary(core,"Backend Services"){
        Container(agents,"agents.py","CrewAI single agent + tools")
        ContainerDb(csv,"CSV Data Lake","credit, account, PR data")
        ContainerDb(rag,"Policy FAISS Index","Embeddings from policy PDFs")
    }
    System_Ext(openai,"OpenAI Chat Completions","LLM powering the agent")

    Rel(user,app,"Submits prompts / approvals")
    Rel(app,agents,"handle_user_input(text)")
    Rel(agents,csv,"load_customer_data()")
    Rel(agents,rag,"PolicyRetriever tool")
    Rel(agents,openai,"CrewAI Agent <> Chat API")
```

## 2. Component Breakdown
| Component | Responsibility | Key Tech |
|-----------|----------------|----------|
| `app.py` | Streamlit UI, session state, approval workflow, stats sidebar, policy evidence display | Streamlit, Python |
| `agents.py` | Data access, FAISS caching, tool registration, unified agent orchestration, standardized error payloads | CrewAI, LangChain, pandas, SentenceTransformerEmbeddings |
| `/data/*.csv` | Source-of-truth tables for credit scores, account status, PR status | CSV, pandas |
| `/policies/*.pdf` | Official lending policies indexed for RAG | PDF + FAISS |
| `/prompts/unified_agent.md` | Behavioral contract for the LLM agent | Markdown prompt |

## 3. Logical Architecture
```mermaid
graph TD
    A[Streamlit UI] -->|text + state| B(handle_user_input)
    B --> C[Validate input]
    C --> D[get_policy_db cache]
    D -->|FAISS handle| E[PolicyRetriever tool]
    B --> F[build_customer_and_policy_tools]
    F --> G[CustomerDataLookup tool]
    B --> H[run_unified_pipeline]
    H --> I[CrewAI Agent]
    I -->|LLM call| J[OpenAI Chat API]
    I -->|tool use| E
    I -->|tool use| G
    H --> K[normalize_loan_response]
    K --> A
```

## 4. Deployment View
- **Runtime**: local Streamlit session (developer laptop or internal VM).
- **Environment variables**: `.env` with `OPENAI_API_KEY`.
- **File dependencies**: expects `./data`, `./policies`, `./prompts`, and `./doc` inside repo root.
- **Network**: outbound HTTPS to OpenAI only (no other external traffic).

## 5. Data Contracts
- Customer tool returns JSON object with `ID`, `Name`, `Nationality`, `AccountStatus`, `CreditScore`, `PRStatus`.
- Unified agent must emit the schema defined in `prompts/unified_agent.md`. Streamlit trusts that structure when rendering.
- UI-level errors always use `{"type": "error", "error": <code>, "message": <details>}` via `error_response`, so the front end can surface consistent warnings.

## 6. Caching Strategy
- `load_prompt` and `_load_customer_tables` are wrapped in `functools.lru_cache` so prompt templates and CSV slices are only read once per process.
- `get_policy_db` memoizes the FAISS vector store in `_POLICY_DB`, preventing repeated PDF parsing as users submit multiple questions.
- Streamlit session state keeps `pending_application`, `officer_*` fields, and `decision_stats` so officer actions survive reruns triggered by widget interaction.

## 7. Observability
- `logging` module prints to stdout and `loan_agents.log` (if configured by the user) with INFO-level events for FAISS caching and policy retrieval errors.

## 8. Future Enhancements
1. Replace CSVs with a relational read replica (PostgreSQL) and add caching/invalidation.
2. Persist officer decisions to a database or audit ledger.
3. Wrap FAISS cache in a background task to pre-build at startup.
