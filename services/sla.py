from datetime import datetime, timedelta


SLA_DURATIONS = {
    "DESIRABLE": timedelta(days=14),
    "ESSENTIAL": timedelta(days=7),
    "CRITICAL": timedelta(days=2),
}


def calculate_sla_due_at(priority, created_at=None):
    """
    Calculate SLA due datetime based on priority.
    """
    if priority not in SLA_DURATIONS:
        raise ValueError(f"Invalid priority: {priority}")

    if created_at is None:
        created_at = datetime.utcnow()

    return created_at + SLA_DURATIONS[priority]
