class IdGenerator:
    def __init__(self, start: int = 1):
        self._next = start
    def next(self) -> int:
        nid = self._next
        self._next += 1
        return nid

GLOBAL_ID_GEN = IdGenerator()