
# from circuits import build_555_timer
# grid, pads = build_555_timer()
# grid.print_ascii()
# print(pads)


### testing_lee.py
from circuits import build_555_timer
from lee      import find_path

grid, pads = build_555_timer()

# Route VCC: pin 8 to pin 4 (the two VCC pins on the chip)
source, target = pads['VCC'][0], pads['VCC'][1]
print(f"Routing from {source} to {target}")

path = find_path(grid, source, target)
if path is None:
    print("No path found!")
else:
    print(f"Path found! Length: {len(path)} cells")
    print(f"Path: {path}")
    grid.mark_trace(path)
    grid.print_ascii()
