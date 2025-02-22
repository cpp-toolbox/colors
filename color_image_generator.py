import re
import json
import math
from PIL import Image

# Read colors from colors.hpp
hpp_file = "colors.hpp"
color_pattern = re.compile(r"glm::vec3\s+(\w+)\s*=\s*glm::vec3\((\d+)\s*/\s*d,\s*(\d+)\s*/\s*d,\s*(\d+)\s*/\s*d\)")

colors = []
with open(hpp_file, "r") as file:
    for line in file:
        match = color_pattern.search(line)
        if match:
            name, r, g, b = match.groups()
            colors.append((name, int(r), int(g), int(b)))

# Determine smallest power-of-two size
num_colors = len(colors)
n = 2 ** math.ceil(math.log2(math.ceil(math.sqrt(num_colors))))

# Create an image
img = Image.new("RGB", (n, n), (0, 0, 0))  # Fill with black
atlas = {"sub_textures": {}}

for i, (name, r, g, b) in enumerate(colors):
    x, y = i % n, i // n
    img.putpixel((x, y), (r, g, b))
    atlas["sub_textures"][name] = {"x": x, "y": y, "width": 1, "height": 1}

# Save image and JSON
img.save("all_colors.png")

with open("all_colors.json", "w") as json_file:
    json.dump(atlas, json_file, indent=2)

print(f"Generated all_colors.png ({n}x{n}) and all_colors_atlas.json with {num_colors} colors.")
