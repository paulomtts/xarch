from datetime import UTC, datetime

class SystemClock:                 # the real time, read from the machine; it has the shape of kernel's Clock
    def now(self) -> datetime: return datetime.now(UTC)
