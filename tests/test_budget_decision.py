from src.media_spend_cap import MediaWorkload, approve_workload


def test_workload_over_remaining_cap_is_rejected() -> None:
    workload = MediaWorkload("trailer.mov", 2.0, 10, 3.0, 2.01)
    assert approve_workload(workload, remaining_usd=2.00) is False
    assert approve_workload(workload, remaining_usd=2.01) is True
