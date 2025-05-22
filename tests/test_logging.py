import io
import logging
import pytest
import sys

from frontmatter_check.logger import memory_handler


@pytest.fixture(scope="module")
def _test_logger():
    test_logger = logging.getLogger("FrontmatterCheck")
    test_logger.propagate = True
    return test_logger


def test_logging_setup(_test_logger, caplog):
    """Asserts that logging is channeled to the appropriate locations based on their level"""

    # Find the stdout handler specifically
    stdout_handler = None
    for handler in _test_logger.handlers:
        if isinstance(handler, logging.StreamHandler) and handler.stream == sys.stdout:
            stdout_handler = handler
            break

    assert stdout_handler is not None, "stdout_handler not found"

    # Create a test stream to capture output
    test_stream = io.StringIO()
    original_stream = stdout_handler.stream
    stdout_handler.stream = test_stream

    try:
        _test_logger.info("info message")
        _test_logger.warning("warning message")
        _test_logger.error("error message")

        # Verify stdout_handler only captures warnings and not errors
        stdout_output = test_stream.getvalue()
        assert "warning message" in stdout_output
        assert "info message" not in stdout_output
        assert "error message" not in stdout_output

        # Verify memory handler only captures errors and are formatted correctly
        memory_records = [r for r in memory_handler.buffer]
        assert len(memory_records) == 1
        assert memory_records[0].levelname == "ERROR"

        # Assert that only WARNING and ERROR are recorded
        assert len(caplog.records) == 2
        assert [r.levelname for r in caplog.records] == ["WARNING", "ERROR"]

    finally:
        # Restore original stream
        stdout_handler.stream = original_stream
