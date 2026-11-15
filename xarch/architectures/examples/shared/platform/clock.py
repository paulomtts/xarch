class SystemClock:                 # satisfies kernel's Clock
    def now(self) -> datetime: return datetime.now(UTC)
