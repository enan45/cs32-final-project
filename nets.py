### FP/nets.py
"""Net class for electrical connections to be routed."""


class Net:
    """
    An electrical connection between two pads.
    Every net has a unique id, two endpoint coordinates (start and goal),
    and after routing, a path of grid cells.
    """

    def __init__(self, net_id, start, goal):
        self.net_id = net_id
        self.start  = start     # (col, row) tuple
        self.goal   = goal      # (col, row) tuple
        self.path   = None      # list of (col, row) tuples after routing
        self.routed = False

    def __str__(self):
        status = f"routed (length={len(self.path)})" if self.routed else "unrouted"
        return f"Net {self.net_id}: {self.start} -> {self.goal} [{status}]"
