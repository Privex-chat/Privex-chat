import os

# --- Configuration ---
CELL_SIZE = 14
GAP = 4
STEP = CELL_SIZE + GAP # 18
ROWS = 7
COLS = 44 # 44 * 18 = 792, fits in 800px width

WIDTH = 800
HEIGHT = 200

OFFSET_X = (WIDTH - (COLS * STEP)) // 2 + 2 # Center horizontally
OFFSET_Y = (HEIGHT - (ROWS * STEP)) // 2 + 2 # Center vertically

COLOR_BG = "#0d1117"
COLOR_EMPTY = "#161b22"
COLOR_FOOD = "#ff7b72"
COLOR_SNAKE_HEAD = "#ffffff"
COLOR_SNAKE_BODY = "#67e8f9"

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

# Path starts completely off screen to the left, exits completely off screen to the right
curr = (-10, 3)
path_coords.append(curr)
add_path(curr, (8, 3))
add_path((8, 3), (8, 6))
add_path((8, 6), (16, 6))
add_path((16, 6), (16, 1))
add_path((16, 1), (28, 1))
add_path((28, 1), (28, 5))
add_path((28, 5), (36, 5))
add_path((36, 5), (36, 2))
add_path((36, 2), (52, 2)) # Exits far right

SNAKE_LENGTH = 7
TOTAL_STEPS = len(path_coords)
DURATION = 7.0 # seconds for the full loop

svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
    <clipPath id="gridClip">
      <rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="10" />
    </clipPath>
  </defs>

  <rect width="100%" height="100%" fill="{COLOR_BG}" rx="10"/>
  
  <g clip-path="url(#gridClip)">
"""

# Draw the background grid
import random
random.seed(42) # Deterministic random for empty grid dots

for r in range(ROWS):
    for c in range(COLS):
        x = OFFSET_X + c * STEP
        y = OFFSET_Y + r * STEP
        fill = COLOR_EMPTY
        
        # Add some subtle random "contributions"
        rand = random.random()
        if rand > 0.98: fill = "#1cb3c8"
        elif rand > 0.95: fill = "#0f6975"
        elif rand > 0.90: fill = "#07373f"
        
        svg_content += f'    <rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{fill}" rx="3" />\n'

# Draw food that the snake "eats"
# We place food along the path right before the snake gets there
# Let's pick a few spots on the path:
food_targets = [15, 30, 45, 60] # Indices in path_coords

for f_idx in food_targets:
    if f_idx < len(path_coords):
        fx, fy = path_coords[f_idx]
        px = OFFSET_X + fx * STEP
        py = OFFSET_Y + fy * STEP
        
        # Calculate when the snake head reaches this food
        # It takes DURATION seconds to do TOTAL_STEPS
        time_to_reach = (f_idx / TOTAL_STEPS) * DURATION
        
        # Food vanishes when head reaches it
        svg_content += f"""
    <rect x="{px}" y="{py}" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{COLOR_FOOD}" rx="3" filter="url(#glow)">
        <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{time_to_reach/DURATION:.3f};{(time_to_reach+0.01)/DURATION:.3f};1" dur="{DURATION}s" repeatCount="indefinite" />
    </rect>
"""

# Draw snake segments
for i in range(SNAKE_LENGTH):
    color = COLOR_SNAKE_HEAD if i == 0 else COLOR_SNAKE_BODY
    
    # Generate the x and y value strings for this segment
    x_values = []
    y_values = []
    
    for t in range(TOTAL_STEPS):
        # Position index is t - i, clamped to 0
        pos_idx = max(0, t - i)
        c, r = path_coords[pos_idx]
        x_values.append(str(OFFSET_X + c * STEP))
        y_values.append(str(OFFSET_Y + r * STEP))
        
    x_val_str = ";".join(x_values)
    y_val_str = ";".join(y_values)
    
    svg_content += f"""
    <rect x="-50" y="-50" width="{CELL_SIZE}" height="{CELL_SIZE}" fill="{color}" rx="3" filter="url(#glow)">
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
