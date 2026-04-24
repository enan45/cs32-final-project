
# from circuits import build_555_timer

# grid, pads = build_555_timer()

# # What are the neighbors of the source?
# source = pads['VCC'][0]
# print(f"Source: {source}")
# print(f"Neighbors of source: {grid.neighbors(*source)}")

# # What state is each pad at column 10?
# for row in range(9, 13):
#     cell = grid.get(10, row)
#     print(f"Cell (10, {row}): state = {cell.state}")


# # ### testing_lee.py
# from circuits import build_555_timer
# from lee      import find_path

# grid, pads = build_555_timer()

# # Route VCC: pin 8 to pin 4 (the two VCC pins on the chip)
# source, target = pads['VCC'][0], pads['VCC'][1]
# print(f"Routing from {source} to {target}")

# path = find_path(grid, source, target)
# if path is None:
#     print("No path found!")
# else:
#     print(f"Path found! Length: {len(path)} cells")
#     print(f"Path: {path}")
#     grid.mark_trace(path)
#     grid.print_ascii()



# TRIG connects pin 2 and pin 6 — diagonally opposite corners of the chip
# source, target = pads['TRIG'][0], pads['TRIG'][1]
# print(f"Routing from {source} to {target}")

# path = find_path(grid, source, target)
# if path is None:
#     print("No path found!")
# else:
#     print(f"Path found! Length: {len(path)} cells")
#     print(f"Path: {path}")
#     grid.mark_trace(path)
#     grid.print_ascii()


## main.py
### main.py
"""Run the live PCB router visualization on the 555 timer circuit."""

from circuits  import build_555_timer
from visualize import visualize_route


def main():
    grid, pads = build_555_timer()

    # Pick a net to route — TRIG is the visually dramatic one since it
    # has to snake around the chip from pin 2 to pin 6.
    net = 'TRIG'
    source = pads[net][0]   # pin 2 (left side)
    target = pads[net][1]   # pin 6 (right side)

    visualize_route(grid, source, target, net_name=net)


if __name__ == '__main__':
    main()
