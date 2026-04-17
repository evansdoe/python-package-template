# {{ cookiecutter.package_name }}

{{ cookiecutter.package_description }}

{%- if cookiecutter.ci_platform in ["gitlab", "both"] %}

[![pipeline status]({{ cookiecutter.package_url }}/badges/main/pipeline.svg)]({{ cookiecutter.package_url }}/-/pipelines)
[![coverage report]({{ cookiecutter.package_url }}/badges/main/coverage.svg)]({{ cookiecutter.package_url }}/-/commits/main)
{%- endif %}

## Getting Started

### Prerequisites

- Python {{ cookiecutter.python_version }}
- [uv](https://docs.astral.sh/uv/) (recommended)

### Installation

```bash
uv sync --all-extras --all-groups
```
{%- if cookiecutter.include_precommit | string == "True" %}

### Pre-commit Hooks

```bash
# Requires a git repository — run git init first if you haven't already
git init && git add .
uv run pre-commit install
```
{%- endif %}

### Development

```bash
# Format & lint
uv run poe precommit

# Run checks (format, lint, {{ "types, " if cookiecutter.type_checker != "none" else "" }}licenses)
uv run poe check

# Run tests
uv run poe test
```
{%- if cookiecutter.type_checker == "mypy" %}

### Type Checking

This project uses [mypy](https://mypy.readthedocs.io/) for static type analysis.

```bash
uv run poe typecheck
# or directly:
uv run mypy .
```
{%- elif cookiecutter.type_checker == "ty" %}

### Type Checking

This project uses [ty](https://docs.astral.sh/ty/) — Astral's fast type checker (beta).

```bash
uv run poe typecheck
# or directly:
uv run ty check .
```
{%- endif %}
{%- if cookiecutter.include_mkdocs | string == "True" %}

### Documentation

```bash
uv run poe docs
```
{%- endif %}
{%- if cookiecutter.include_cli | string == "True" %}

### CLI

```bash
uv run {{ cookiecutter.__package_name_kebab_case }} --help
```
{%- endif %}
{%- if cookiecutter.include_docker | string == "True" %}

### Docker

```bash
docker build --target runtime -t {{ cookiecutter.__package_name_kebab_case }} .
```
{%- if cookiecutter.ci_platform in ["gitlab", "both"] %}

GitLab CI pushes images to the project's container registry:

- `{{ cookiecutter.gitlab_registry }}/<group>/<project>/{{ cookiecutter.__package_name_snake_case }}/build`
- `{{ cookiecutter.gitlab_registry }}/<group>/<project>/{{ cookiecutter.__package_name_snake_case }}/dev`
- `{{ cookiecutter.gitlab_registry }}/<group>/<project>/{{ cookiecutter.__package_name_snake_case }}/runtime`
{%- endif %}
{%- if cookiecutter.ci_platform in ["github", "both"] %}

GitHub Actions pushes images to GHCR:

- `ghcr.io/<owner>/<repo>/{{ cookiecutter.__package_name_snake_case }}/build`
- `ghcr.io/<owner>/<repo>/{{ cookiecutter.__package_name_snake_case }}/dev`
- `ghcr.io/<owner>/<repo>/{{ cookiecutter.__package_name_snake_case }}/runtime`
{%- endif %}
{%- endif %}
{%- if cookiecutter.include_devcontainer | string == "True" %}

### Development in a DevContainer (Recommended)

The easiest way to get a fully working development environment is via
[VS Code DevContainers](https://code.visualstudio.com/docs/devcontainers/containers).

**Prerequisites:** [Docker](https://www.docker.com/products/docker-desktop/) and
[VS Code](https://code.visualstudio.com/) with the
[Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).

1. Open the project in VS Code:

   ```bash
   cd {{ cookiecutter.__package_name_kebab_case }}
   code .
   ```

2. VS Code will detect the `.devcontainer/` folder and prompt:
   **"Reopen in Container"** — click it (or use **Ctrl+Shift+P** →
   *Dev Containers: Reopen in Container*).

3. The container builds automatically with all dependencies, tools, and
   VS Code extensions pre-installed. Once inside, everything just works:

   ```bash
   poeprecommit     # format + lint
   poecheck         # full quality checks
   poetest          # run tests
   ```

   No need to activate any virtual environment — the container's Python
   is already configured at `/opt/venv` and on the PATH.
{%- endif %}



## Keeping Up to Date

This project was generated from a [Cookiecutter](https://cookiecutter.readthedocs.io/)
template using [Cruft](https://cruft.github.io/cruft/). To pull in template updates:

```bash
# Check if the project is up to date with the template
uv run cruft check

# Update the project from the latest template
uv run cruft update

# If there are merge conflicts, resolve them and delete the .rej files
```

## CI/CD

{%- if cookiecutter.ci_platform == "github" %}
This project uses **GitHub Actions** for CI/CD. Workflows live under `.github/workflows/`.
{%- elif cookiecutter.ci_platform == "gitlab" %}
This project uses **GitLab CI** for CI/CD. Configuration lives in `.gitlab-ci.yml`.
{%- elif cookiecutter.ci_platform == "both" %}
This project is configured for **both** GitHub Actions and GitLab CI. The two pipelines
do the same work (format, lint, {{ "type-check, " if cookiecutter.type_checker != "none" else "" }}test, build, optionally publish) — use whichever platform hosts the repository.

- GitHub Actions: `.github/workflows/`
- GitLab CI: `.gitlab-ci.yml` and `.gitlab/`
{%- endif %}
