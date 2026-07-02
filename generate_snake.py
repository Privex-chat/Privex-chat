import os

# --- Configuration ---
CELL_SIZE = 14
GAP = 2
STEP = CELL_SIZE + GAP # 16
ROWS = 7
COLS = 44 # 44 * 16 = 704

WIDTH = 800
HEIGHT = 200

OFFSET_X = (WIDTH - (COLS * STEP)) // 2
OFFSET_Y = (HEIGHT - (ROWS * STEP)) // 2

# Flat Retro Palette
COLOR_BG = "#0d1117"       # Pure dark background
COLOR_EMPTY = "#161b22"    # Faint grid dot color
COLOR_FOOD = "#ff7b72"     # Flat red food
COLOR_SNAKE = "#67e8f9"    # Flat cyan snake

# Generate path
path_coords = []
def add_path(start, end):
    dc = 1 if end[0] > start[0] else (-1 if end[0] < start[0] else 0)
    dr = 1 if end[1] > start[1] else (-1 if end[1] < start[1] else 0)
    c, r = start
    while c != end[0] or r != end[1]:
        c += dc
        r += dr
        path_coords.append((c, r))

# Classic snake winding path (pixel perfect grid coordinates)
curr = (-15, 3) # Start far off-screen
path_coords.append(curr)
add_path(curr, (10, 3))
add_path((10, 3), (10, 6))
add_path((10, 6), (20, 6))
add_path((20, 6), (20, 1))
add_path((20, 1), (30, 1))
add_path((30, 1), (30, 4))
add_path((30, 4), (40, 4))
add_path((40, 4), (40, 2))
add_path((40, 2), (55, 2)) # Exit far right off-screen

SNAKE_LENGTH = 10 
TOTAL_STEPS = len(path_coords)
DURATION = 8.0 # seconds for the full loop (faster, more retro tick rate)

svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">
  <!-- Flat background, no rounded corners -->
  <rect width="100%" height="100%" fill="{COLOR_BG}" />
  <g>
"""

# Draw the background grid (simple faint 2x2 dots for a classic aesthetic)
for r in range(ROWS):
    for c in range(COLS):
        x = OFFSET_X + c * STEP + (CELL_SIZE // 2) - 1
        y = OFFSET_Y + r * STEP + (CELL_SIZE // 2) - 1
        svg_content += f'    <rect x="{x}" y="{y}" width="2" height="2" fill="{COLOR_EMPTY}" />\n'

# Food targets
food_targets = [15, 30, 45, 60]
for f_idx in food_targets:
    if f_idx < len(path_coords):
        fx, fy = path_coords[f_idx]
        px = OFFSET_X + fx * STEP
        py = OFFSET_Y + fy * STEP
        time_to_reach = (f_idx / TOTAL_STEPS) * DURATION
        
        # Flat square food, disappears instantly when eaten
        svg_content += f"""
    <rect x="{px}" y="{py}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{COLOR_FOOD}">
        <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{time_to_reach/DURATION:.3f};{(time_to_reach+0.001)/DURATION:.3f};1" dur="{DURATION}s" repeatCount="indefinite" />
    </rect>
"""

# Draw snake segments
for i in range(SNAKE_LENGTH):
    x_values = []
    y_values = []
    
    for t in range(TOTAL_STEPS):
        pos_idx = max(0, t - i)
        c, r = path_coords[pos_idx]
        x_values.append(str(OFFSET_X + c * STEP))
        y_values.append(str(OFFSET_Y + r * STEP))
        
    x_val_str = ";".join(x_values)
    y_val_str = ";".join(y_values)
    
    # Pure flat square for the snake (no rx/ry, no filters, no opacity fading)
    svg_content += f"""
    <rect x="-50" y="-50" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{COLOR_SNAKE}">
        <animate attributeName="x" values="{x_val_str}" calcMode="discrete" dur="{DURATION}s" repeatCount="indefinite" />
        <animate attributeName="y" values="{y_val_str}" calcMode="discrete" dur="{DURATION}s" repeatCount="indefinite" />
    </rect>
"""

svg_content += """
  </g>
</svg>
"""

os.makedirs("dist", exist_ok=True)
with open("dist/custom-snake.svg", "w") as f:
    f.write(svg_content)

print("Generated dist/custom-snake.svg")
