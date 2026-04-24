### lee.py
"""
Lee's algorithm which is an implementation ofA* with h=0.
guaranteed shortest path if one exists.
first I am implementing this without heuristic,
I will later figure out theManhattan heuristic to make it A* proper.
"""

from collections import deque
from grid import Grid, Cell

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
    allowed_pads = {source, target}

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

        col, row = current
        neighbors = grid.neighbors(col, row)


        for neighbor in neighbors:
          cell = grid.get(neighbor[0], neighbor[1])

          if cell.state == Cell.PAD and neighbor not in allowed_pads:
              continue

          if neighbor not in visited:
            visited.add(neighbor)
            came_from[neighbor] = current
            frontier.append(neighbor)

    # no path found
    return None


def reconstruct_path(came_from, target):
    """
    Rebuild the path by starting at the target
    and walking backward to the source.
    """
    path = []
    current = target

    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

####pygame
def find_path_stepped(grid, source, target):
    """Generator version of find_path for live visualization.

    At each step, yields a dict describing the current state:
        {
            'current':   the cell just popped from the frontier,
            'frontier':  list of cells currently in the frontier,
            'visited':   set of cells already processed,
            'came_from': dict mapping cell -> predecessor,
            'done':      False during search, True when finished,
            'path':      None during search, final path (or None) at end,
            'iteration': iteration count
        }

    Consume with a for loop; the final yield has done=True and path set.
    """
    allowed_pads = {source, target}

    frontier  = deque([source])
    visited   = {source}
    came_from = {source: None}
    iteration = 0

    while frontier:
        iteration += 1
        current = frontier.popleft()

        # Yield state BEFORE checking for target so animation shows the hit
        yield {
            'current':   current,
            'frontier':  list(frontier),
            'visited':   set(visited),
            'came_from': dict(came_from),
            'done':      False,
            'path':      None,
            'iteration': iteration,
        }

        if current == target:
            path = reconstruct_path(came_from, target)
            yield {
                'current':   current,
                'frontier':  list(frontier),
                'visited':   set(visited),
                'came_from': dict(came_from),
                'done':      True,
                'path':      path,
                'iteration': iteration,
            }
            return

        col, row = current
        for neighbor in grid.neighbors(col, row):
            if grid.get(*neighbor).state == Cell.PAD and neighbor not in allowed_pads:
                continue
            if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                frontier.append(neighbor)

    # Frontier exhausted without finding target
    yield {
        'current':   None,
        'frontier':  [],
        'visited':   set(visited),
        'came_from': dict(came_from),
        'done':      True,
        'path':      None,
        'iteration': iteration,
    }
