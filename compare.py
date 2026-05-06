### compare.py
"""
Side-by-side comparison of Lee's algorithm vs A* with Manhattan heuristic.

Both algorithms find the shortest path. The point of A* is that it finds
it by visiting far fewer cells, especially on long routes. This code was 
built to show the numbers for this as I was curious how much faster manhattan 
heuristics make the algo run.
"""

from circuits import build_555_timer
from lee import find_path as lee_find
from astar import find_path as astar_find


def compare_net(net_name):
    """
    Route the same net with both algorithms and print stats which i defined in lee and astar.
    """
    #build the same circuit twice. I need both algos to start from the same clean board
    grid_lee, pads = build_555_timer()
    grid_astar, _  = build_555_timer()
    
    #pick source and target pads for chosen net.
    source = pads[net_name][0]
    target = pads[net_name][1]

    #run both routing algos on same start and end points    
    path_lee, stats_lee = lee_find(
        grid_lee, source, target
    )
    
    path_astar, stats_astar = astar_find(
        grid_astar, source, target
    )
    
    #This handles the case where one of the algos cant find a route. This is when either is none, pring no path found
    if path_lee is None or path_astar is None:
        print(f"{net_name}: no path found")
        return
    
    #compares how many cells each algo visited. lee against astar becuase I expect lee to have more cells visited than astar
    lee_visited = stats_lee["visited"]
    astar_visited = stats_astar['visited']
    speedup = lee_visited / astar_visited

    #print comparison results
    print("Net:", net_name)
    print("  Path length:", len(path_lee))
    print("  Lee visited:", stats_lee["visited"])
    print("  A* visited:", stats_astar["visited"])
    print("  Speedup:", round(speedup, 1), "x")
    print()
    
    # Sanity check that both algorithms find the same path length which I expect
    if len(path_lee) != len(path_astar):
        print("Error: the two algorithms found different path lengths.")


def main():
    print("Lee vs A*")
    print()

    nets = ["VCC", "TRIG", "GND", "DISCHG"]

    for net_name in nets:
        compare_net(net_name)
    
    print()


if __name__ == '__main__':
    main()


    """
    Both algorithms find paths of the same length, which is what I expect because
    both should find shortest paths. But A* visits far fewer cells. For example, on
    the VCC net, Lee visits 226 cells while A* visits only 56. On DISCHG, Lee visits 
    154 cells while A* visits only 31. So my results show that A* keeps correctness but 
    improves efficiency by guiding the search toward the target.
    """