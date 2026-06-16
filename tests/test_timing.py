from app.core.timing import elapsed_ms, now_ms


def test_elapsed_ms_is_non_negative():
    start = now_ms()
    assert elapsed_ms(start) >= 0
