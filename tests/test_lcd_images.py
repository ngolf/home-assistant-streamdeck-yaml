from home_assistant_streamdeck_yaml import (
    LCD_ICON_SIZE_X,
    LCD_ICON_SIZE_Y,
    _draw_light_temperature_bar,
    _draw_light_brightness_bar,
    _draw_room_temperature_bar,
)
from PIL import Image, ImageChops
import os
import pytest

# Define parameter sets for each function
LIGHT_TEMPERATURE_PARAMS = [
    {
        "name": "default",
        "current_temperature": 4500,
        "set_temperature": 5000,
        "min_temperature": 2202,
        "max_temperature": 6535,
        "size": (LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y),
    },
    {
        "name": "narrow_range",
        "current_temperature": 3500,
        "set_temperature": 4000,
        "min_temperature": 2700,
        "max_temperature": 5000,
        "size": (LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y),
    },
    {
        "name": "none_current",
        "current_temperature": None,
        "set_temperature": 3000,
        "min_temperature": 2202,
        "max_temperature": 6535,
        "size": (LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y),
    },
    {
        "name": "custom_size",
        "current_temperature": 4500,
        "set_temperature": 5000,
        "min_temperature": 2202,
        "max_temperature": 6535,
        "size": (200, 40),
    },
]

LIGHT_BRIGHTNESS_PARAMS = [
    {
        "name": "default",
        "current_brightness": 50,
        "set_brightness": 100,
        "min_brightness": 0,
        "max_brightness": 255,
        "size": (LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y),
    },
    {
        "name": "custom_range",
        "current_brightness": 150,
        "set_brightness": 180,
        "min_brightness": 10,
        "max_brightness": 200,
        "size": (LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y),
    },
    {
        "name": "none_set",
        "current_brightness": 100,
        "set_brightness": None,
        "min_brightness": 0,
        "max_brightness": 255,
        "size": (LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y),
    },
    {
        "name": "custom_size",
        "current_brightness": 50,
        "set_brightness": 100,
        "min_brightness": 0,
        "max_brightness": 255,
        "size": (200, 40),
    },
]

ROOM_TEMPERATURE_PARAMS = [
    {
        "name": "default",
        "current_temperature": 20,
        "set_temperature": 22,
        "min_temperature": 10,
        "max_temperature": 30,
        "size": (LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y),
    },
    {
        "name": "narrow_range",
        "current_temperature": 18,
        "set_temperature": 20,
        "min_temperature": 15,
        "max_temperature": 25,
        "size": (LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y),
    },
    {
        "name": "none_current",
        "current_temperature": None,
        "set_temperature": 24,
        "min_temperature": 10,
        "max_temperature": 30,
        "size": (LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y),
    },
    {
        "name": "custom_size",
        "current_temperature": 20,
        "set_temperature": 22,
        "min_temperature": 10,
        "max_temperature": 30,
        "size": (200, 40),
    },
]

# Ensure output directories exist
os.makedirs("tests", exist_ok=True)
os.makedirs("tests/diffs", exist_ok=True)

def save_image(image, function_name, params):
    """Save an image with a descriptive filename based on function and parameters."""
    name = params.get("name", "unnamed")
    filename = f"tests/{function_name}_{name}.png"
    image.save(filename)
    print(f"Saved image: {filename}")

def compare_images(image, reference_path, diff_path):
    """Compare two images and save a diff image if they differ."""
    if not os.path.exists(reference_path):
        raise FileNotFoundError(f"Reference image not found: {reference_path}")
    
    reference = Image.open(reference_path)
    if image.size != reference.size:
        raise AssertionError(f"Image size {image.size} does not match reference size {reference.size}")
    
    diff = ImageChops.difference(image, reference)
    diff_bbox = diff.getbbox()
    if diff_bbox:
        # Non-empty diff, save it
        diff.save(diff_path)
        raise AssertionError(f"Images differ, diff saved to {diff_path}")
    
    return True

def test_draw_light_temperature_bar():
    """Test _draw_light_temperature_bar by comparing generated images with saved references."""
    for params in LIGHT_TEMPERATURE_PARAMS:
        name = params["name"]
        # Exclude 'name' from parameters passed to the function
        draw_params = {k: v for k, v in params.items() if k != "name"}
        image = _draw_light_temperature_bar(**draw_params)
        assert image.size == params["size"], (
            f"Expected image size {params['size']}, but got {image.size} for {name}"
        )
        reference_path = f"tests/draw_light_temperature_bar_{name}.png"
        diff_path = f"tests/diffs/draw_light_temperature_bar_{name}_diff.png"
        compare_images(image, reference_path, diff_path)

def test_draw_light_brightness_bar():
    """Test _draw_light_brightness_bar by comparing generated images with saved references."""
    for params in LIGHT_BRIGHTNESS_PARAMS:
        name = params["name"]
        # Exclude 'name' from parameters passed to the function
        draw_params = {k: v for k, v in params.items() if k != "name"}
        image = _draw_light_brightness_bar(**draw_params)
        assert image.size == params["size"], (
            f"Expected image size {params['size']}, but got {image.size} for {name}"
        )
        reference_path = f"tests/draw_light_brightness_bar_{name}.png"
        diff_path = f"tests/diffs/draw_light_brightness_bar_{name}_diff.png"
        compare_images(image, reference_path, diff_path)

def test_draw_room_temperature_bar():
    """Test _draw_room_temperature_bar by comparing generated images with saved references."""
    for params in ROOM_TEMPERATURE_PARAMS:
        name = params["name"]
        # Exclude 'name' from parameters passed to the function
        draw_params = {k: v for k, v in params.items() if k != "name"}
        image = _draw_room_temperature_bar(**draw_params)
        assert image.size == params["size"], (
            f"Expected image size {params['size']}, but got {image.size} for {name}"
        )
        reference_path = f"tests/draw_room_temperature_bar_{name}.png"
        diff_path = f"tests/diffs/draw_room_temperature_bar_{name}_diff.png"
        compare_images(image, reference_path, diff_path)

if __name__ == "__main__":
    # Generate and save reference images for all parameter sets
    for params in LIGHT_TEMPERATURE_PARAMS:
        draw_params = {k: v for k, v in params.items() if k != "name"}
        image = _draw_light_temperature_bar(**draw_params)
        save_image(image, "draw_light_temperature_bar", params)
    
    for params in LIGHT_BRIGHTNESS_PARAMS:
        draw_params = {k: v for k, v in params.items() if k != "name"}
        image = _draw_light_brightness_bar(**draw_params)
        save_image(image, "draw_light_brightness_bar", params)
    
    for params in ROOM_TEMPERATURE_PARAMS:
        draw_params = {k: v for k, v in params.items() if k != "name"}
        image = _draw_room_temperature_bar(**draw_params)
        save_image(image, "draw_room_temperature_bar", params)