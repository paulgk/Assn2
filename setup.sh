#!/usr/bin/env bash
set -e

ENV_NAME="loan_env"
PYTHON_VERSION="3.11.14"

echo "🔄 Removing existing environment (if any)..."
conda deactivate 2>/dev/null || true
conda remove -n "$ENV_NAME" --all -y 2>/dev/null || true

echo "🆕 Creating conda environment: $ENV_NAME (Python $PYTHON_VERSION)"
conda create -n "$ENV_NAME" \
  python="$PYTHON_VERSION" \
  pip=25.3 \
  setuptools=80.9.0 \
  wheel=0.45.1 \
  -y

echo "⚙️ Initializing conda for this shell"
source "$(conda info --base)/etc/profile.d/conda.sh"

echo "🚀 Activating environment"
conda activate "$ENV_NAME"

echo "⬆️ Upgrading pip tooling"
pip install --upgrade pip setuptools wheel

# -------------------------------------------------------------------
# 1️⃣ Core SDK FIRST (everything depends on this)
# -------------------------------------------------------------------
echo "🔑 Installing OpenAI SDK first"
pip install openai==1.83.0

# -------------------------------------------------------------------
# 2️⃣ Direct OpenAI dependents
# -------------------------------------------------------------------
echo "🧠 Installing Instructor + LangChain OpenAI"
pip install \
  instructor==1.12.0 \
  langchain-openai==1.1.1

# -------------------------------------------------------------------
# 3️⃣ LangChain core stack
# -------------------------------------------------------------------
echo "🔗 Installing LangChain core"
pip install \
  langchain==1.1.3 \
  langchain-core==1.1.3 \
  langchain-community==0.4.1 \
  langchain-text-splitters==1.0.0 \
  langsmith==0.4.59 \
  langgraph==1.0.4

# -------------------------------------------------------------------
# 4️⃣ CrewAI (depends on OpenAI + Instructor)
# -------------------------------------------------------------------
echo "🤖 Installing CrewAI"
pip install crewai==1.7.0

# -------------------------------------------------------------------
# 5️⃣ ML stack (Torch → Transformers → Sentence-Transformers → FAISS)
# -------------------------------------------------------------------
echo "🧬 Installing ML stack"
pip install \
  torch==2.9.1 \
  transformers==4.46.3 \
  sentence-transformers==5.1.2 \
  faiss-cpu==1.13.1 \
  scikit-learn==1.8.0 \
  scipy==1.16.3 \
  numpy==2.3.5

# -------------------------------------------------------------------
# 6️⃣ Storage, vector DB, infra
# -------------------------------------------------------------------
echo "🗄️ Installing storage & infra"
pip install \
  chromadb==1.1.1 \
  onnxruntime==1.23.2 \
  kubernetes==34.1.0 \
  diskcache==5.6.3 \
  aiosqlite==0.21.0

# -------------------------------------------------------------------
# 7️⃣ Telemetry
# -------------------------------------------------------------------
echo "📡 Installing telemetry"
pip install \
  opentelemetry-api==1.34.1 \
  opentelemetry-sdk==1.34.1 \
  opentelemetry-semantic-conventions==0.55b1 \
  grpcio==1.76.0 \
  google-auth==2.43.0 \
  googleapis-common-protos==1.72.0

# -------------------------------------------------------------------
# 8️⃣ Streamlit + UI
# -------------------------------------------------------------------
echo "🎨 Installing UI stack"
pip install \
  streamlit==1.52.1 \
  altair==6.0.0 \
  pydeck==0.9.1 \
  blinker==1.9.0 \
  watchdog==6.0.0 \
  tornado==6.5.3

# -------------------------------------------------------------------
# 9️⃣ Remaining utilities
# -------------------------------------------------------------------
echo "🧩 Installing remaining utilities"
pip install \
  aiohappyeyeballs==2.6.1 \
  aiohttp==3.13.2 \
  aiosignal==1.4.0 \
  anyio==4.12.0 \
  appdirs==1.4.4 \
  attrs==25.4.0 \
  backoff==2.2.1 \
  bcrypt==5.0.0 \
  build==1.3.0 \
  cachetools==6.2.2 \
  certifi==2025.11.12 \
  cffi==2.0.0 \
  cfgv==3.5.0 \
  charset-normalizer==3.4.4 \
  click==8.1.8 \
  colorama==0.4.6 \
  coloredlogs==15.0.1 \
  cryptography==46.0.3 \
  dataclasses-json==0.6.7 \
  distlib==0.4.0 \
  distro==1.9.0 \
  docstring-parser==0.17.0 \
  durationpy==0.10 \
  filelock==3.20.0 \
  flatbuffers==25.9.23 \
  frozenlist==1.8.0 \
  fsspec==2025.12.0 \
  gitdb==4.0.12 \
  gitpython==3.1.45 \
  greenlet==3.3.0 \
  h11==0.16.0 \
  httpcore==1.0.9 \
  httptools==0.7.1 \
  httpx==0.28.1 \
  httpx-sse==0.4.3 \
  huggingface-hub==0.36.0 \
  humanfriendly==10.0 \
  identify==2.6.15 \
  idna==3.11 \
  importlib-metadata==8.7.0 \
  importlib-resources==6.5.2 \
  jinja2==3.1.6 \
  jiter==0.10.0 \
  joblib==1.5.2 \
  json-repair==0.25.3 \
  json5==0.10.0 \
  jsonpatch==1.33 \
  jsonpointer==3.0.0 \
  jsonref==1.1.0 \
  jsonschema==4.25.1 \
  marshmallow==3.26.1 \
  pandas==2.3.3 \
  pillow==12.0.0 \
  protobuf==5.29.5 \
  pyarrow==22.0.0 \
  pydantic==2.11.10 \
  pydantic-settings==2.10.1 \
  pypdf\
  pyyaml==6.0.3 \
  regex==2024.9.11 \
  requests==2.32.5 \
  rich==14.2.0 \
  sqlalchemy==2.0.45 \
  tenacity==9.1.2 \
  tiktoken==0.12.0 \
  tokenizers==0.20.3 \
  typing-extensions==4.15.0 \
  uvicorn==0.38.0 \
  websockets==15.0.1 \
  xxhash==3.6.0 \
  yarl==1.22.0 \
  zstandard==0.25.0

# -------------------------------------------------------------------
# Verification
# -------------------------------------------------------------------
echo "🧪 Running verification"
pip check || true

echo "🎉 Environment recreated successfully"
echo "👉 Activate with: conda activate $ENV_NAME"
