import json
import logging

from app.core.logging import JsonFormatter


def test_json_formatter_emits_monitoring_fields() -> None:
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="request_completed",
        args=(),
        exc_info=None,
    )
    record.request_id = "req-123"
    record.status_code = 200

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "test"
    assert payload["message"] == "request_completed"
    assert payload["request_id"] == "req-123"
    assert payload["status_code"] == 200
    assert "timestamp" in payload
