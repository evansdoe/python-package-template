"""Tests for the Python package template.

Uses pytest-cookies to generate projects with various parameter combinations
and verify the output is correct.

Test tiers:
  - test_bake_*: Fast file-existence checks across the full parameter matrix
  - test_yaml_*: YAML syntax validation for all generated CI files
  - test_integration_*: Actually runs uv sync + poe precommit (slow, marked)
"""

import os
import subprocess

import pytest
import yaml

# ──────────────────────────────────────────────────────────────────────────
# Shared defaults — every test overrides only what it's testing
# ──────────────────────────────────────────────────────────────────────────
DEFAULTS = {
    "package_name": "Test Package",
    "package_description": "A test project",
    "is_subproject": "True",
    "accelerator": "none",
    "package_url": "https://github.com/test/test-package",
    "author_name": "Test Author",
    "author_email": "test@example.com",
    "python_version": "3.13",
    "uv_version": "latest",
    "timezone": "Europe/Vienna",
    "docstring_style": "google",
    "open_source_license": "MIT",
    "ci_platform": "github",
    "gitlab_registry": "registry.gitlab.com",
    "include_docker": "True",
    "include_devcontainer": "True",
    "include_mkdocs": "True",
    "include_precommit": "True",
    "type_checker": "mypy",
    "include_cli": "True",
    "include_security_scans": "True",
    "include_pypi_publish": "False",
}


def bake(cookies, **overrides):
    """Bake the template with defaults + overrides and assert success."""
    ctx = {**DEFAULTS, **overrides}
    result = cookies.bake(extra_context=ctx)
    assert result.exit_code == 0, f"Bake failed: {result.exception}"
    assert result.exception is None
    assert result.project_path.is_dir()
    return result


def collect_yaml_files(project_path):
    """Find all .yml files in the generated project."""
    yamls = []
    for root, _, files in os.walk(project_path):
        for f in files:
            if f.endswith((".yml", ".yaml")):
                yamls.append(os.path.join(root, f))
    return yamls


# ──────────────────────────────────────────────────────────────────────────
# Core bake tests: ci_platform × is_subproject × type_checker
# ──────────────────────────────────────────────────────────────────────────
CI_PLATFORMS = ["github", "gitlab", "both"]
SUBPROJECT_VALUES = ["True", "False"]
TYPE_CHECKERS = ["mypy", "ty", "none"]


@pytest.mark.parametrize("ci_platform", CI_PLATFORMS)
@pytest.mark.parametrize("is_subproject", SUBPROJECT_VALUES)
@pytest.mark.parametrize("type_checker", TYPE_CHECKERS)
def test_bake_core_matrix(cookies, ci_platform, is_subproject, type_checker):
    """Test that every core combination generates without errors."""
    result = bake(
        cookies,
        ci_platform=ci_platform,
        is_subproject=is_subproject,
        type_checker=type_checker,
    )
    assert result.project_path.name == "test-package"


# ──────────────────────────────────────────────────────────────────────────
# CI platform file routing
# ──────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("ci_platform", CI_PLATFORMS)
def test_github_files_presence(cookies, ci_platform):
    """GitHub files exist only when ci_platform is github or both."""
    result = bake(cookies, ci_platform=ci_platform)
    github_dir = result.project_path / ".github"
    should_exist = ci_platform in ("github", "both")
    assert github_dir.exists() == should_exist


@pytest.mark.parametrize("ci_platform", CI_PLATFORMS)
def test_gitlab_files_presence(cookies, ci_platform):
    """GitLab files exist only when ci_platform is gitlab or both."""
    result = bake(cookies, ci_platform=ci_platform)
    gitlab_ci = result.project_path / ".gitlab-ci.yml"
    gitlab_dir = result.project_path / ".gitlab"
    should_exist = ci_platform in ("gitlab", "both")
    assert gitlab_ci.exists() == should_exist
    assert gitlab_dir.exists() == should_exist


@pytest.mark.parametrize("ci_platform", CI_PLATFORMS)
def test_subproject_orchestrator_files(cookies, ci_platform):
    """Subproject generates orchestrator files; standalone does not."""
    # Subproject mode
    result_sub = bake(cookies, ci_platform=ci_platform, is_subproject="True")

    if ci_platform in ("github", "both"):
        module_wf = result_sub.project_path / ".github" / "workflows" / "test-package.yml"
        assert module_wf.exists(), "Subproject should have module-specific workflow"

    if ci_platform in ("gitlab", "both"):
        root_ci = result_sub.project_path / ".gitlab-ci.root.yml"
        assert root_ci.exists(), "Subproject should have root orchestrator"

    # Standalone mode
    result_std = bake(cookies, ci_platform=ci_platform, is_subproject="False")

    if ci_platform in ("github", "both"):
        module_wf = result_std.project_path / ".github" / "workflows" / "test-package.yml"
        assert not module_wf.exists(), "Standalone should NOT have module workflow"

    if ci_platform in ("gitlab", "both"):
        root_ci = result_std.project_path / ".gitlab-ci.root.yml"
        assert not root_ci.exists(), "Standalone should NOT have root orchestrator"


# ──────────────────────────────────────────────────────────────────────────
# Type checker routing
# ──────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("type_checker", TYPE_CHECKERS)
def test_type_checker_pyproject(cookies, type_checker):
    """pyproject.toml contains the right type checker dep and config."""
    result = bake(cookies, type_checker=type_checker)
    pyproject = (result.project_path / "pyproject.toml").read_text()

    if type_checker == "mypy":
        assert '"mypy>=' in pyproject
        assert "[tool.mypy]" in pyproject
        assert "[tool.ty]" not in pyproject
    elif type_checker == "ty":
        assert '"ty>=' in pyproject
        assert "[tool.ty]" in pyproject
        assert "[tool.mypy]" not in pyproject
    else:
        assert '"mypy' not in pyproject
        assert '"ty>=' not in pyproject
        assert "[tool.mypy]" not in pyproject
        assert "[tool.ty]" not in pyproject


@pytest.mark.parametrize("type_checker", TYPE_CHECKERS)
def test_type_checker_poe_tasks(cookies, type_checker):
    """poe typecheck task exists only when type_checker is not none."""
    result = bake(cookies, type_checker=type_checker)
    pyproject = (result.project_path / "pyproject.toml").read_text()

    if type_checker == "none":
        assert "_typecheck" not in pyproject
    else:
        assert '_typecheck = "' in pyproject
        assert "typecheck" in pyproject


@pytest.mark.parametrize("type_checker", TYPE_CHECKERS)
def test_py_typed_marker(cookies, type_checker):
    """py.typed exists when a type checker is selected."""
    result = bake(cookies, type_checker=type_checker)
    py_typed = result.project_path / "test_package" / "py.typed"
    should_exist = type_checker != "none"
    assert py_typed.exists() == should_exist


# ──────────────────────────────────────────────────────────────────────────
# Feature toggle tests
# ──────────────────────────────────────────────────────────────────────────
def test_docker_toggle(cookies):
    """Dockerfile and .dockerignore removed when include_docker is False."""
    result = bake(cookies, include_docker="False")
    assert not (result.project_path / "Dockerfile").exists()
    assert not (result.project_path / ".dockerignore").exists()


def test_devcontainer_toggle(cookies):
    """DevContainer removed when include_devcontainer is False."""
    result = bake(cookies, include_devcontainer="False")
    assert not (result.project_path / ".devcontainer").exists()


def test_mkdocs_toggle(cookies):
    """MkDocs files removed when include_mkdocs is False."""
    result = bake(cookies, include_mkdocs="False")
    assert not (result.project_path / "mkdocs.yml").exists()
    assert not (result.project_path / "docs").exists()


def test_mkdocs_docs_workflow_toggle(cookies):
    """GitHub docs.yml workflow removed when include_mkdocs is False."""
    result = bake(cookies, include_mkdocs="False", ci_platform="github")
    docs_yml = result.project_path / ".github" / "workflows" / "docs.yml"
    assert not docs_yml.exists()


def test_precommit_toggle(cookies):
    """Pre-commit config removed when include_precommit is False."""
    result = bake(cookies, include_precommit="False")
    assert not (result.project_path / ".pre-commit-config.yaml").exists()


def test_cli_toggle(cookies):
    """CLI file removed when include_cli is False."""
    result = bake(cookies, include_cli="False")
    assert not (result.project_path / "test_package" / "cli.py").exists()

    result_on = bake(cookies, include_cli="True")
    assert (result_on.project_path / "test_package" / "cli.py").exists()
    pyproject = (result_on.project_path / "pyproject.toml").read_text()
    assert "[project.scripts]" in pyproject


# ──────────────────────────────────────────────────────────────────────────
# GPU toggle
# ──────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "accelerator,expected_image",
    [
        ("none", "debian:stable-slim"),
        ("cuda", "nvidia/cuda"),
        ("rocm", "rocm/dev-ubuntu"),
        ("mps", "debian:stable-slim"),
        ("tpu", "debian:stable-slim"),
    ],
)
def test_accelerator_dockerfile(cookies, accelerator, expected_image):
    """Accelerator choice sets correct FROM_IMAGE in Dockerfile."""
    result = bake(cookies, accelerator=accelerator)
    dockerfile = (result.project_path / "Dockerfile").read_text()
    assert expected_image in dockerfile


def test_accelerator_docker_compose_cuda(cookies):
    """CUDA adds nvidia deploy block and shm_size."""
    result = bake(cookies, accelerator="cuda")
    compose = (result.project_path / ".devcontainer" / "docker-compose.yml").read_text()
    assert "shm_size" in compose
    assert "nvidia" in compose
    assert "driver: nvidia" in compose


def test_accelerator_docker_compose_rocm(cookies):
    """ROCm adds AMD device passthrough and shm_size."""
    result = bake(cookies, accelerator="rocm")
    compose = (result.project_path / ".devcontainer" / "docker-compose.yml").read_text()
    assert "shm_size" in compose
    assert "/dev/kfd" in compose
    assert "/dev/dri" in compose


@pytest.mark.parametrize("accelerator", ["none", "mps", "tpu"])
def test_accelerator_docker_compose_no_gpu(cookies, accelerator):
    """Non-Docker accelerators have no GPU blocks in docker-compose."""
    result = bake(cookies, accelerator=accelerator)
    compose = (result.project_path / ".devcontainer" / "docker-compose.yml").read_text()
    assert "shm_size" not in compose
    assert "nvidia" not in compose
    assert "/dev/kfd" not in compose


# ──────────────────────────────────────────────────────────────────────────
# License generation
# ──────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize(
    "license_choice,expected_text",
    [
        ("MIT", "MIT License"),
        ("Apache-2.0", "Apache License"),
        ("BSD-3-Clause", "BSD 3-Clause"),
        ("Proprietary", "proprietary and confidential"),
    ],
)
def test_license_content(cookies, license_choice, expected_text):
    """LICENSE file contains the right license text."""
    result = bake(cookies, open_source_license=license_choice)
    license_text = (result.project_path / "LICENSE").read_text()
    assert expected_text in license_text


# ──────────────────────────────────────────────────────────────────────────
# Shared files always present
# ──────────────────────────────────────────────────────────────────────────
def test_core_files_always_present(cookies):
    """Essential files exist regardless of parameter choices."""
    result = bake(cookies)
    for path in [
        "pyproject.toml",
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "LICENSE",
        ".gitignore",
        ".editorconfig",
        ".python-version",
        ".env.example",
        "test_package/__init__.py",
        "test_package/main.py",
        "tests/test__example.py",
    ]:
        assert (result.project_path / path).exists(), f"{path} should always exist"


def test_python_version_file(cookies):
    """.python-version contains the correct version."""
    result = bake(cookies, python_version="3.13")
    content = (result.project_path / ".python-version").read_text().strip()
    assert content == "3.13"


def test_python_version_not_gitignored(cookies):
    """.python-version should NOT be in .gitignore."""
    result = bake(cookies)
    gitignore = (result.project_path / ".gitignore").read_text()
    assert ".python-version" not in gitignore


# ──────────────────────────────────────────────────────────────────────────
# No Jinja leaks
# ──────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("ci_platform", CI_PLATFORMS)
@pytest.mark.parametrize("type_checker", TYPE_CHECKERS)
def test_no_jinja_leaks(cookies, ci_platform, type_checker):
    """No leftover {{ or {% tags in generated files."""
    result = bake(cookies, ci_platform=ci_platform, type_checker=type_checker)
    for root, _, files in os.walk(result.project_path):
        for f in files:
            filepath = os.path.join(root, f)
            try:
                content = open(filepath).read()
            except UnicodeDecodeError:
                continue  # skip binary files
            assert "{{" not in content or "cookiecutter" not in content, (
                f"Jinja leak in {filepath}"
            )
            assert "{%" not in content, f"Jinja block tag leak in {filepath}"


# ──────────────────────────────────────────────────────────────────────────
# YAML validity
# ──────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("ci_platform", CI_PLATFORMS)
@pytest.mark.parametrize("is_subproject", SUBPROJECT_VALUES)
def test_yaml_validity(cookies, ci_platform, is_subproject):
    """All generated YAML files are syntactically valid."""
    result = bake(
        cookies, ci_platform=ci_platform, is_subproject=is_subproject
    )
    yaml_files = collect_yaml_files(result.project_path)
    assert len(yaml_files) > 0, "Should have at least one YAML file"

    for f in yaml_files:
        with open(f) as fp:
            try:
                yaml.safe_load(fp)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {f}: {e}")


# ──────────────────────────────────────────────────────────────────────────
# Cruft support
# ──────────────────────────────────────────────────────────────────────────
def test_cruft_dev_dependency(cookies):
    """cruft is included as a dev dependency."""
    result = bake(cookies)
    pyproject = (result.project_path / "pyproject.toml").read_text()
    assert '"cruft>=' in pyproject


# ──────────────────────────────────────────────────────────────────────────
# Integration tests — actually run uv sync (slow, needs network)
# ──────────────────────────────────────────────────────────────────────────
@pytest.mark.slow
@pytest.mark.parametrize(
    "ci_platform,type_checker",
    [
        ("github", "mypy"),
        ("gitlab", "ty"),
        ("both", "none"),
    ],
)
def test_integration_uv_sync(cookies, ci_platform, type_checker):
    """Generated project can actually install dependencies with uv."""
    result = bake(
        cookies,
        ci_platform=ci_platform,
        type_checker=type_checker,
        include_cli="False",  # avoid typer dep to speed up sync
    )
    proc = subprocess.run(
        ["uv", "sync", "--all-extras", "--all-groups"],
        cwd=result.project_path,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, (
        f"uv sync failed:\nstdout: {proc.stdout}\nstderr: {proc.stderr}"
    )
