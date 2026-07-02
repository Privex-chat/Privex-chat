import os

svg_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200" width="800" height="200">
  <defs>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="3" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <rect width="100%" height="100%" fill="#0d1117" rx="10"/>
"""

# Draw subtle minimalist grid dots
grid_dots = ""
for x in range(20, 800, 20):
    for y in range(20, 200, 20):
        # Make a few dots slightly brighter to look like static contributions
        fill = "#161b22"
        import random
        random.seed(x * y)
        if random.random() > 0.95:
            fill = "#07373f"
        elif random.random() > 0.98:
            fill = "#0f6975"
            
        grid_dots += f'  <circle cx="{x}" cy="{y}" r="2" fill="{fill}" />\n'

svg_content += grid_dots

# Path for snake to follow
path_d = "M -40,60 L 140,60 L 140,140 L 340,140 L 340,40 L 540,40 L 540,120 L 740,120 L 740,80 L 840,80"

# Draw the path faintly as a "trail" (optional, but looks cool)
# svg_content += f'<path d="{path_d}" fill="none" stroke="#161b22" stroke-width="4" stroke-dasharray="4 4" />\n'

# Add snake segments
snake_segments = ""
num_segments = 20
base_delay = 0.08
duration = 10  # 10 seconds for a slow, aesthetic slither

for i in range(num_segments):
    delay = i * base_delay
    opacity = max(0.1, 1.0 - (i * 0.04))
    
    # Head is white, body fades into cyan
    if i == 0:
        color = "#ffffff"
        size = 6
    elif i < 3:
        color = "#e0fbfc"
        size = 5.5
    else:
        color = "#67e8f9"
        size = max(2, 5 - (i * 0.15))
        
    snake_segments += f"""
    <circle r="{size}" fill="{color}" opacity="{opacity}" filter="url(#glow)">
        <animateMotion dur="{duration}s" repeatCount="indefinite" begin="-{delay}s" path="{path_d}" />
    </circle>
"""

# Add a little "food" dot that the snake is heading towards
# Wait, if the snake loops, the food would be eaten and reappear. 
# We can just put a glowing dot at (740, 80) which it hits near the end!
svg_content += """
    <circle cx="740" cy="80" r="4" fill="#ff7b72" filter="url(#glow)">
        <animate attributeName="opacity" values="0.3;1;0.3" dur="2s" repeatCount="indefinite" />
    </circle>
"""

svg_content += snake_segments
svg_content += "</svg>"

os.makedirs("dist", exist_ok=True)
with open("dist/custom-snake.svg", "w") as f:
    f.write(svg_content)

print("Generated dist/custom-snake.svg")
