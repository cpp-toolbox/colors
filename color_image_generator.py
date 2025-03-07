import re
import json
import math
import argparse
from PIL import Image, ImageDraw, ImageFont

def parse_colors(hpp_file):
    color_pattern = re.compile(r"glm::vec3\s+(\w+)\s*=\s*glm::vec3\((\d+)\s*/\s*d,\s*(\d+)\s*/\s*d,\s*(\d+)\s*/\s*d\)")
    colors = []
    with open(hpp_file, "r") as file:
        for line in file:
            match = color_pattern.search(line)
            if match:
                name, r, g, b = match.groups()
                colors.append((name, int(r), int(g), int(b)))
    return colors

def generate_atlas(colors, pixel_size, legend=False):
    num_colors = len(colors)
    n = 2 ** math.ceil(math.log2(math.ceil(math.sqrt(num_colors))))
    img_size = n * pixel_size
    
    img = Image.new("RGB", (img_size, img_size), (0, 0, 0))
    draw = ImageDraw.Draw(img)
    atlas = {"sub_textures": {}}
    
    # Load font only if legend is enabled
    if legend:
        try:
            font = ImageFont.truetype("arial.ttf", pixel_size // 4)
        except IOError:
            font = ImageFont.load_default()
    
    for i, (name, r, g, b) in enumerate(colors):
        x, y = (i % n) * pixel_size, (i // n) * pixel_size
        
        for dx in range(pixel_size):
            for dy in range(pixel_size):
                img.putpixel((x + dx, y + dy), (r, g, b))
        
        atlas["sub_textures"][name] = {"x": x, "y": y, "width": pixel_size, "height": pixel_size}
        
        if legend:
            text_color = (255, 255, 255) if (r + g + b) / 3 < 128 else (0, 0, 0)
            text_width, text_height = draw.textbbox((0, 0), name, font=font)[2:]  # Get text size
            text_position = (
                x + (pixel_size - text_width) // 2,
                y + (pixel_size - text_height) // 2,
            )
            draw.text(text_position, name, fill=text_color, font=font)
    
    return img, atlas

def main():
    parser = argparse.ArgumentParser(description="Generate a color atlas from colors.hpp")
    parser.add_argument("hpp_file", help="Path to colors.hpp")
    parser.add_argument("pixel_size", type=int, help="Size of each color square in pixels")
    parser.add_argument("--legend", action="store_true", help="Generate a legend with color names")
    args = parser.parse_args()
    
    colors = parse_colors(args.hpp_file)
    img, atlas = generate_atlas(colors, args.pixel_size, args.legend)
    
    # Save the image
    img.save("all_colors.png")
    
    # If legend is enabled, save the image with legend as well
    if args.legend:
        img.save("all_colors_legend.png")
    
    # Save the atlas data to JSON
    with open("all_colors.json", "w") as json_file:
        json.dump(atlas, json_file, indent=2)
    
    print(f"Generated all_colors.png ({img.width}x{img.height}) and all_colors.json with {len(colors)} colors.")
    if args.legend:
        print("Legend added to the image and saved as all_colors_legend.png.")

if __name__ == "__main__":
    main()
