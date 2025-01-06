import pytest
import logging

from frontmatter_check.logger import memory_handler


@pytest.fixture(scope="module")
def _test_logger():
    test_logger = logging.getLogger("FrontmatterCheck")
    test_logger.propagate = True
    return test_logger


def test_logging_setup(_test_logger, caplog):
    """Asserts that logging is channeled to the appropriate locations based on their level"""
    _test_logger.info("info message")
    _test_logger.warning("warning message")
    _test_logger.error("error message")

    # Verify memory handler only captures errors and are formatted correctly
    memory_records = [r for r in memory_handler.buffer]
    assert len(memory_records) == 1

    # Assert that only WARNING and ERROR are recorded
    assert len(caplog.records) == 2
    assert [r.levelname for r in caplog.records] == ["WARNING", "ERROR"]
