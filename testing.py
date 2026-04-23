
from circuits import build_555_timer

grid, pads = build_555_timer()

# What are the neighbors of the source?
source = pads['VCC'][0]
print(f"Source: {source}")
print(f"Neighbors of source: {grid.neighbors(*source)}")

# What state is each pad at column 10?
for row in range(9, 13):
    cell = grid.get(10, row)
    print(f"Cell (10, {row}): state = {cell.state}")


# ### testing_lee.py
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
