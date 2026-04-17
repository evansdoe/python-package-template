"""Post-generation hook: remove files for disabled features and unused CI platform."""

import os
import shutil


def remove_path(path):
    """Remove a file or directory if it exists."""
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


CI_PLATFORM = "{{ cookiecutter.ci_platform }}"
IS_SUBPROJECT = "{{ cookiecutter.is_subproject }}" == "True"
PACKAGE_SLUG = "{{ cookiecutter.__package_name_kebab_case }}"
PACKAGE_SNAKE = "{{ cookiecutter.__package_name_snake_case }}"

# ── CI platform routing ──────────────────────────────────────────────────────
# Remove files for whichever platform is NOT chosen.

if CI_PLATFORM == "github":
    # Remove all GitLab CI files
    remove_path(".gitlab-ci.yml")
    remove_path(".gitlab-ci.root.yml")
    remove_path(".gitlab")
    remove_path("CODEOWNERS.gitlab")

elif CI_PLATFORM == "gitlab":
    # Remove all GitHub Actions files
    remove_path(".github")
    # Rename CODEOWNERS.gitlab -> CODEOWNERS (at repo root)
    if os.path.isfile("CODEOWNERS.gitlab"):
        os.rename("CODEOWNERS.gitlab", "CODEOWNERS")

elif CI_PLATFORM == "both":
    # Keep everything, but tidy up the CODEOWNERS file layout:
    # GitHub uses .github/CODEOWNERS (already in place)
    # GitLab uses root-level CODEOWNERS
    if os.path.isfile("CODEOWNERS.gitlab"):
        os.rename("CODEOWNERS.gitlab", "CODEOWNERS")

# ── For subprojects with GitHub, remove the module workflow in standalone mode ─
if CI_PLATFORM in ["github", "both"] and not IS_SUBPROJECT:
    module_workflow = os.path.join(".github", "workflows", f"{PACKAGE_SLUG}.yml")
    remove_path(module_workflow)

# ── For subprojects with GitLab, the root orchestrator stays until user moves it ─
if CI_PLATFORM in ["gitlab", "both"] and not IS_SUBPROJECT:
    remove_path(".gitlab-ci.root.yml")

# ── Docker ───────────────────────────────────────────────────────────────────
if "{{ cookiecutter.include_docker }}" != "True":
    remove_path("Dockerfile")
    remove_path(".dockerignore")

# ── DevContainer ─────────────────────────────────────────────────────────────
if "{{ cookiecutter.include_devcontainer }}" != "True":
    remove_path(".devcontainer")

# ── MkDocs ───────────────────────────────────────────────────────────────────
if "{{ cookiecutter.include_mkdocs }}" != "True":
    remove_path("mkdocs.yml")
    remove_path("docs")
    # GitHub Pages workflow
    if CI_PLATFORM in ["github", "both"]:
        remove_path(os.path.join(".github", "workflows", "docs.yml"))

# ── Pre-commit ───────────────────────────────────────────────────────────────
if "{{ cookiecutter.include_precommit }}" != "True":
    remove_path(".pre-commit-config.yaml")

# ── Type checker ─────────────────────────────────────────────────────────────
# py.typed marks the package as type-hint-aware; keep it for any type checker.
if "{{ cookiecutter.type_checker }}" == "none":
    remove_path(os.path.join(PACKAGE_SNAKE, "py.typed"))

# ── CLI ──────────────────────────────────────────────────────────────────────
if "{{ cookiecutter.include_cli }}" != "True":
    remove_path(os.path.join(PACKAGE_SNAKE, "cli.py"))

# ── Print next-steps message ─────────────────────────────────────────────────
print("")
print("━" * 70)
print(f"  Project generated: {PACKAGE_SLUG}")
print(f"  CI platform: {CI_PLATFORM}")
print("━" * 70)

if IS_SUBPROJECT:
    print("")
    print("  This is a SUBPROJECT. To wire it into your monorepo:")
    print("")
    print(f"    1. Move this project under src/ in your monorepo:")
    print(f"       mv {PACKAGE_SLUG} <monorepo>/src/")
    print("")

    if CI_PLATFORM in ["github", "both"]:
        print("    GitHub Actions:")
        print(f"       Move .github/workflows/ci.yml and {PACKAGE_SLUG}.yml into")
        print(f"       <monorepo>/.github/workflows/  (merge with existing if any)")
        print("")

    if CI_PLATFORM in ["gitlab", "both"]:
        print("    GitLab CI:")
        print(f"       Move .gitlab-ci.root.yml to <monorepo>/.gitlab-ci.yml")
        print(f"       (or merge its trigger job into the monorepo's existing .gitlab-ci.yml)")
        print(f"       Move CODEOWNERS to <monorepo>/CODEOWNERS")
        print("")

print("  Next steps:")
print(f"    cd {PACKAGE_SLUG}")
print("    git init && git add . && git commit -m 'Initial commit'")
print("    uv sync --all-extras --all-groups")
if "{{ cookiecutter.include_precommit }}" == "True":
    print("    uv run pre-commit install")
print("    uv run poe check")
print("    uv run poe test")
print("")
print("━" * 70)
