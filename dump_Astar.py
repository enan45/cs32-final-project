### FP/astar.py
"""A* search for routing a single net on the board."""

import heapq


def manhattan(a, b):
    """Manhattan distance between two (col, row) points.

    This is admissible — never overestimates — which guarantees A*
    will find the shortest valid path when one exists.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_route(board, net):
    """Find the shortest path for this net on the board using A*.

    Returns True if path found (and updates net.path, net.routed).
    Returns False if no path exists.
    """
    start = net.start
    goal  = net.goal

    # Priority queue ordered by f = g + h
    # Each entry: (f, g, col, row) — f is priority, g is cost so far
    frontier = []
    heapq.heappush(frontier, (manhattan(start, goal), 0, start[0], start[1]))

    # Track best g-cost seen for each cell
    best_cost = {start: 0}

    # Track how we got to each cell (for path reconstruction)
    came_from = {start: None}

    while frontier:
        f, g, col, row = heapq.heappop(frontier)
        current = (col, row)

        # Reached the goal — reconstruct path
        if current == goal:
            path = []
            node = goal
            while node is not None:
                path.append(node)
                node = came_from[node]
            path.reverse()

            net.path   = path
            net.routed = True
            return True

        # Skip if we already found a better path to this cell
        if g > best_cost.get(current, float('inf')):
            continue

        # Explore neighbors
        for nc, nr in board.neighbors(col, row, net.net_id):
            new_g = g + 1
            if new_g < best_cost.get((nc, nr), float('inf')):
                best_cost[(nc, nr)] = new_g
                came_from[(nc, nr)] = current
                new_f = new_g + manhattan((nc, nr), goal)
                heapq.heappush(frontier, (new_f, new_g, nc, nr))

    # Frontier empty — no path exists
    return False


def route_all(board, nets):
    """Route all nets sequentially.

    Each successfully routed trace becomes an obstacle for later nets.
    Returns (routed_count, failed_count).
    """
    routed_count = 0
    failed_count = 0

    for net in nets:
        success = astar_route(board, net)
        if success:
            board.mark_trace(net.path, net.net_id)
            routed_count += 1
            print(f"  Routed {net}")
        else:
            failed_count += 1
            print(f"  FAILED  {net}")

    return routed_count, failed_count
