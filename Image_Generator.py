from PIL import Image, ImageDraw
import json
from datetime import datetime

def create_grid(width, height):
    # Create a blank white image with the specified width and height
    return Image.new("RGB", (width, height), "white")

def fill_color(draw, weekday, positions_and_colors, cell_width, cell_height):
    # Sort the positions and colors based on time
    sorted_positions = sorted(positions_and_colors.keys(), key=lambda x: float(x))
    for i in range(len(sorted_positions)):
        # Calculate the start and end time for each color segment
        start = sorted_positions[i - 1] if i != 0 else "0000"
        end = sorted_positions[i]
        color_info = positions_and_colors[end]

        start_hour, start_minute = divmod(int(start), 100)
        end_hour, end_minute = divmod(int(end), 100)

        start_float = start_hour + start_minute / 60
        end_float = end_hour + end_minute / 60

        # Calculate the starting position (x) and y position based on the weekday
        x = start_float * cell_width
        y = weekday * cell_height
        width = (end_float - start_float) * cell_width

        # Calculate total weight for the color segment
        total_weight = sum(int(weight.split('-')[0]) if '-' in weight else 1 for weight in color_info[0])
        height_per_weight = cell_height / total_weight if total_weight > 0 else 0

        # Draw each color segment with the corresponding height based on its weight
        for color_spec in color_info[0]:
            if '-' in color_spec:
                weight, color = color_spec.split("-")
                weight = int(weight)
            else:
                weight = 1
                color = color_spec

            # Calculate the height for the current color segment based on its weight
            cell_height_color = weight * height_per_weight
            draw.rectangle([x, y, x + width, y + cell_height_color], fill=color)
            y += cell_height_color

def draw_grid_border(draw, grid_width, grid_height, cell_width, cell_height, border_width):
    # Draw borders for each row and column in the grid
    for row in range(7):
        x1 = 0
        y1 = int(row * cell_height)
        x2 = grid_width
        y2 = int((row + 1) * cell_height)
        draw.rectangle([x1, y1, x2, y2], outline="black", width=border_width)

    for col in range(24):
        x1 = int(col * cell_width)
        y1 = 0
        x2 = int((col + 1) * cell_width)
        y2 = grid_height
        draw.rectangle([x1, y1, x2, y2], outline="black", width=border_width)

def display_and_save(image, filename):
    # Display the generated image and save it to a file
    image.show()
    image.save(filename)

def read_json(file_path):
    # Read JSON data from the specified file
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

# Set up grid dimensions and border width
grid_width = 1980
grid_height = 1080
border_width = 3

# Create a blank grid image
grid_image = create_grid(grid_width, grid_height)
draw = ImageDraw.Draw(grid_image)
filename = "data_vis"

# Read JSON data from the file (replace with your JSON file path)
json_data = read_json(f"{filename}.json")

# Iterate through each week and fill colors in the grid
for key, value in json_data.items():
    # Parse the date and get the weekday
    date_object = datetime.strptime(key, "%d %b %Y")
    weekday = date_object.weekday()
    # Fill colors for the current week
    fill_color(draw, weekday, value, grid_width / 24, grid_height / 7)

# Draw borders for the grid
draw_grid_border(draw, grid_width, grid_height, grid_width / 24, grid_height / 7, border_width)

# Display and save the final grid image
display_and_save(grid_image, f"{filename}.png")
