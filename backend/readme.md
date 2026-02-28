# Backend Setup

This guide explains how to set up the backend environment using [uv](https://github.com/astral-sh/uv).

## 1. Create a Virtual Environment
Create a virtual environment with a specific Python version (e.g., Python 3.12):
```bash
uv venv --python 3.12
```

## 2. Activate the Environment
Activation depends on your operating system:

**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```powershell
.venv\Scripts\activate
```

## 3. Install Dependencies
Install the required packages from the requirements file:
```bash
uv pip install -r requierements.txt
```

## Automation with Makefile
You can also use the following `make` commands:

- **Setup Everything:** `make setup && make install`
- **Activate Env:** `make activate` (shows the command to run)
- **Run Tests:** `make test` (uses uv run, no manual activation needed)
- **Clean Environment:** `make clean`
- **Help:** `make help`