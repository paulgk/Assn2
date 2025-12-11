import os
import sys
import types
from copy import deepcopy

import pytest


def _ensure_module(fullname: str):
    """Ensure a module (and its parents) exist so we can attach stubs."""
    module = sys.modules.get(fullname)
    if module:
        return module
    module = types.ModuleType(fullname)
    sys.modules[fullname] = module
    if "." in fullname:
        parent_name, child_name = fullname.rsplit(".", 1)
        parent = _ensure_module(parent_name)
        setattr(parent, child_name, module)
    return module


try:  # pragma: no cover - only executes when optional deps are missing
    import crewai  # type: ignore  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover - fallback stub
    crewai = _ensure_module("crewai")

    class Agent:  # noqa: D401 - simple stub
        """Stub Agent used only for import time."""

        def __init__(self, *args, **kwargs):
            pass

    class Task:
        def __init__(self, *args, **kwargs):
            pass

    class Crew:
        def __init__(self, *args, **kwargs):
            self.tasks_output = [types.SimpleNamespace(raw="{}")]

        def kickoff(self):
            return self

    crewai.Agent = Agent
    crewai.Task = Task
    crewai.Crew = Crew

    tools_mod = _ensure_module("crewai.tools")

    def tool(name):  # noqa: D401 - simple stub decorator
        def decorator(func):
            return func

        return decorator

    tools_mod.tool = tool


def _stub_langchain():  # pragma: no cover - import-time helper
    loaders = _ensure_module("langchain_community.document_loaders")
    embeddings = _ensure_module("langchain_community.embeddings")
    vectorstores = _ensure_module("langchain_community.vectorstores")
    splitters = _ensure_module("langchain_text_splitters")

    class PyPDFLoader:
        def __init__(self, path):
            self.path = path

        def load(self):
            return []

    class SentenceTransformerEmbeddings:
        def __init__(self, *args, **kwargs):
            pass

    class FAISS:
        def __init__(self):
            self.docs = []

        @classmethod
        def from_documents(cls, docs, embedding):
            instance = cls()
            instance.docs = list(docs)
            return instance

        def similarity_search(self, query, k=5):
            return []

    class RecursiveCharacterTextSplitter:
        def __init__(self, *args, **kwargs):
            pass

        def split_documents(self, docs):
            return docs

    loaders.PyPDFLoader = PyPDFLoader
    embeddings.SentenceTransformerEmbeddings = SentenceTransformerEmbeddings
    vectorstores.FAISS = FAISS
    splitters.RecursiveCharacterTextSplitter = RecursiveCharacterTextSplitter


try:  # pragma: no cover - prefer real library when available
    import langchain_community  # type: ignore  # noqa: F401
    import langchain_text_splitters  # type: ignore  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover - fallback stub
    _stub_langchain()


os.environ.setdefault("OPENAI_API_KEY", "test-key")

from agents import load_customer_data, normalize_loan_response, safe_json_loads  # noqa: E402


def test_load_customer_data_by_id_for_singaporean():
    customer = load_customer_data("1111")
    assert customer["Name"] == "Loren"
    assert customer["Nationality"] == "Singaporean"
    assert customer["PRStatus"] == "Not Required"
    assert customer["CreditScore"] == 455


def test_load_customer_data_by_id_for_non_singaporean():
    customer = load_customer_data("2222")
    assert customer["Name"] == "Matt"
    assert customer["Nationality"] == "Non-Singaporean"
    assert customer["PRStatus"] == "True"


def test_load_customer_data_returns_none_for_missing_customer():
    assert load_customer_data("9999") is None


def test_load_customer_data_requires_identifier():
    result = load_customer_data("")
    assert result["error"] == "Customer identifier cannot be empty."


def test_safe_json_loads_handles_code_fences():
    wrapped = """```json
    {"type": "qa", "answer": "Hello"}
    ```"""
    parsed = safe_json_loads(wrapped)
    assert parsed == {"type": "qa", "answer": "Hello"}


def test_safe_json_loads_fallback_single_quotes():
    parsed = safe_json_loads("{'type': 'qa', 'answer': 'Hi'}")
    assert parsed == {"type": "qa", "answer": "Hi"}


@pytest.fixture
def base_payload():
    return {
        "type": "loan_application",
        "customer": {
            "id": "1234",
            "name": "Casey",
            "nationality": "Singaporean",
            "pr_status": "Not Required",
            "account_status": "good standing",
            "credit_score": 720,
        },
        "ai_assessment": {
            "risk": "Low",
            "ai_recommendation": "Approve",
            "interest_rate": "3.2%",
            "policy_notes": "Clause 4.2 satisfied",
            "pr_status_used": "Not Required",
        },
        "letter": "All conditions satisfied.",
    }


def test_normalize_loan_response_returns_structured_payload(base_payload):
    normalized = normalize_loan_response(deepcopy(base_payload))
    assert normalized["type"] == "loan_application"
    assert normalized["customer"]["name"] == "Casey"
    assert normalized["ai_assessment"]["risk"] == "Low"


def test_normalize_loan_response_enforces_policy_notes(base_payload):
    payload = deepcopy(base_payload)
    payload["ai_assessment"]["policy_notes"] = ""
    result = normalize_loan_response(payload)
    assert result["type"] == "error"
    assert result["error"] == "policy_evidence_missing"


def test_normalize_loan_response_enforces_interest_rate(base_payload):
    payload = deepcopy(base_payload)
    payload["ai_assessment"]["interest_rate"] = "Unknown"
    result = normalize_loan_response(payload)
    assert result["type"] == "error"
    assert result["error"] == "interest_rate_missing"


def test_normalize_loan_response_default_answer():
    result = normalize_loan_response({"type": "qa"})
    assert result["type"] == "qa"
    assert "I don't have the necessary information" in result["answer"]


def test_normalize_loan_response_propogates_error_type():
    result = normalize_loan_response({"type": "error", "error": "boom", "message": "fail"})
    assert result == {"type": "error", "error": "boom", "message": "fail"}
