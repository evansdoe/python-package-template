"""CLI for {{ cookiecutter.package_name }}."""

import typer

app = typer.Typer(
    name="{{ cookiecutter.__package_name_kebab_case }}",
    help="{{ cookiecutter.package_description }}",
    add_completion=False,
)


@app.command()
def hello(name: str = typer.Argument("world", help="Name to greet")) -> None:
    """Say hello — replace this with your real commands."""
    typer.echo(f"Hello, {name}! Project {{ cookiecutter.__package_name_kebab_case }} is set up!")


if __name__ == "__main__":
    app()
