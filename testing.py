
# ### main.py
# """Run the live PCB router visualization on the 555 timer circuit."""

# from circuits  import build_555_timer
# from visualize import visualize_route


# def main():
#     grid, pads = build_555_timer()
    
#     # Pick a net to route — TRIG is the visually dramatic one since it
#     # has to snake around the chip from pin 2 to pin 6.
#     net = 'TRIG'
#     source = pads[net][0]   # pin 2 (left side)
#     target = pads[net][1]   # pin 6 (right side)
    
#     visualize_route(grid, source, target, net_name=net)


# if __name__ == '__main__':
#     main()

    ### testing.py
# from circuits import build_555_timer
# from lee      import find_path


# def demo_route(net_name):
#     grid, pads = build_555_timer()
#     source = pads[net_name][0]
#     target = pads[net_name][1]
    
#     print(f"\n=== Routing net '{net_name}' from {source} to {target} ===")
    
#     path, stats = find_path(grid, source, target)
    
#     if path is None:
#         print(f"No path found for {net_name}.")
#         return
    
#     print(f"Path found! Length: {len(path)} cells  "
#       f"(visited {stats['visited']} cells in {stats['iterations']} iterations)")
#     print(f"Route: {path}")
    
#     grid.mark_trace(path)
#     grid.print_ascii()


# def main():
#     demo_route('VCC')
#     demo_route('TRIG')


# if __name__ == '__main__':
#     main()







from circuits import build_555_timer
from astar import find_path

grid, netlist = build_555_timer()

# Route TRIG's first segment, mark it, then try second segment
seg1_src, seg1_tgt = netlist['TRIG'][0], netlist['TRIG'][1]
seg2_src, seg2_tgt = netlist['TRIG'][1], netlist['TRIG'][2]

p1, _ = find_path(grid, seg1_src, seg1_tgt)
print(f"Seg 1: {len(p1) if p1 else 'FAIL'} cells")
grid.mark_trace(p1)

p2, _ = find_path(grid, seg2_src, seg2_tgt)
print(f"Seg 2: {len(p2) if p2 else 'FAIL'} cells")