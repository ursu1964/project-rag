from scripts.check_dependencies import generate_report


def test_generate_report_contains_required_fields():
    report = generate_report()
    assert report
    first = report[0]
    assert {"package", "version", "risk", "update_recommendation"}.issubset(first)
