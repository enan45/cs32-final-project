### lee.py
"""
Lee's algorithm which is an implementation ofA* with h=0.
guaranteed shortest path if one exists.
first I am implementing this without heuristic,
I will later figure out theManhattan heuristic to make it A* proper.
"""

from collections import deque

def find_path(grid, source, target):
    """Find the shortest path from source to target using BFS.

    Args:
        grid: Grid object from grid.py
        source: (col, row) tuple — the starting cell
        target: (col, row) tuple — the goal cell

    Returns:
        A list of (col, row) tuples from source to target,
        or None if no path exists.
    """
    # FIFO queue of cells to expand. double ended queue.
    frontier = deque()
    frontier.append(source)

    # keep track of cells we've already visited
    visited = set()
    visited.add(source)

    # For each visited cell, which cell did we reach it from?
    came_from = {source: None}

    while frontier:
        current = frontier.popleft()

        # stop if we reached the target
        if current == target:
            return reconstruct_path(came_from, target)

        # Expand neighbors
        col, row = current
        for neighbor in grid.neighbors(col, row):
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                frontier.append(neighbor)

    # Frontier emptied without finding target — no path exists
    return None


def reconstruct_path(came_from, target):
    """Walk came_from backwards from target to source, then reverse."""
    path = []
    current = target
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path
