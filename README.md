# Loan Assistant (Assn2)

Streamlit console that lets loan officers review customer data, quote policy-backed answers, and record final decisions with help from a CrewAI agent.

## Requirements

- Conda (Miniconda/Anaconda) with permission to create environments.
- macOS/Linux/Windows host with Python builds supported by Conda.
- OpenAI API key for the agent (`OPENAI_API_KEY`).

## Installation (via `setup.sh`)

1. Make the script executable once:  
   ```bash
   chmod +x setup.sh
   ```
2. Run the installer (recreates the `loan_env` Conda env each time):  
   ```bash
   ./setup.sh
   ```
3. Activate the environment whenever you work on the project:  
   ```bash
   conda activate loan_env
   ```

### Windows notes

- Run the script from Git Bash or WSL so the shebang and `set -e` behavior are respected:  
  ```bash
  bash setup.sh
  ```
- If you prefer PowerShell, install the free **GnuWin** or **MSYS2** toolchain and invoke `bash setup.sh` from there.
- Ensure `conda init powershell` has been executed at least once so `conda activate loan_env` works in new PowerShell sessions.

What the script handles for you:
- Removes any previous `loan_env` to guarantee a clean slate.
- Creates a Python 3.11.14 Conda environment with up-to-date build tools.
- Installs the required OpenAI SDK, CrewAI stack, LangChain ecosystem, FAISS, ML dependencies, and Streamlit UI packages in the right order.
- Runs `pip check` so dependency issues surface immediately.

## Configuration

Create an `.env` file in the repo root:

```bash
OPENAI_API_KEY=sk-...
# optional
LOAN_AGENT_LOG_PATH=/absolute/path/to/loan_agents.log
```

Drop the latest PDF policy manuals inside `policies/` and populate `data/` with the CSV samples provided in the repo (or your own exports).

## Usage

Start the Streamlit console after activating the environment:

```bash
streamlit run app.py
```

The app will warm the FAISS index for any PDFs in `policies/`, load CSV customer data on demand, and route user questions through the CrewAI agent before displaying the result cards and officer controls.

## Tests

```bash
pytest
```

Use the suite after editing `agents.py`, prompts, or any guardrail logic to ensure the agent contract with the UI stays intact.

## Container usage

Build the CPU-only image (Conda not required inside the container):

```bash
docker build -t loan-assistant .
```

Run it while mounting your policies/data folders and injecting env vars:

```bash
docker run --rm -p 8501:8501 \
  --env-file .env \
  -v "$(pwd)/policies:/app/policies" \
  -v "$(pwd)/data:/app/data" \
  loan-assistant
```

- `--env-file .env` passes `OPENAI_API_KEY` (and optional `LOAN_AGENT_LOG_PATH`) without baking secrets into the image.
- Bind mounts keep your PDFs/CSVs on the host so you can update them without rebuilding.
- Streamlit listens on `0.0.0.0:8501` inside the container; the `-p 8501:8501` mapping lets you visit http://localhost:8501 from the host browser.

If you want to share the prebuilt image instead of the source tree, export/import it:

```bash
# Sender
docker build -t loan-assistant .
docker save loan-assistant | gzip > loan-assistant.tar.gz

# Receiver
docker load < loan-assistant.tar.gz
docker run --rm -p 8501:8501 \
  --env-file .env \
  -v "$(pwd)/policies:/app/policies" \
  -v "$(pwd)/data:/app/data" \
  loan-assistant
```

This keeps the environment identical to what you built while avoiding the need to transfer the full repo.
