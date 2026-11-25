import atexit
import sys
from threading import RLock

from ._native import OutputRedactor


class _RedactedOutput:
    def __init__(self, stream, secrets):
        self._stream = stream
        self._filter = OutputRedactor()
        self._lock = RLock()
        self.add(secrets)
        atexit.register(self._finish)

    def add(self, secrets):
        with self._lock:
            self._filter.add(secrets)

    def write(self, text):
        with self._lock:
            output = self._filter.write(text.encode("utf-8", "surrogatepass"))
            if output:
                self._stream.write(output.decode("utf-8", "surrogatepass"))
        return len(text)

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def _finish(self):
        with self._lock:
            if not self._stream.closed:
                output = self._filter.finish()
                if output:
                    self._stream.write(output.decode("utf-8", "surrogatepass"))
                self._stream.flush()

    def __getattr__(self, name):
        return getattr(self._stream, name)


def redact_stdout(secrets):
    if not any(secrets) or sys.stdout is None:
        return
    if isinstance(sys.stdout, _RedactedOutput):
        sys.stdout.add(secrets)
    else:
        sys.stdout = _RedactedOutput(sys.stdout, secrets)
