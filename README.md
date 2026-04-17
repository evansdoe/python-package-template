# 🐍 Python Package Template (uv + Monorepo Ready)

[![Cruft](https://img.shields.io/badge/cruft-enabled-blue)](https://cruft.github.io/cruft/)
[![uv](https://img.shields.io/badge/uv-enabled-brightgreen)](https://github.com/astral-sh/uv)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Checked with ty](https://img.shields.io/badge/type%20checker-mypy%20%7C%20ty-blue)](https://docs.astral.sh/ty/)

A modern, production-ready [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for Python projects.

**Why another Python template?** Most templates assume you're building a standalone package on a single CI platform. This one is built for how teams actually work:

1. **`uv`-First:** Lightning-fast dependency management using Astral's `uv` and `hatchling` build backend.
2. **Unified CI Architecture:** Generate pipelines for **GitHub Actions**, **GitLab CI**, or **both** from a single template. Your Python code stays identical — only the CI syntax changes.
3. **Monorepo Support:** Built-in support for subprojects under `src/` with parent-child CI pipelines that only trigger when relevant files change.

---

## ✨ Features

- **⚡ Fast by Default:** `uv` for dependency management, `hatchling` for builds, `ruff` for linting.
- **🛠️ Developer Experience:** Fully configured VS Code DevContainers with extensions (Copilot, Jupyter, Ruff, Claude Code) and a `poethepoet` task runner (`poe check`, `poe test`).
- **🛡️ Code Quality:** Pre-commit hooks with `ruff`, `black`, and `isort`. Choose between `mypy` (stable) or `ty` (Astral, fast, beta) for type checking — or skip type checking entirely.
- **🐳 GPU-Aware Docker:** Multi-stage builds (build → runtime → dev) with dynamic NVIDIA CUDA base image selection, `shm_size`, and GPU deploy blocks in `docker-compose.yml`.
- **🔒 Enterprise Ready:** License auditing via `liccheck`, SAST scanning (CodeQL for GitHub, native templates for GitLab), secret detection, and dependency vulnerability scanning.
- **📚 Documentation:** MkDocs Material site with auto-generated API docs, deployed to GitHub Pages or GitLab Pages on merge to `main`.
- **📦 Publishing:** PyPI trusted publishing (GitHub) or GitLab Package Registry publishing on version tags.
- **🔄 Template Updates:** Cruft integration with a non-blocking "template drift" CI check, so teams know when upstream improvements are available.

---

## 🚀 Quickstart

We recommend [Cruft](https://cruft.github.io/cruft/) over plain Cookiecutter. Cruft records which template version your project was generated from, letting you pull in improvements later with `cruft update`.

### 1. Generate the project

```bash
pip install cruft
cruft create https://github.com/evansdoe/python-package-template
```

You'll be prompted for project name, CI platform, GPU support, type checker, and other options.

**Platform shortcuts** — skip the interactive prompt if you already know what you need:

```bash
# GitHub Actions (default — just press Enter at the ci_platform prompt)
cruft create https://github.com/evansdoe/python-package-template

# GitLab CI
cruft create https://github.com/evansdoe/python-package-template --no-input ci_platform=gitlab

# Both platforms
cruft create https://github.com/evansdoe/python-package-template --no-input ci_platform=both
```

<details>
<summary>Alternative: plain Cookiecutter (no template update support)</summary>

```bash
pip install cookiecutter
cookiecutter https://github.com/evansdoe/python-package-template
```

Note: projects generated with plain cookiecutter won't have a `.cruft.json`
file, so `cruft update` won't work later.

</details>

### 2. Install dependencies

```bash
cd your-new-project
uv sync --all-extras --all-groups
```

### 3. Start developing

```bash
# Install pre-commit hooks
uv run pre-commit install

# Format and lint
uv run poe precommit

# Run all checks (format, lint, types, licenses)
uv run poe check

# Run tests
uv run poe test
```

---

## 🏗️ What does it generate?

<details>
<summary>Click to expand the generated directory tree</summary>

```
my-package/
├── my_package/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py                       ← optional (include_cli)
│   └── py.typed                     ← optional (type_checker != none)
├── tests/
│   └── test__example.py
├── docs/                            ← optional (include_mkdocs)
│   ├── index.md
│   └── reference.md
├── .devcontainer/                   ← optional (include_devcontainer)
│   ├── devcontainer.json
│   ├── docker-compose.yml           ← GPU blocks added dynamically
│   ├── .env
│   └── .env-secrets.example
├── .github/                         ← if ci_platform is github or both
│   ├── workflows/
│   │   ├── ci.yml                   ← orchestrator (subproject) or full pipeline (standalone)
│   │   ├── my-package.yml           ← reusable workflow (subproject only)
│   │   ├── publish.yml              ← PyPI publishing on tag push
│   │   └── docs.yml                 ← GitHub Pages deployment
│   ├── dependabot.yml
│   ├── CODEOWNERS
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
├── .gitlab-ci.yml                   ← if ci_platform is gitlab or both
├── .gitlab-ci.root.yml              ← orchestrator for subprojects (move to monorepo root)
├── .gitlab/                         ← if ci_platform is gitlab or both
│   ├── issue_templates/
│   └── merge_request_templates/
├── CODEOWNERS                       ← GitLab version (at repo root)
├── Dockerfile                       ← optional (include_docker)
├── .pre-commit-config.yaml          ← optional (include_precommit)
├── pyproject.toml
├── mkdocs.yml                       ← optional (include_mkdocs)
├── .python-version
├── .env.example
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── README.md
├── .gitignore
├── .editorconfig
└── .dockerignore                    ← optional (include_docker)
```

</details>

---

## ⚙️ Parameters

| Parameter | Default | Description |
|---|---|---|
| `package_name` | `My Package` | Human-readable project name |
| `package_description` | — | Short description |
| `is_subproject` | `true` | Monorepo subproject under `src/`, or standalone repo |
| `include_gpu` | `false` | NVIDIA CUDA base image + GPU docker-compose config |
| `package_url` | — | Repository URL |
| `author_name` / `author_email` | — | Author identity |
| `python_version` | `3.13` | Python version (pinned in `.python-version` too) |
| `uv_version` | `0.6.12` | uv version for CI |
| `timezone` | `Europe/Vienna` | Timezone for Docker dev container |
| `docstring_style` | `google` | `google` or `numpy` |
| `open_source_license` | `MIT` | `MIT`, `Apache-2.0`, `BSD-3-Clause`, or `Proprietary` |
| `type_checker` | `mypy` | `mypy` (stable), `ty` (Astral, beta), or `none` |
| `ci_platform` | `github` | `github`, `gitlab`, or `both` |
| `gitlab_registry` | `registry.gitlab.com` | Container registry hostname (GitLab) |
| `include_docker` | `true` | Dockerfile + .dockerignore |
| `include_devcontainer` | `true` | VS Code DevContainer |
| `include_mkdocs` | `true` | MkDocs documentation + Pages deployment |
| `include_precommit` | `true` | Pre-commit hooks |
| `include_cli` | `false` | Typer CLI entry point |
| `include_security_scans` | `true` | GitLab SAST / Secret Detection / Dependency Scanning |
| `include_pypi_publish` | `true` | Publish workflow on tag push |

---

## 🔀 How `is_subproject` works

| Aspect | `is_subproject: true` | `is_subproject: false` |
|---|---|---|
| Project location | Under `src/<name>/` in a monorepo | At the repo root |
| Docker volume mount | `../../../:/workspace` | `../:/workspace` |
| **GitHub CI** | `ci.yml` orchestrator with `dorny/paths-filter` → `<module>.yml` reusable workflow | Single `ci.yml` with all jobs inline |
| **GitLab CI** | `.gitlab-ci.root.yml` orchestrator with `trigger:` + `rules: changes:` → child pipeline | Single `.gitlab-ci.yml` at root |
| CI working directory | `src/<name>` | `.` |

---

## 🔄 Updating your project

Because you used Cruft, your project remembers where it came from:

```bash
# Check if the template has been updated
uv run cruft check

# Pull in template improvements interactively
uv run cruft update

# Resolve any .rej files, then commit
```

A non-blocking `cruft-check` job runs in CI to notify you when the project has drifted from the template.

---

## 📋 Poe Tasks

| Task | Description |
|---|---|
| `poe precommit` | Auto-format, sort imports, fix lint issues |
| `poe check` | Verify format, imports, lint, types, licenses |
| `poe test` | Run pytest with coverage |
| `poe typecheck` | Run type checking (mypy or ty) |
| `poe docs` | Serve documentation locally |
| `poe check_licenses` | Export requirements and audit licenses |

---

## 🤝 Contributing

Want to add a feature, fix a bug, or support a new CI platform? See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

This template is released under the [MIT License](LICENSE).
