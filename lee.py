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
    """
    Find the shortest path from source to target using BFS.

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
    iterations = 0

    while frontier:
        iterations += 1
        current = frontier.popleft()

        # stop if we reached the target
        if current == target:
            stats = {
                'iterations': iterations, 
                'visited': len(visited)
            }
            return reconstruct_path(came_from, target), stats

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
    stats = {
        'iterations': iterations, 
        'visited': len(visited)
    } #Use stats when comparing lee with astar

    return None, stats


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

###pygame
def find_path_stepped(grid, source, target):
    """ 
    Step by step Lee search for visualization. I utilize generators which is something new
    I learnt during this project! instead of showing final path as find path would, I show the search
    as it happnes

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

    allowed_pads = {source, target} #same as above

    #normal BFS setup as above too
    frontier  = deque()
    frontier.append(source)

    visited   = set()
    visited.add(source)

    came_from = {source: None}
    iteration = 0

    while frontier:
        iteration += 1
        current = frontier.popleft()

        # yield to paused and hand pygame visualizer snapshot of current search state. Generator implementation
        #builds a dictionary for ease of reading stuff and to separate current, frontier and visited.
        yield {
            'current':   current,
            'frontier':  list(frontier),
            'visited':   set(visited),
            'came_from': dict(came_from),
            'done':      False,
            'path':      None,
            'iteration': iteration,
        }

        #if search reaches target, I contstruct final path, then yield again a snapshot telling visualizer search is finished
        #same dictionary, same code from BFS
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

        #same As BFS
        col, row = current
        for neighbor in grid.neighbors(col, row):
             cell = grid.get(neighbor[0], neighbor[1])

             if cell.state == Cell.PAD and neighbor not in allowed_pads:
                 continue
             
             if neighbor not in visited:
                visited.add(neighbor)
                came_from[neighbor] = current
                frontier.append(neighbor)

    # Frontier exhausted without finding target. final yield
    #frontier empties before reaching target, yield final state. search is done. no path found
    yield {
        'current':   None,
        'frontier':  [],
        'visited':   set(visited),
        'came_from': dict(came_from),
        'done':      True,
        'path':      None,
        'iteration': iteration,
    }


"""
A generator is a function that can pause and continue later. In this project, that lets me run the BFS 
one step at a time and show each step in Pygame. Without this pygame would not run as I envision it.
"""