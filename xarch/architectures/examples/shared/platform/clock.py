from datetime import UTC, datetime

# the real time, read from the machine; it has the shape of kernel's Clock
class SystemClock:
    def now(self) -> datetime: return datetime.now(UTC)
