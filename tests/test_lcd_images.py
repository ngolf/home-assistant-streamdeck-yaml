from home_assistant_streamdeck_yaml import (
    LCD_ICON_SIZE_X,
    LCD_ICON_SIZE_Y,
    _draw_light_temperature_bar,
)


def test_draw_light_temperature_bar():
    """Test the _draw_light_temperature_bar function by generating and saving a sample image.
    Verifies that the image is generated with the default size (LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y).
    """
    # Generate the image with sample parameters
    image = _draw_light_temperature_bar(
        current_temperature=4500,
        set_temperature=5000,
    )

    # Verify image size matches default parameters
    assert image.size == (LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y), (
        f"Expected image size {(LCD_ICON_SIZE_X, LCD_ICON_SIZE_Y)}, but got {image.size}"
    )

    # Save the image to the tests folder
    image.save("tests/test_temperature_bar.png")


if __name__ == "__main__":
    test_draw_light_temperature_bar()
