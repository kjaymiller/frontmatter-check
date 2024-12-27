import pathlib

import frontmatter
from rich.console import Console
from typer import Typer, Option, Exit
import typing
from typing_extensions import Annotated

from .frontmatter_validator import FrontmatterValidator

app = Typer(no_args_is_help=True)
err_console = Console(stderr=True)


@app.command(
    name="check",
)
def check_file(
    target_files: typing.List[pathlib.Path],
    config_file: Annotated[
        pathlib.Path,
        Option(help="configuration file to process rules"),
    ],
) -> None:
    """Check a file for the layout attribute."""

    ret_code = 0
    validator = FrontmatterValidator(config_file=config_file)

    for target_file in target_files:
        fm_file = frontmatter.loads(target_file.read_text())

        if not fm_file.metadata:
            continue

        results = validator.validates(post=fm_file)
        ret_code = int(not (results.validates))  # Return 1 for False

        if results.warnings:
            warning_codes = [
                f"{target_file} is missing `{warning}`" for warning in results.warnings
            ]
            print("WARNINGS: \n".join(warning_codes))

        if results.errors:
            error_codes = [
                f"{target_file} is missing `{error}`" for error in results.errors
            ]
            err_console.print("\n".join(error_codes))

    raise Exit(code=ret_code)


if __name__ == "__main__":
    app()
