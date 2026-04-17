{%- set is_github = cookiecutter.ci_platform in ["github", "both"] -%}
{%- set is_gitlab = cookiecutter.ci_platform in ["gitlab", "both"] -%}
{%- if cookiecutter.ci_platform == "github" -%}
{%- set contrib_term = "Pull Request" -%}
{%- set contrib_term_short = "PR" -%}
{%- else -%}
{%- set contrib_term = "Merge Request" -%}
{%- set contrib_term_short = "MR" -%}
{%- endif -%}
# Contributing to {{ cookiecutter.package_name }}

Thank you for your interest in contributing! This document provides guidelines
and instructions for contributing to this project.

## Development Setup

1. Clone the repository:

   ```bash
   git clone {{ cookiecutter.package_url }}.git
   cd {{ cookiecutter.__package_name_kebab_case }}
   ```

2. Install dependencies with [uv](https://docs.astral.sh/uv/):

   ```bash
   uv sync --all-extras --all-groups
   ```
{%- if cookiecutter.include_precommit %}

3. Install pre-commit hooks:

   ```bash
   uv run pre-commit install
   ```
{%- endif %}

## Development Workflow

Before submitting changes, run the full quality pipeline:

```bash
# Format and lint (auto-fix)
uv run poe precommit

# Check formatting, linting, licenses{{ ", and types" if cookiecutter.type_checker != "none" else "" }}
uv run poe check

# Run tests
uv run poe test
```

### Available Tasks

| Task | Description |
|---|---|
| `poe precommit` | Auto-format, sort imports, fix lint issues |
| `poe check` | Verify format, imports, lint, licenses{{ ", types" if cookiecutter.type_checker != "none" else "" }} |
| `poe test` | Run pytest with coverage |
{%- if cookiecutter.type_checker != "none" %}
| `poe typecheck` | Run mypy type checking |
{%- endif %}
{%- if cookiecutter.include_mkdocs %}
| `poe docs` | Serve documentation locally |
{%- endif %}



## Template Updates

This project was scaffolded with [Cruft](https://cruft.github.io/cruft/).
To check for and apply template updates:

```bash
# Check if the project has drifted from the template
uv run cruft check

# Pull in template changes (interactive merge)
uv run cruft update

# Resolve any .rej files, then commit
```

## Branching Strategy

- `main` — stable, production-ready
- `dev` — integration branch for features
- `feature/<name>` — feature branches, merge into `dev`
- `fix/<name>` — bugfix branches

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new data loader
fix: handle edge case in parser
docs: update API reference
chore: bump dependency versions
test: add tests for transformer module
```

## {{ contrib_term }}s

1. Create a branch from `dev`
2. Make your changes with tests
3. Ensure `poe check` and `poe test` pass
4. Submit {{ "a" if contrib_term_short == "PR" else "an" }} {{ contrib_term_short }} to `dev` with a clear description
{%- if cookiecutter.ci_platform == "both" %}

## Platform Notes

This project supports both **GitHub** and **GitLab** CI pipelines. When
contributing, be aware that changes to `.github/workflows/` affect GitHub
Actions while changes under `.gitlab-ci.yml` and `.gitlab/` affect GitLab CI.
Keep both in sync when modifying the pipeline.
{%- endif %}
