### astar.py
"""
A* shortest-path search for PCB routing.

A* generalizes Lee's algorithm by ordering the frontier with f = g + h
where g is cost-from-source and h is an admissible estimate of remaining
cost. 

With h=0 this reduces exactly to Lee's BFS. With h=Manhattan distance
on a 4-direction grid, A* finds the same shortest paths as Lee but expands
far fewer cells on long routes.
"""

import heapq
from grid import Cell


def manhattan(a, b):
    """
    Manhattan distance between two (col, row) cells.
    """
    #how far apart two cells are if movement is only allowed up, down, left, and right.
    return abs(a[0] - b[0]) + abs(a[1] - b[1]) 


def find_path(grid, source, target):
    """Find the shortest path from source to target using A* search.
    
    Args and returns same as find path
    """
    allowed_pads = {source, target} #same as lee
    
    # Each entry is (f_score, g_score, cell). T
    frontier = []
    start_h = manhattan(source, target)
    start_g = 0
    start_cell = source

    heapq.heappush(frontier, (start_h, start_g, start_cell))
    
    # best known cost from source to each cell
    best_g = {source: 0}
    
    # For each cell, the predecessor used to reach its best-known cost.
    came_from = {source: None}

    iterations = 0
    
    while frontier:
        iterations += 1
        f_score, g_score, current = heapq.heappop(frontier)
        
        # if this heap entry is outdated, skip it
        if g_score > best_g[current]:
            continue

        #Stop if we reached the target
        if current == target:
            stats = {
                'iterations': iterations, 
                'visited': len(best_g)
            }
            path = reconstruct_path(came_from, target)
            return path, stats
        
        col, row = current
        
        # Expand neighbors.
        for neighbor in grid.neighbors(col, row):
            cell = grid.get(neighbor[0], neighbor[1])

            #do not move through unrelated pads 
            if cell.state == Cell.PAD and neighbor not in allowed_pads:
                continue
            
            new_g = g_score + 1

            #only keep this path if it better
            
            if new_g < best_g.get(neighbor, float('inf')):
                best_g[neighbor] = new_g
                came_from[neighbor] = current

                new_f = new_g + manhattan(neighbor, target)
                heapq.heappush(frontier, (new_f, new_g, neighbor))


    # Frontier emptied without reaching target ---> no path exists.
    stats = {
        'iterations': iterations, 
        'visited': len(best_g)
    }
    return None, stats


def reconstruct_path(came_from, target): # same as lee
    """Walk backwards from target using came_from, then reverse."""
    path = []
    current = target

    while current is not None:
        path.append(current)
        current = came_from[current]
        
    path.reverse()
    return path