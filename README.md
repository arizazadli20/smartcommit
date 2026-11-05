SmartCommit 🚀

A lightweight, zero-cost CLI tool that uses the Google Gemini API to automatically generate Conventional Git Commit messages based on your staged code changes.

-- Features

- **Zero Server Costs (BYOK):** Uses your personal Gemini API key stored securely in a local configuration file (`~/.smartcommit_config.json`).
- **Conventional Commits:** Generates standardized, clean commit messages (`feat`, `fix`, `chore`, etc.) to maintain a professional Git history.
- **Interactive Terminal UI:** Built with `Typer` and `Rich`, allowing you to review, edit, regenerate, or cancel the AI's suggestion before committing.
- **Fast & Minimal:** Clean Python code designed for speed, readability, and ease of use.

---

-- Tech Stack

- **Language:** Python 3.9+
- **AI Engine:** Google Gemini API (`google-genai`)
- **CLI Framework:** `Typer`
- **Terminal Styling:** `Rich`
- **Version Control Integration:** Native Python `subprocess` module

---

-- Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/smartcommit.git](https://github.com/YOUR_USERNAME/smartcommit.git)
   cd smartcommit

``

2. **Create and activate a virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate

```

3. **Install the dependencies:**
```bash
pip install -r requirements.txt

```

---

## Usage

1. **Stage your code changes:**
```bash
git add .

```

2. **Run SmartCommit:**
```bash
python main.py

```

*(On the first run, the tool will securely ask for your Gemini API key and save it locally).*
3. **Review the interactive prompt:**
The AI will generate a commit message, and you can choose:
* **[A]ccept:** Commits the changes using the generated message.
* **[E]dit:** Lets you manually modify the message before committing.
* **[R]egenerate:** Asks the AI to generate a brand new suggestion.
* **[C]ancel:** Aborts the operation.

---

## Global Alias Setup (Optional)

If you want to run `smartcommit` from *any* project directory on your Mac/Linux machine:

1. Open your Zsh config file:
```bash
nano ~/.zshrc

```

2. Add the alias at the bottom (update paths to match your system):
```bash
alias smartcommit="/path/to/your/smartcommit/venv/bin/python /path/to/your/smartcommit/main.py"

```

3. Save and refresh your terminal:
```bash
source ~/.zshrc

```
Now you can simply type `smartcommit` anywhere!

---

## License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).

```

