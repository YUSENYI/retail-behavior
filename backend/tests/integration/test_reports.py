from __future__ import annotations

from reports.report_service import ReportService


def test_report_generation_records_filters_and_masking_state() -> None:
    report = ReportService().generate("behavior_detail", {"channelId": "search"})
    assert report["filters"]["channelId"] == "search"
    assert report["sensitiveDataState"] == "masked"
