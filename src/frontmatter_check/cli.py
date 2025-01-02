import pathlib
import logging

from rich.console import Console
from typer import Typer, Option, Exit
import typing
from typing_extensions import Annotated

from .pattern_check import FrontmatterPatternCheck

app = Typer(no_args_is_help=True)
err_console = Console(stderr=True)


@app.command(
    name="check",
)
def check_files(
    target_files: typing.List[pathlib.Path],
    config_file: Annotated[
        pathlib.Path,
        Option(
            help="configuration file to process rules",
            envvar="FRONTMATTER_CHECK_CONFIG_FILE",
        ),
    ] = pathlib.Path(".frontmatter_check.yaml"),
) -> None:
    """Check files for the layout attribute."""

    ret_code = 0

    pattern_check = FrontmatterPatternCheck.from_yaml_config(config_file=config_file)

    for target_file in target_files:
        try:
            check_result = pattern_check.validates(frontmatter_file=target_file)
            ret_code = int(not check_result)

        except ValueError as e:
            logging.error(e)
            continue

    raise Exit(code=ret_code)


if __name__ == "__main__":
    app()
