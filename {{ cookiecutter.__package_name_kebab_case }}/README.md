# {{ cookiecutter.package_name }}

{{ cookiecutter.package_description }}

{%- if cookiecutter.ci_platform in ["gitlab", "both"] %}

[![pipeline status]({{ cookiecutter.package_url }}/badges/main/pipeline.svg)]({{ cookiecutter.package_url }}/-/pipelines)
[![coverage report]({{ cookiecutter.package_url }}/badges/main/coverage.svg)]({{ cookiecutter.package_url }}/-/commits/main)
{%- endif %}

---

## Quick Setup
{%- if cookiecutter.is_subproject | string == "True" %}

This project is a **subproject** designed to live under `src/` in a monorepo.

### 1. Place the project in your monorepo

```bash
# Move into your monorepo's src/ directory (if not already there)
mv {{ cookiecutter.__package_name_kebab_case }} <monorepo>/src/
cd <monorepo>
```

### 2. Wire up CI
{%- if cookiecutter.ci_platform in ["github", "both"] %}

**GitHub Actions:**

<details>
<summary><strong>First subproject</strong> (monorepo has no <code>.github/workflows/ci.yml</code> yet)</summary>

```bash
mkdir -p .github/workflows
cp src/{{ cookiecutter.__package_name_kebab_case }}/.github/workflows/ci.yml .github/workflows/ci.yml
cp src/{{ cookiecutter.__package_name_kebab_case }}/.github/workflows/{{ cookiecutter.__package_name_kebab_case }}.yml .github/workflows/
```

</details>

<details>
<summary><strong>Additional subproject</strong> (<code>.github/workflows/ci.yml</code> already exists)</summary>

Open `src/{{ cookiecutter.__package_name_kebab_case }}/.github/workflows/ci.yml` and copy these
three pieces into your existing `<monorepo>/.github/workflows/ci.yml`:

1. The **output** line from the `changes` job's `outputs:` section
2. The **path filter** entry from the `filters:` block
3. The **trigger job** block (`{{ cookiecutter.__package_name_kebab_case }}: ...`)

Then copy the module workflow (no merging needed — it's a new file):

```bash
cp src/{{ cookiecutter.__package_name_kebab_case }}/.github/workflows/{{ cookiecutter.__package_name_kebab_case }}.yml .github/workflows/
```

The existing `ci.yml` has commented examples showing exactly where to paste each piece.

</details>
{%- endif %}
{%- if cookiecutter.ci_platform in ["gitlab", "both"] %}

**GitLab CI:**

<details>
<summary><strong>First subproject</strong> (no <code>.gitlab-ci.yml</code> at monorepo root yet)</summary>

```bash
mv src/{{ cookiecutter.__package_name_kebab_case }}/.gitlab-ci.root.yml .gitlab-ci.yml
mv src/{{ cookiecutter.__package_name_kebab_case }}/CODEOWNERS .
```

</details>

<details>
<summary><strong>Additional subproject</strong> (<code>.gitlab-ci.yml</code> already exists)</summary>

Copy the `trigger-{{ cookiecutter.__package_name_kebab_case }}` job from
`src/{{ cookiecutter.__package_name_kebab_case }}/.gitlab-ci.root.yml` into your existing
`<monorepo>/.gitlab-ci.yml`. The file has a commented example showing
exactly where to paste it.

Then clean up:

```bash
rm src/{{ cookiecutter.__package_name_kebab_case }}/.gitlab-ci.root.yml
```

Merge the `{{ cookiecutter.__package_name_kebab_case }}` entry from
`src/{{ cookiecutter.__package_name_kebab_case }}/CODEOWNERS` into your existing
`<monorepo>/CODEOWNERS`, then:

```bash
rm src/{{ cookiecutter.__package_name_kebab_case }}/CODEOWNERS
```

</details>
{%- endif %}

### 3. Install dependencies

```bash
cd src/{{ cookiecutter.__package_name_kebab_case }}
uv sync --all-extras --all-groups
```
{%- if cookiecutter.include_precommit | string == "True" %}

### 4. Install pre-commit hooks

```bash
# From the monorepo root
cd ../..
uv run --directory src/{{ cookiecutter.__package_name_kebab_case }} pre-commit install
```
{%- endif %}

### {{ "5" if cookiecutter.include_precommit | string == "True" else "4" }}. Verify everything works

```bash
cd src/{{ cookiecutter.__package_name_kebab_case }}
uv run poe check
uv run poe test
```

{%- else %}

### 1. Initialize git and install dependencies

```bash
cd {{ cookiecutter.__package_name_kebab_case }}
git init && git add . && git commit -m "Initial commit"
uv sync --all-extras --all-groups
```
{%- if cookiecutter.include_precommit | string == "True" %}

### 2. Install pre-commit hooks

```bash
uv run pre-commit install
```
{%- endif %}

### {{ "3" if cookiecutter.include_precommit | string == "True" else "2" }}. Verify everything works

```bash
uv run poe check
uv run poe test
```
{%- endif %}

---

## Prerequisites

- Python {{ cookiecutter.python_version }}
- [uv](https://docs.astral.sh/uv/)
{%- if cookiecutter.include_devcontainer | string == "True" %}
- [Docker](https://www.docker.com/products/docker-desktop/) (for DevContainer)
- [VS Code](https://code.visualstudio.com/) with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) (recommended)
{%- endif %}
{%- if cookiecutter.include_devcontainer | string == "True" %}

---

## Development in a DevContainer (Recommended)

The easiest way to get a fully working development environment — no manual
Python/uv/dependency setup needed.

1. Open the project in VS Code:

   ```bash
   {%- if cookiecutter.is_subproject | string == "True" %}
   cd <monorepo>/src/{{ cookiecutter.__package_name_kebab_case }}
   {%- else %}
   cd {{ cookiecutter.__package_name_kebab_case }}
   {%- endif %}
   code .
   ```

2. VS Code detects `.devcontainer/` and prompts **"Reopen in Container"** —
   click it (or **Ctrl+Shift+P** → *Dev Containers: Reopen in Container*).

3. The container builds automatically with all dependencies, tools, and
   VS Code extensions pre-installed. Once inside:

   ```bash
   poeprecommit     # format + lint
   poecheck         # full quality checks
   poetest          # run tests
   ```

   No need to activate any virtual environment — Python is pre-configured
   at `/opt/venv` and on the PATH.
{%- endif %}

---

## Development Commands

| Command | Description |
|---|---|
| `uv run poe precommit` | Auto-format (black), sort imports (isort), lint (ruff) |
| `uv run poe check` | Verify format, imports, lint{{ ", types" if cookiecutter.type_checker != "none" else "" }}, and licenses |
| `uv run poe test` | Run pytest with coverage |
{%- if cookiecutter.type_checker != "none" %}
| `uv run poe typecheck` | Run {{ cookiecutter.type_checker }} type checker |
{%- endif %}
{%- if cookiecutter.include_mkdocs | string == "True" %}
| `uv run poe docs` | Serve MkDocs documentation locally |
{%- endif %}
{%- if cookiecutter.include_cli | string == "True" %}
| `uv run {{ cookiecutter.__package_name_kebab_case }} --help` | Run the CLI |
{%- endif %}

Inside a DevContainer, the shorter aliases also work: `poeprecommit`, `poecheck`, `poetest`.
{%- if cookiecutter.type_checker != "none" %}

---

## Type Checking
{%- if cookiecutter.type_checker == "mypy" %}

This project uses [mypy](https://mypy.readthedocs.io/) for static type analysis.
Configuration is in `pyproject.toml` under `[tool.mypy]`.

```bash
uv run poe typecheck    # or: uv run mypy .
```
{%- elif cookiecutter.type_checker == "ty" %}

This project uses [ty](https://docs.astral.sh/ty/) — Astral's fast type checker (beta).
Configuration is in `pyproject.toml` under `[tool.ty]`.

```bash
uv run poe typecheck    # or: uv run ty check .
```
{%- endif %}
{%- endif %}
{%- if cookiecutter.include_docker | string == "True" %}

---

## Docker

Multi-stage Dockerfile with three targets: `build`, `dev`, and `runtime`.

```bash
# Build the production image
docker build --target runtime -t {{ cookiecutter.__package_name_kebab_case }} .

# Build the dev image (includes all dev tools)
docker build --target dev -t {{ cookiecutter.__package_name_kebab_case }}-dev .
```
{%- if cookiecutter.accelerator == "cuda" %}

This project is configured for **NVIDIA CUDA** GPU support. The Dockerfile
uses `nvidia/cuda:12.4.1-runtime-ubuntu22.04` as the base image and
`docker-compose.yml` includes the NVIDIA deploy block.
{%- elif cookiecutter.accelerator == "rocm" %}

This project is configured for **AMD ROCm** GPU support. The Dockerfile
uses `rocm/dev-ubuntu-22.04:6.2` as the base image and `docker-compose.yml`
passes through `/dev/kfd` and `/dev/dri`.
{%- elif cookiecutter.accelerator == "mps" %}

This project targets **Apple MPS** (Metal Performance Shaders). GPU acceleration
works natively on macOS via `device="mps"` in PyTorch — not via Docker.
The Docker images are CPU-only for portability.
{%- elif cookiecutter.accelerator == "tpu" %}

This project targets **Google Cloud TPU** via PyTorch/XLA. TPU access is at
the VM level, not through Docker GPU passthrough. The Docker images are CPU-only.
{%- endif %}
{%- if cookiecutter.ci_platform in ["gitlab", "both"] %}

**GitLab CI** builds and pushes images to the project's container registry automatically.
{%- endif %}
{%- if cookiecutter.ci_platform in ["github", "both"] %}

**GitHub Actions** builds and pushes images to GHCR automatically.
{%- endif %}
{%- endif %}
{%- if cookiecutter.include_mkdocs | string == "True" %}

---

## Documentation

```bash
uv run poe docs
```

Opens a local MkDocs Material site at `http://127.0.0.1:8000`.
API reference is auto-generated from docstrings ({{ cookiecutter.docstring_style }} style).
{%- if cookiecutter.ci_platform in ["github", "both"] %}
Documentation is deployed to **GitHub Pages** on push to `main`.
{%- endif %}
{%- if cookiecutter.ci_platform in ["gitlab", "both"] %}
Documentation is deployed to **GitLab Pages** on push to the default branch.
{%- endif %}
{%- endif %}

---

## Keeping Up to Date

This project was generated from a [Cookiecutter](https://cookiecutter.readthedocs.io/)
template using [Cruft](https://cruft.github.io/cruft/). When the template is
updated with improvements or fixes, you can pull them in:

```bash
uv run cruft check       # check if the template has changed
uv run cruft update      # apply changes interactively
```

If there are merge conflicts, resolve them and delete any `.rej` files.
{%- if cookiecutter.ci_platform != "none" %}
A non-blocking `cruft-check` CI job will notify you when the project has
drifted from the template.
{%- endif %}

---

## Project Structure

```
{{ cookiecutter.__package_name_kebab_case }}/
├── {{ cookiecutter.__package_name_snake_case }}/     # Python package
│   ├── __init__.py
│   ├── main.py
{%- if cookiecutter.include_cli | string == "True" %}
│   ├── cli.py              # Typer CLI entry point
{%- endif %}
{%- if cookiecutter.type_checker != "none" %}
│   └── py.typed            # PEP 561 type marker
{%- endif %}
├── tests/                   # pytest tests
│   └── test__example.py
{%- if cookiecutter.include_mkdocs | string == "True" %}
├── docs/                    # MkDocs source
{%- endif %}
{%- if cookiecutter.include_devcontainer | string == "True" %}
├── .devcontainer/           # VS Code DevContainer config
{%- endif %}
{%- if cookiecutter.include_docker | string == "True" %}
├── Dockerfile               # Multi-stage build
{%- endif %}
├── pyproject.toml           # Project config (uv, hatchling, poe tasks, tools)
{%- if cookiecutter.include_precommit | string == "True" %}
├── .pre-commit-config.yaml  # Pre-commit hooks
{%- endif %}
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.md
```

---

## CI/CD
{%- if cookiecutter.ci_platform == "github" %}

This project uses **GitHub Actions**. Workflows live under `.github/workflows/`:

| Workflow | Trigger | What it does |
|---|---|---|
| `ci.yml` | Push, PR | Format, lint{{ ", typecheck" if cookiecutter.type_checker != "none" else "" }}, test, license check, Docker builds |
{%- if cookiecutter.include_pypi_publish | string == "True" %}
| `publish.yml` | Tag `v*` | Build and publish to PyPI |
{%- endif %}
{%- if cookiecutter.include_mkdocs | string == "True" %}
| `docs.yml` | Push to main | Deploy docs to GitHub Pages |
{%- endif %}
{%- elif cookiecutter.ci_platform == "gitlab" %}

This project uses **GitLab CI**. Configuration:
{%- if cookiecutter.is_subproject | string == "True" %}

| File | Purpose |
|---|---|
| `.gitlab-ci.yml` | Child pipeline (SAST, test, build, publish) — stays with this subproject |
| `.gitlab-ci.root.yml` | Root orchestrator — move to monorepo root as `.gitlab-ci.yml` |
{%- else %}

| File | Purpose |
|---|---|
| `.gitlab-ci.yml` | Full pipeline (SAST, test, build, publish) |
{%- endif %}
{%- elif cookiecutter.ci_platform == "both" %}

This project supports **both** GitHub Actions and GitLab CI.
The two pipelines do the same work — use whichever platform hosts the repository.

| Platform | Config |
|---|---|
| GitHub Actions | `.github/workflows/` |
| GitLab CI | `.gitlab-ci.yml` + `.gitlab/` |
{%- endif %}

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development workflow, branching
strategy, and how to submit changes.
