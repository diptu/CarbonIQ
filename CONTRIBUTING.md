# 🤝 Contributing Guide

Thanks for taking the time to contribute!
This project follows a **production-ready workflow** with `uv` for dependency management.
Please read the following steps carefully before submitting changes.

---

## 📂 Branching Strategy
- **`main`** → Stable, production-ready code
- **`develop`** → Integration branch (default target for PRs)
- **Feature branches** → `feat/<short-description>`
- **Bugfix branches** → `fix/<short-description>`
- **Hotfix branches** → `hotfix/<version>`

👉 Never commit directly to `main` or `develop`. Always open a Pull Request.

---

## ⚙️ Local Setup

### 1. Install `uv`
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
### 2. Clone the repository
```bash
git clone https://github.com/diptu/CarbonIQ.git
cd CarbonIQ
```
### 3. Install dependencies
```bash
uv sync
```
### 4. Run pre-commit hooks (one-time setup)
```bash
uv run pre-commit install
```

## 🧪 Development Workflow
### Run tests
```bash
uv run pytest
```
### Run linter
```bash
uv run ruff check .
```
### Run type checker
```bash
uv run mypy src
```

### Format code
```bash
uv run black .
```

## 📋 Pull Request Process

### Create a feature/bugfix branch from develop.
```bash
git checkout develop
git pull
git checkout -b feat/add-login
```
### Commit your changes (use conventional commit messages: feat: ..., fix: ..., docs: ...).

### Push your branch:
```bash
git push -u origin feat/add-login
```
### Open a Pull Request → target branch develop.

    #### Ensure:

        ✅ All pre-commit checks pass (pre-commit run --all-files)

        ✅ Tests pass (uv run pytest)

        ✅ CI checks are green
### Wait for at least 1 reviewer approval.

## 🛡️ Commit Message Guidelines

### We use Conventional Commits:

- feat: → new feature

- fix: → bug fix

- docs: → documentation only changes

- refactor: → code change that neither fixes a bug nor adds a feature

- test: → adding missing tests or refactoring tests

#### Example:
```bash
feat(auth): add JWT-based login system
```

## 🐛 Reporting Issues

- Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md)
.

- Include steps to reproduce, logs, and environment details.

## 🚀 Requesting Features

- Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md)

- Explain the motivation and possible solutions.

## ❤️ Code of Conduct

- Please be respectful, collaborative, and constructive.
- We aim to make this project beginner-friendly and professional.
