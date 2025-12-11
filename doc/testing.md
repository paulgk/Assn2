## Testing Overview

This project now includes a lightweight pytest suite that focuses on the parts of the assistant we can validate locally without calling external LLM services.

- **Data integrity** – `tests/test_agents.py` confirms that `load_customer_data` stitches together the CSV slices correctly for both Singaporean and non-Singaporean customers, handles missing customers, and enforces identifier validation.
- **Response normalisation** – Guardrails around policy notes, interest rates, and fallback QA answers are verified through `normalize_loan_response` tests so the Streamlit UI never renders incomplete applications.
- **Parser utilities** – `safe_json_loads` parsing of fenced / single-quoted JSON output is covered to ensure downstream robustness when the LLM deviates slightly from the contract.

## Running the tests

```bash
# install the dependencies listed in README.md (crewai, streamlit, langchain, etc.)
pytest
```

> The test suite automatically stubs optional dependencies (e.g., CrewAI, LangChain community loaders) when they are not available so it can run in constrained environments, but the real packages are used whenever they are installed.
