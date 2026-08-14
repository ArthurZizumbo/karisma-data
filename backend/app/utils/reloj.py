"""Monotonic stopwatch shared by the chat transport and its providers.

Two callers measure the same thing with the same clock -how long a stream has
been open, how long a card took to resolve- and both write the figure into a
log record or into a typed event. The function lived twice, byte for byte, in
``services/chat_stream.py`` and in ``services/proveedores/guionizado.py``: the
day one of the two switches to ``time.perf_counter`` or starts rounding up,
the two halves of one User Story publish durations that no longer compare.

``time.monotonic`` and not ``time.time``: a clock adjustment mid stream would
otherwise be able to produce a negative duration in a record that claims to
measure elapsed work.
"""

import time


def transcurrido_ms(inicio: float) -> int:
    """Return the milliseconds elapsed since a monotonic instant.

    Args:
        inicio: Reading of ``time.monotonic`` taken when the measured work
            started.

    Returns:
        The elapsed time, rounded down to the millisecond.
    """
    return int((time.monotonic() - inicio) * 1000)
