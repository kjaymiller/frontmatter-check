import pathlib
import logging
import itertools

from rich.console import Console
from typer import Typer, Option, Exit, echo
import typing
from typing_extensions import Annotated

from .pattern_check import FrontmatterPatternMatchCheck

app = Typer(no_args_is_help=True)
err_console = Console(stderr=True)


def _check_pattern(pattern_check: FrontmatterPatternMatchCheck, target_file):
    echo(f"Checking File: {target_file}")
    return pattern_check.validates(frontmatter_file=target_file)


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
    file_pattern: typing.List[str] = ["*.md", "*.txt"],
) -> None:
    """Check files for the layout attribute."""

    ret_code = 0

    pattern_check = FrontmatterPatternMatchCheck.from_yaml_config(
        config_file=config_file
    )

    for target_file in target_files:
        if target_file.is_dir():
            files_to_check = itertools.chain.from_iterable(
                target_file.glob(pattern) for pattern in file_pattern
            )
            for _target_file in files_to_check:
                try:
                    check_result = _check_pattern(
                        pattern_check=pattern_check, target_file=_target_file
                    )
                    ret_code = int(not check_result)
                except ValueError as e:
                    logging.error(e)
                    continue
        else:
            try:
                check_result = _check_pattern(
                    pattern_check=pattern_check, target_file=target_file
                )
                ret_code = int(not check_result)
            except ValueError as e:
                logging.error(e)
                continue

    raise Exit(code=ret_code)


if __name__ == "__main__":
    app()
