from PIL import Image, ImageDraw
import json
from datetime import datetime
import math


def create_grid(width, height):
    """
    Create a new image grid with the specified width and height.
    """
    return Image.new("RGB", (width, height), "white")


def draw_grid_border(draw, grid_width, grid_height, cell_width, cell_height, border_width):
    """
    Draw borders for each row and column in the grid.
    """
    # Draw borders for each row
    for row in range(7):
        x1 = 0
        y1 = int(row * cell_height)
        x2 = grid_width
        y2 = int((row + 1) * cell_height)
        draw.rectangle([x1, y1, x2, y2], outline="black", width=border_width)

    # Draw borders for each column
    for col in range(24):
        x1 = int(col * cell_width)
        y1 = 0
        x2 = int((col + 1) * cell_width)
        y2 = grid_height
        draw.rectangle([x1, y1, x2, y2], outline="black", width=border_width)


def fill_color(draw, weekday, positions_and_colors, cell_width, cell_height):
    """
    Fill colors in the grid based on the provided positions_and_colors data.
    """
    sorted_positions = sorted(positions_and_colors.keys(), key=lambda x: float(x))
    for i in range(len(sorted_positions)):
        # Extract time range and color information
        start = sorted_positions[i - 1] if i != 0 else "0000"
        end = sorted_positions[i]
        color_info = positions_and_colors[end]

        # Convert time to float for positioning
        start_hour, start_minute = divmod(int(start), 100)
        end_hour, end_minute = divmod(int(end), 100)
        start_float = start_hour + start_minute / 60
        end_float = end_hour + end_minute / 60

        # Calculate initial positions
        x = start_float * cell_width
        y = weekday * cell_height
        width = (end_float - start_float) * cell_width

        # Calculate total weight for color distribution
        total_weight = sum(int(weight.split('-')[0]) if '-' in weight else 1 for weight in color_info[0])
        height_per_weight = cell_height / total_weight if total_weight > 0 else 0

        for color_spec in color_info[0]:
            if '-' in color_spec:
                weight, color = color_spec.split("-")
                weight = int(weight)
            else:
                weight = 1
                color = color_spec

            cell_height_color = weight * height_per_weight

            if ',' in color:
                # Draw a 5x7 grid for multiple colors
                sub_colors = color.split(',')
                cell_width_sub = width / 5
                cell_height_sub = cell_height_color / 7

                for row in range(7):
                    for col in range(5):
                        # Repeat colors if there are fewer than 7
                        cell_color = sub_colors[(col + row) % len(sub_colors)]
                        # Draw sub-cell
                        draw.rectangle(
                            [x + col * cell_width_sub, y + row * cell_height_sub, x + (col + 1) * cell_width_sub,
                             y + (row + 1) * cell_height_sub],
                            fill=cell_color
                        )

                y += cell_height_color
            else:
                # Draw a single cell for a single color
                draw.rectangle([x, y, x + width, y + cell_height_color], fill=color)
                y += cell_height_color


def display_and_save(image, filename):
    """
    Display the image and save it to a file.
    """
    global last_week_bool
    if last_week_bool: image.show()
    image.save(filename)


def read_json(file_path):
    """
    Read JSON data from a file.
    """
    with open(file_path, "r") as file:
        data = json.load(file)
    return data


def generate_week_image(json_data, start_date):
    """
    Generate an image for the provided week based on JSON data.
    """
    # Set up grid dimensions and border width
    grid_width = 1920
    grid_height = 1080
    border_width = 3

    # Create a new image
    grid_image = create_grid(grid_width, grid_height)
    draw = ImageDraw.Draw(grid_image)

    # Iterate through each time entry and fill colors
    for key, value in json_data.items():
        date_object = datetime.strptime(key, "%d %b %Y")
        weekday = date_object.weekday()
        fill_color(draw, weekday, value, grid_width / 24, grid_height / 7)

    # Draw borders for the grid
    draw_grid_border(draw, grid_width, grid_height, grid_width / 24, grid_height / 7, border_width)

    # Display and save the image
    display_and_save(grid_image, f"{(str(start_date)[:4] + str(start_date)[-4:]).replace('_', '').replace(' ', '')}.png")


# Read JSON data from the file (replace with your JSON file path)
json_data = read_json("data_vis.json")

current_week_start = None
current_week_data = {}

last_day = [datetime.strptime(key, "%d %b %Y").day for key, value in json_data.items()][-1]
last_week_bool = False
# Print the result


# Iterate through each week and generate images
for key, value in json_data.items():
    date_object = datetime.strptime(key, "%d %b %Y")
    week_date = date_object.strftime("%d %b %Y")

    if current_week_start is None:
        current_week_start = date_object

    if datetime.strptime(key, "%d %b %Y").day == last_day:
        last_week_bool = True


    # Get the weekday
    weekday = date_object.weekday()
    current_week_data[key] = value

    # Check if it's the last day of the week (Sunday)
    if weekday == 6 or last_week_bool:
        # Generate the image for the current week
        generate_week_image(current_week_data, current_week_start.strftime("%d %b %Y"))
        current_week_start = None
        current_week_data = {}
