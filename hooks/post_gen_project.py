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
    print(f"  1. Move this project under src/ (if not already there):")
    print(f"       mv {PACKAGE_SLUG} <monorepo>/src/")
    print("")
    print("  2. Wire up CI:")
    print("")

    if CI_PLATFORM in ["github", "both"]:
        print("     GitHub Actions:")
        print("")
        print("     ┌─ FIRST subproject (no .github/workflows/ci.yml yet):")
        print("     │   mkdir -p <monorepo>/.github/workflows")
        print(f"    │   cp src/{PACKAGE_SLUG}/.github/workflows/ci.yml <monorepo>/.github/workflows/")
        print(f"    │   cp src/{PACKAGE_SLUG}/.github/workflows/{PACKAGE_SLUG}.yml <monorepo>/.github/workflows/")
        print("     │")
        print("     └─ ADDITIONAL subproject (ci.yml already exists):")
        print(f"        Copy the path filter + trigger job for {PACKAGE_SLUG}")
        print(f"        from src/{PACKAGE_SLUG}/.github/workflows/ci.yml")
        print(f"        into your existing <monorepo>/.github/workflows/ci.yml")
        print(f"        Then copy the module workflow:")
        print(f"          cp src/{PACKAGE_SLUG}/.github/workflows/{PACKAGE_SLUG}.yml <monorepo>/.github/workflows/")
        print("")

    if CI_PLATFORM in ["gitlab", "both"]:
        print("     GitLab CI:")
        print("")
        print("     ┌─ FIRST subproject (no .gitlab-ci.yml at monorepo root yet):")
        print(f"    │   mv src/{PACKAGE_SLUG}/.gitlab-ci.root.yml <monorepo>/.gitlab-ci.yml")
        print(f"    │   mv src/{PACKAGE_SLUG}/CODEOWNERS <monorepo>/CODEOWNERS")
        print("     │")
        print("     └─ ADDITIONAL subproject (.gitlab-ci.yml already exists):")
        print(f"        Copy the trigger-{PACKAGE_SLUG} job from")
        print(f"          src/{PACKAGE_SLUG}/.gitlab-ci.root.yml")
        print(f"        into your existing <monorepo>/.gitlab-ci.yml")
        print(f"        Then: rm src/{PACKAGE_SLUG}/.gitlab-ci.root.yml")
        print(f"        Merge the {PACKAGE_SLUG} entry from src/{PACKAGE_SLUG}/CODEOWNERS")
        print(f"        into your existing <monorepo>/CODEOWNERS")
        print(f"        Then: rm src/{PACKAGE_SLUG}/CODEOWNERS")
        print("")

    print("  3. Initialize git (if this is a new monorepo):")
    print("       cd <monorepo>")
    print("       git init && git add . && git commit -m 'Initial commit'")
    print("")
    print("  4. Install dependencies:")
    print(f"       cd src/{PACKAGE_SLUG}")
    print("       uv sync --all-extras --all-groups")
    if "{{ cookiecutter.include_precommit }}" == "True":
        print("")
        print("  5. Install pre-commit hooks (requires git):")
        print(f"       cd src/{PACKAGE_SLUG}")
        print("       uv run pre-commit install")
        print("")
        print("  6. Verify:")
    else:
        print("")
        print("  5. Verify:")
    print(f"       cd src/{PACKAGE_SLUG}")
    print("       uv run poe check")
    print("       uv run poe test")

else:
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
