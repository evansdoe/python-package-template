# Contributing to the Python Package Template

Thank you for your interest in improving this template! This document explains
how to work on the template's Jinja logic, add new features, and test your
changes before opening a PR.

## Setup

```bash
git clone https://github.com/evansdoe/python-package-template.git
cd python-package-template
uv sync --all-extras --all-groups
```

## How the template works

The template is a standard [Cookiecutter](https://cookiecutter.readthedocs.io/)
project. All user-facing parameters are defined in `cookiecutter.json`. The
directory named `{{ cookiecutter.__package_name_kebab_case }}/` contains the
actual template files with Jinja2 conditionals that branch on user choices.

After generation, the `hooks/post_gen_project.py` script runs to remove files
that don't apply (e.g., `.github/` when `ci_platform` is `gitlab`).

### Key Jinja patterns used

```jinja
{# Three-way platform routing #}
{%- if cookiecutter.ci_platform in ["github", "both"] %}
...github-specific content...
{%- endif %}

{# Type checker branching #}
{%- if cookiecutter.type_checker == "mypy" %}
_typecheck = "mypy ."
{%- elif cookiecutter.type_checker == "ty" %}
_typecheck = "ty check ."
{%- endif %}

{# GitHub Actions expressions must be escaped with raw/endraw #}
run: uv python install {% raw %}${{ env.PYTHON_VERSION }}{% endraw %}
```

## Testing

We use `pytest-cookies` to generate projects with every combination of
parameters and verify they are valid.

### Run the full test matrix

```bash
uv run pytest tests/ -n auto -v
```

### Run a specific combination

```bash
uv run pytest tests/ -k "github-mypy-subproject" -v
```

### What the tests check

1. The template generates without errors (`cookies.bake()` succeeds)
2. The expected files exist (or don't exist) for each parameter combination
3. The generated `pyproject.toml` is valid and `uv sync` succeeds
4. The generated code passes `poe precommit` (formatting + linting)
5. All generated YAML files are syntactically valid

### Adding a new parameter

When you add a new cookiecutter variable:

1. Add it to `cookiecutter.json` with a sensible default
2. Add the Jinja conditionals in the relevant template files
3. Update `hooks/post_gen_project.py` if files need to be removed
4. Add the new parameter to the test matrix in `tests/test_bake.py`
5. Update the root `README.md` parameters table
6. Update the generated project's `README.md` if relevant

## Pull Requests

1. Create a branch from `main`
2. Make your changes
3. Run `uv run pytest tests/ -n auto` locally
4. Submit a PR with a clear description of what changed and why
