"""Test App Home_assistant_streamdeck_yaml for Streamdeck plus."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
import websockets
from PIL import Image
from StreamDeck.Devices.StreamDeck import DialEventType
from StreamDeck.Devices.StreamDeckPlus import StreamDeckPlus

from home_assistant_streamdeck_yaml import (
    Button,
    Config,
    Dial,
    InactivityState,
    Page,
    TouchscreenEventType,
    TurnProperties,
    _on_dial_event_callback,
    _on_press_callback,
    _on_touchscreen_event_callback,
    _update_state,
    safe_load_yaml,
    update_dial_lcd,
)

ROOT = Path(__file__).parent.parent
TEST_STATE_FILENAME = ROOT / "tests" / "state_plus.json"


# TESTS FOR STREAM DECK PLUS
@pytest.fixture
def websocket_mock() -> Mock:
    """Mock websocket client protocol."""
    return Mock(spec=websockets.WebSocketClientProtocol)


@pytest.fixture
def state() -> dict[str, dict[str, Any]]:
    """State fixture."""
    with TEST_STATE_FILENAME.open("r") as f:
        return json.load(f)


@pytest.fixture
def mock_deck_plus() -> Mock:
    """Mocks a StreamDeck Plus."""
    deck_mock = Mock(spec=StreamDeckPlus)

    deck_mock.KEY_PIXEL_WIDTH = StreamDeckPlus.KEY_PIXEL_WIDTH
    deck_mock.KEY_PIXEL_HEIGHT = StreamDeckPlus.KEY_PIXEL_HEIGHT
    deck_mock.KEY_FLIP = StreamDeckPlus.KEY_FLIP
    deck_mock.KEY_ROTATION = StreamDeckPlus.KEY_ROTATION
    deck_mock.KEY_IMAGE_FORMAT = StreamDeckPlus.KEY_IMAGE_FORMAT

    deck_mock.key_image_format.return_value = {
        "size": (deck_mock.KEY_PIXEL_WIDTH, deck_mock.KEY_PIXEL_HEIGHT),
        "format": deck_mock.KEY_IMAGE_FORMAT,
        "flip": deck_mock.KEY_FLIP,
        "rotation": deck_mock.KEY_ROTATION,
    }

    deck_mock.TOUCHSCREEN_PIXEL_WIDTH = StreamDeckPlus.TOUCHSCREEN_PIXEL_WIDTH
    deck_mock.TOUCHSCREEN_PIXEL_HEIGHT = StreamDeckPlus.TOUCHSCREEN_PIXEL_HEIGHT
    deck_mock.TOUCHSCREEN_IMAGE_FORMAT = StreamDeckPlus.TOUCHSCREEN_IMAGE_FORMAT
    deck_mock.TOUCHSCREEN_FLIP = StreamDeckPlus.TOUCHSCREEN_FLIP
    deck_mock.TOUCHSCREEN_ROTATION = StreamDeckPlus.TOUCHSCREEN_ROTATION

    deck_mock.touchscreen_image_format.return_value = {
        "size": (deck_mock.TOUCHSCREEN_PIXEL_WIDTH, deck_mock.TOUCHSCREEN_PIXEL_HEIGHT),
        "format": deck_mock.TOUCHSCREEN_IMAGE_FORMAT,
        "flip": deck_mock.TOUCHSCREEN_FLIP,
        "rotation": deck_mock.TOUCHSCREEN_ROTATION,
    }

    deck_mock.key_count.return_value = 8
    deck_mock.dial_count.return_value = 4

    deck_mock.__enter__ = Mock(return_value=deck_mock)
    deck_mock.__exit__ = Mock(return_value=False)

    return deck_mock


@pytest.fixture
def dial_yaml_config() -> str:
    """Returns YAML configuration for StreamDeck Plus dials."""
    yaml_file = Path(__file__).parent / "dial_config.yaml"
    with yaml_file.open("r") as f:
        return f.read()


@pytest.fixture
def dials(dial_yaml_config: str) -> list[Dial]:
    """Order of dials for page."""
    dial_configs = safe_load_yaml(dial_yaml_config, return_included_paths=False)
    assert isinstance(dial_configs, list)
    return [Dial(**config) for config in dial_configs]


@pytest.fixture
def state_change_msg() -> dict[str, Any]:
    """Message for state change."""
    return {
        "type": "event",
        "event": {
            "event_type": "state_changed",
            "data": {
                "entity_id": "input_number.streamdeck",
                "old_state": {
                    "entity_id": "input_number.streamdeck",
                    "state": "0",
                    "attributes": {
                        "initial": None,
                        "editable": True,
                        "min": 0,
                        "max": 100,
                        "step": 1,
                        "mode": "slider",
                        "friendly_name": "StreamDeck",
                    },
                    "last_changed": "2024-04-03T14:05:05.526890+00:00",
                    "last_updated": "2024-04-03T14:05:05.526890+00:00",
                },
                "new_state": {
                    "entity_id": "input_number.streamdeck",
                    "state": 1,
                    "attributes": {
                        "initial": None,
                        "editable": True,
                        "min": 0,
                        "max": 200,
                        "step": 5,
                        "mode": "slider",
                        "friendly_name": "StreamDeck",
                    },
                    "last_changed": "2024-04-03T14:05:05.526890+00:00",
                    "last_updated": "2024-04-03T14:05:05.526890+00:00",
                },
            },
        },
    }


def test_dials(dials: list[Dial], state: dict[str, dict[str, Any]]) -> None:
    """Tests setup of pages with dials and rendering of image."""
    page = Page(name="Home", dials=dials)
    config = Config(pages=[page])
    first_page = config.to_page(0)

    key = 0
    # change number value TURN event
    d = first_page.dials[key]
    turn_state = 50.0
    d.set_turn_state(turn_state)
    # check domain type
    assert d.entity_id is not None
    # check image rendering
    d = d.rendered_template_dial(state)
    icon = d.render_lcd_image(state, key, (200, 100))
    assert isinstance(icon, Image.Image)
    # check dial_value Jinja rendering
    assert d.turn is not None
    assert d.turn.service_data is not None
    assert isinstance(float(d.turn.service_data["value"]), float)
    assert float(d.turn.service_data["value"]) == turn_state  # Verify rendered state

    d = first_page.dials[1]
    assert d.push is not None
    assert d.push.service_data is not None

    key = 2
    d = first_page.dials[key]
    # check icon rendering for mdi icons
    d = d.rendered_template_dial(state)
    icon = d.render_lcd_image(state, key, (200, 100))
    assert isinstance(icon, Image.Image)
    assert d.text is not None
    assert d.turn is not None

    key = 3
    d = first_page.dials[key]
    d = d.rendered_template_dial(state)
    icon = d.render_lcd_image(state, key, (200, 100))
    assert isinstance(icon, Image.Image)
    assert d.turn is not None


async def test_streamdeck_plus(
    mock_deck_plus: Mock,
    websocket_mock: Mock,
    state: dict[str, dict[str, Any]],
    dials: list[Dial],
    state_change_msg: dict[str, dict[str, Any]],
) -> None:
    """Tests dials, buttons and pages on streamdeck plus with state change."""
    home = Page(
        name="home",
        buttons=[
            Button(special_type="go-to-page", special_type_data="page_1"),
            Button(special_type="go-to-page", special_type_data="page_anon"),
        ],
    )

    page_1 = Page(
        name="page_1",
        dials=dials,
    )

    page_anon = Page(name="page_anon", dials=dials)
    config = Config(pages=[home, page_1], anonymous_pages=[page_anon])
    assert config._current_page_index == 0
    assert config.to_page("page_1") == page_1
    assert config.current_page() == page_1

    dial = config.dial(0)
    assert dial is not None
    dial = dial.rendered_template_dial(state)
    assert dial.entity_id == "input_number.streamdeck"
    assert dial.turn is not None
    assert dial.turn.service == "input_number.set_value"

    # set TurnProperties as a TurnProperties object
    dial.turn.properties = TurnProperties(
        min=0,
        max=100,
        step=1,
        state=0.0,
        service_attribute="value",
    )

    # gets attributes of dial and checks if state is correct
    update_dial_lcd(mock_deck_plus, 0, config, state)
    dial_val = {
        "min": dial.turn.properties.min,
        "max": dial.turn.properties.max,
        "step": dial.turn.properties.step,
        "state": dial.turn.properties.state,
    }
    assert isinstance(dial_val, dict)
    dial_state = dial_val["state"]
    assert dial_state is not None
    # Fires dial event and increments state by 1
    inactivity_state = InactivityState()
    dial_event = _on_dial_event_callback(
        inactivity_state,
        websocket_mock,
        state,
        config,
    )
    await dial_event(mock_deck_plus, 0, DialEventType.TURN, 1)
    # Test update state
    _update_state(state, state_change_msg, config, mock_deck_plus)
    # Check if state changed for input_number
    assert float(state["input_number.streamdeck"]["state"]) == dial_state + 1

    # test update attributes
    turn_max_property = 200
    dial.turn.properties.max = turn_max_property
    turn_step_property = 5
    dial.turn.properties.step = turn_step_property
    updated_attributes = {
        "min": dial.turn.properties.min,
        "max": dial.turn.properties.max,
        "step": dial.turn.properties.step,
    }
    assert updated_attributes["max"] == turn_max_property
    assert updated_attributes["step"] == turn_step_property
    assert updated_attributes["min"] == 0


async def test_touchscreen(
    mock_deck_plus: Mock,
    websocket_mock: Mock,
    state: dict[str, dict[str, Any]],
    dials: list[Dial],
) -> None:
    """Test touchscreen events for dial."""
    home = Page(
        name="home",
        buttons=[
            Button(special_type="go-to-page", special_type_data="page_1"),
            Button(special_type="go-to-page", special_type_data="page_anon"),
        ],
    )

    page_1 = Page(
        name="page_1",
        dials=dials,
    )

    page_anon = Page(name="page_anon", dials=dials)
    config = Config(pages=[home, page_1], anonymous_pages=[page_anon])
    assert config._current_page_index == 0
    assert config.current_page() == home
    inactivity_state = InactivityState()
    # Check if you can change page using Touchscreen.
    touch_event = _on_touchscreen_event_callback(
        inactivity_state,
        websocket_mock,
        state,
        config,
    )
    await touch_event(
        mock_deck_plus,
        TouchscreenEventType.DRAG,
        {
            "x": 0,
            "y": 0,
            "x_out": 100,
            "y_out": 0,
        },
    )

    assert config.current_page() == page_1
    # Check if you can set max using touchscreen.
    dial = config.dial(0)
    assert dial is not None
    assert dial.turn is not None
    dial.turn.properties = Mock()
    dial.turn.properties.min = 0
    dial.turn.properties.max = 100
    dial.turn.properties.step = 1
    dial.turn.properties.state = 0.0
    dial.turn.properties.service_attribute = "value"

    touch_event = _on_touchscreen_event_callback(
        inactivity_state,
        websocket_mock,
        state,
        config,
    )
    await touch_event(
        mock_deck_plus,
        TouchscreenEventType.LONG,
        {
            "x": 100,
            "y": 50,
        },
    )
    attributes = {
        "min": dial.turn.properties.min,
        "max": dial.turn.properties.max,
        "state": dial.turn.properties.state,
    }
    assert attributes["state"] == attributes["max"]

    # Check if you can set min using touchscreen.
    touch_event = _on_touchscreen_event_callback(
        inactivity_state,
        websocket_mock,
        state,
        config,
    )
    await touch_event(
        mock_deck_plus,
        TouchscreenEventType.SHORT,
        {
            "x": 100,
            "y": 50,
        },
    )
    attributes = {
        "min": dial.turn.properties.min,
        "max": dial.turn.properties.max,
        "state": dial.turn.properties.state,
    }
    assert attributes["state"] == attributes["min"]

    # Check if disabling touchscreen events works
    dial = config.dial(3)
    assert dial is not None
    assert dial.turn is not None
    assert dial.allow_touchscreen_events is not True
    dial.turn.properties = Mock()
    dial.turn.properties.min = 0
    dial.turn.properties.max = 100
    dial.turn.properties.state = 50.0
    dial.turn.properties.service_attribute = "value"

    touch_event = _on_touchscreen_event_callback(
        inactivity_state,
        websocket_mock,
        state,
        config,
    )
    await touch_event(
        mock_deck_plus,
        TouchscreenEventType.SHORT,
        {
            "x": 300,
            "y": 50,
        },
    )
    attributes = {
        "min": dial.turn.properties.min,
        "max": dial.turn.properties.max,
        "state": dial.turn.properties.state,
    }
    assert attributes["state"] is not attributes["min"]


async def test_return_to_home(  # noqa: PLR0915
    mock_deck_plus: Mock,
    websocket_mock: Mock,
    state: dict[str, dict[str, Any]],
    dials: list[Dial],
) -> None:
    """Test that the return to home works."""
    return_to_home_after = 0.8
    assert return_to_home_after
    shorter_than_return_to_home_after = return_to_home_after - 0.1
    assert shorter_than_return_to_home_after < return_to_home_after
    assert shorter_than_return_to_home_after > 0.0
    longer_than_return_to_home_after = return_to_home_after + 0.1
    assert longer_than_return_to_home_after > return_to_home_after
    assert longer_than_return_to_home_after > 0.0
    longer_and_shorter_delta = longer_than_return_to_home_after - shorter_than_return_to_home_after
    home = Page(
        name="home",
        buttons=[
            Button(special_type="go-to-page", special_type_data="anon"),
            Button(special_type="go-to-page", special_type_data="second"),
            Button(special_type="go-to-page", special_type_data="stay-on"),
        ],
    )
    second = Page(
        name="second",
        buttons=[Button(special_type="empty")],
        dials=dials,
    )
    anon = Page(
        name="anon",
        buttons=[Button(text="yolo"), Button(text="foo", delay=0.1)],
    )
    stay_on = Page(
        name="stay-on",
        buttons=[Button(text="close")],
        close_on_inactivity_timer=False,
    )
    config = Config(
        pages=[home, second],
        anonymous_pages=[anon, stay_on],
        return_to_home_after_no_presses={
            "home_page": "home",
            "duration": return_to_home_after,
        },
    )
    inactivity_state = InactivityState()

    # We need to have a release otherwise it will be timing for a long press
    async def press_and_release(key: int) -> None:
        press = _on_press_callback(inactivity_state, websocket_mock, state, config)
        await press(mock_deck_plus, key, True)  # noqa: FBT003
        await press(mock_deck_plus, key, False)  # noqa: FBT003

    assert config._current_page_index == 0
    assert config._detached_page is None
    await press_and_release(0)
    assert config._detached_page is not None
    assert config.current_page() == anon
    await asyncio.sleep(
        longer_than_return_to_home_after,
    )  # longer than delay should then switch to home
    # Should now be on the home page, with the anon page closed automatically
    assert config._detached_page is None
    assert config.current_page() == home
    # Check that the logic also works on non detached pages
    await press_and_release(1)
    assert config._detached_page is None
    assert config.current_page() == second
    await asyncio.sleep(
        shorter_than_return_to_home_after,
    )  # shorter than delay should stay on page
    assert config._detached_page is None
    assert config.current_page() == second
    await asyncio.sleep(longer_and_shorter_delta)
    assert config._detached_page is None
    assert config.current_page() == home
    # Check that multiple button presses delay the return to home
    # We have to use a non-detached page for these, as these close
    # When pressed
    await press_and_release(1)
    assert config._detached_page is None
    assert config.current_page() == second
    await asyncio.sleep(
        shorter_than_return_to_home_after,
    )  # shorter than delay should stay on page
    assert config._detached_page is None
    assert config.current_page() == second
    await press_and_release(0)
    await asyncio.sleep(
        shorter_than_return_to_home_after,
    )  # shorter than delay, should still remain on page
    assert config._detached_page is None
    assert config.current_page() == second

    # Check that dial events also reset the timer
    async def dial_something() -> None:
        dial = _on_dial_event_callback(inactivity_state, websocket_mock, state, config)
        await dial(mock_deck_plus, 0, DialEventType.TURN, 1)

    await dial_something()
    await asyncio.sleep(
        shorter_than_return_to_home_after,
    )  # shorter than delay, should still remain on page
    assert config._detached_page is None
    assert config.current_page() == second

    # Check that dial events also reset the timer
    async def touch_something() -> None:
        touch = _on_touchscreen_event_callback(
            inactivity_state,
            websocket_mock,
            state,
            config,
        )
        await touch(mock_deck_plus, TouchscreenEventType.SHORT, {"x": 0, "y": 0})

    await touch_something()
    await asyncio.sleep(
        shorter_than_return_to_home_after,
    )  # shorter than delay, should still remain on page
    assert config._detached_page is None
    assert config.current_page() == second

    await asyncio.sleep(longer_than_return_to_home_after)
    assert config.current_page() == home

    # Check that the stay on page works as expected
    await press_and_release(2)
    assert config.current_page() == stay_on
    await asyncio.sleep(longer_than_return_to_home_after)
    assert config.current_page() == stay_on
    await press_and_release(0)
    assert config.current_page() == home
