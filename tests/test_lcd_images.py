"""Test module for image drawing functions in Home Assistant StreamDeck YAML.

This module tests the `_draw_light_temperature_bar`, `_draw_light_brightness_bar`, and
`_draw_room_temperature_bar` functions by generating images with various parameter sets,
verifying their sizes, and comparing them against saved reference images. Differences
are saved as diff images for debugging.
"""

from pathlib import Path
from typing import Any

from PIL import Image, ImageChops

from home_assistant_streamdeck_yaml import (
    LCD_ICON_SIZE_X,
    LCD_ICON_SIZE_Y,
    _draw_light_brightness_bar,
    _draw_light_temperature_bar,
    _draw_room_temperature_bar,
)

# Define directory paths
TEST_PATH: Path = Path("tests")
DIFF_PATH: Path = Path("tests/diffs")

# Define parameter sets for each function
LIGHT_TEMPERATURE_PARAMS: list[dict[str, Any]] = [
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

LIGHT_BRIGHTNESS_PARAMS: list[dict[str, Any]] = [
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

ROOM_TEMPERATURE_PARAMS: list[dict[str, Any]] = [
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
TEST_PATH.mkdir(exist_ok=True, parents=True)
DIFF_PATH.mkdir(exist_ok=True, parents=True)


def save_image(image: Image.Image, function_name: str, params: dict[str, Any]) -> None:
    """Save an image with a descriptive filename based on function and parameters."""
    name: str = params.get("name", "unnamed")
    filename: Path = TEST_PATH / f"{function_name}_{name}.png"
    image.save(filename)
    print(f"Saved image: {filename}")


def compare_images(image: Image.Image, reference_path: Path, diff_path: Path) -> bool:
    """Compare two images and save a diff image if they differ."""
    if not reference_path.exists():
        msg = f"Reference image not found: {reference_path}"
        raise FileNotFoundError(msg)

    reference: Image.Image = Image.open(reference_path)
    if image.size != reference.size:
        msg = f"Image size {image.size} does not match reference size {reference.size}"
        raise AssertionError(msg)

    diff: Image.Image = ImageChops.difference(image, reference)
    diff_bbox = diff.getbbox()
    if diff_bbox:
        # Non-empty diff, save it
        diff.save(diff_path)
        msg = f"Images differ, diff saved to {diff_path}"
        raise AssertionError(msg)

    return True


def test_draw_light_temperature_bar() -> None:
    """Test _draw_light_temperature_bar by comparing generated images with saved references."""
    for params in LIGHT_TEMPERATURE_PARAMS:
        name: str = params["name"]
        # Exclude 'name' from parameters passed to the function
        draw_params: dict[str, Any] = {k: v for k, v in params.items() if k != "name"}
        image: Image.Image = _draw_light_temperature_bar(**draw_params)
        assert image.size == params["size"], (
            f"Expected image size {params['size']}, but got {image.size} for {name}"
        )
        reference_path: Path = TEST_PATH / f"draw_light_temperature_bar_{name}.png"
        diff_path: Path = DIFF_PATH / f"draw_light_temperature_bar_{name}_diff.png"
        compare_images(image, reference_path, diff_path)


def test_draw_light_brightness_bar() -> None:
    """Test _draw_light_brightness_bar by comparing generated images with saved references."""
    for params in LIGHT_BRIGHTNESS_PARAMS:
        name: str = params["name"]
        # Exclude 'name' from parameters passed to the function
        draw_params: dict[str, Any] = {k: v for k, v in params.items() if k != "name"}
        image: Image.Image = _draw_light_brightness_bar(**draw_params)
        assert image.size == params["size"], (
            f"Expected image size {params['size']}, but got {image.size} for {name}"
        )
        reference_path: Path = TEST_PATH / f"draw_light_brightness_bar_{name}.png"
        diff_path: Path = DIFF_PATH / f"draw_light_brightness_bar_{name}_diff.png"
        compare_images(image, reference_path, diff_path)


def test_draw_room_temperature_bar() -> None:
    """Test _draw_room_temperature_bar by comparing generated images with saved references."""
    for params in ROOM_TEMPERATURE_PARAMS:
        name: str = params["name"]
        # Exclude 'name' from parameters passed to the function
        draw_params: dict[str, Any] = {k: v for k, v in params.items() if k != "name"}
        image: Image.Image = _draw_room_temperature_bar(**draw_params)
        assert image.size == params["size"], (
            f"Expected image size {params['size']}, but got {image.size} for {name}"
        )
        reference_path: Path = TEST_PATH / f"draw_room_temperature_bar_{name}.png"
        diff_path: Path = DIFF_PATH / f"draw_room_temperature_bar_{name}_diff.png"
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
