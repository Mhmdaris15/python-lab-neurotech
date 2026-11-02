# Local checks and VS Code setup

First install the tools and check an assignment from the terminal. Then configure editor hints and formatting in VS Code.

## 1. Install and run the checks

### Step 1. Install Python

Install [Python 3.14](https://www.python.org/downloads/). Assignments involving memory reading require version 3.14.7.

On Windows, enable **Add python.exe to PATH** when prompted by the installer. Open a new terminal after installation.

### Step 2. Open a terminal in the repository folder

Use the local folder for your course repository. It should contain `requirements.txt`, `pyproject.toml`, and the module folders.

**Windows**

1. Open the repository folder in File Explorer.
2. Enter `cmd` in the address bar and press Enter.
3. Check the Python version:

```bat
python --version
```

**macOS**

1. Open Terminal.
2. Change to the repository folder, replacing the example path with your own:

```bash
cd "/path/to/repository"
```

3. Check the Python version:

```bash
python3 --version
```

The command should show Python 3.14.7. If it is not found or shows an older version, check your Python installation first.

Run all remaining commands from this folder.

### Step 3. Create a virtual environment

A virtual environment keeps libraries separate for this repository. You only need to create it once.

If `.venv` already exists and uses Python 3.14, go to Step 4. If it was created with an older Python version, rename its folder to `.venv-old` and create a new one.

**Windows**

```bat
python -m venv .venv
```

**macOS**

```bash
python3 -m venv .venv
```

### Step 4. Activate the environment

**Windows — in the open cmd window**

```bat
.venv\Scripts\activate.bat
```

**macOS**

```bash
source .venv/bin/activate
```

You will usually see `(.venv)` at the start of the terminal prompt. After activation, use the `python` command on both systems.

In each new terminal, change to the repository folder and activate the environment again. You do not need to recreate it.

### Step 5. Install the tools

1. Upgrade pip, the package installer:

```bash
python -m pip install --upgrade pip
```

2. Install the repository dependencies:

```bash
python -m pip install --upgrade -r requirements.txt
```

This installs:

- **Ruff** — code checking and formatting.
- **mypy** — type checking.
- **pytest** and **pytest-timeout** — running tests with a time limit.

Check settings are already in `pyproject.toml`. The `python -m` form runs each tool using Python from the active environment.

### Step 6. Check your solution

The examples use the first assignment in Module 2. Replace `02_DataStructures/01_Min_To_Drop` with your assignment folder.

1. Format the code. This command changes file formatting:

```bash
python -m ruff format 02_DataStructures/01_Min_To_Drop
```

2. Run the linter:

```bash
python -m ruff check 02_DataStructures/01_Min_To_Drop
```

3. Check types:

```bash
python -m mypy 02_DataStructures/01_Min_To_Drop
```

4. Run tests:

```bash
python -m pytest --timeout=10 -q 02_DataStructures/01_Min_To_Drop
```

If a check reports an error, fix it and run the check again. Run all four commands before submitting. On the server, formatting is checked with `ruff format --check` and types with mypy.

## 2. VS Code setup (optional, but highly recommended)

### Step 1. Open the repository

1. Install [VS Code](https://code.visualstudio.com/) if you do not already have it.
2. Choose **File → Open Folder**.
3. Open the full course repository folder containing `requirements.txt` and `pyproject.toml`.

### Step 2. Install extensions

Open **Extensions** in the sidebar. Find each extension and click **Install**:

1. [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) by Microsoft — environment selection and running Python.
2. [Pyrefly — Python Language Tooling](https://marketplace.visualstudio.com/items?itemName=meta.pyrefly) by Meta — editor hints and type errors.
3. [Ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff) by Astral — linting and formatting.

You do not need to install Pyrefly with pip; it is included in the extension.

If Pylance is installed and enabled, open its page, click the gear icon, and choose **Disable (Workspace)** to avoid duplicate hints.

### Step 3. Select the environment

1. Open the Command Palette: **Ctrl+Shift+P** on Windows or **⌘⇧P** on macOS.
2. Find **Python: Select Interpreter**.
3. Select `.venv` from your repository.

If the environment is not listed, choose **Enter interpreter path** and locate the file inside the repository:

- Windows: `.venv\Scripts\python.exe`.
- macOS: `.venv/bin/python`.

### Step 4. Enable formatting on save

1. Open the Command Palette again.
2. Choose **Preferences: Open Workspace Settings (JSON)**.
3. Add these settings to the opened `.vscode/settings.json` file:

```json
{
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true
    },
    "ruff.importStrategy": "fromEnvironment",
    "python.pyrefly.typeCheckingMode": "default"
}
```

If the file already has settings, add these fields and keep the existing ones. If a `[python]` section already exists, add the formatting settings inside it.

4. Save the file: **Ctrl+S** on Windows or **⌘S** on macOS.

### Step 5. Check the setup

1. Open the Python solution file.
2. Save it. Ruff will format it automatically if needed.
3. Check **View → Problems**. Hover over an underlined error to see details.

Pyrefly provides hints as you work, but it may sometimes assess code differently from mypy. Before submitting, run the checks from Step 6 in Part 1, even if the editor shows no errors.
