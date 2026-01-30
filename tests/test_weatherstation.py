import json
import os
from unittest.mock import MagicMock, patch

import sys
# Mock dependencies before importing weatherstation
sys.modules['pirateweather'] = MagicMock()
sys.modules['waveshare_epd'] = MagicMock()
sys.modules['waveshare_epd.epd2in13bc'] = MagicMock()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from weatherstation import wrap_text, get_line_height, fit_summary_to_lines

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_icons_json_exists():
    icons_path = os.path.join(PROJECT_ROOT, "icons.json")
    assert os.path.exists(icons_path)


def test_icons_json_valid():
    icons_path = os.path.join(PROJECT_ROOT, "icons.json")
    with open(icons_path, "r") as f:
        icons = json.load(f)

    assert isinstance(icons, dict)
    assert "clear-day" in icons
    assert "rain" in icons


def test_weather_icons_font_exists():
    font_path = os.path.join(PROJECT_ROOT, "weathericons.ttf")
    assert os.path.isfile(font_path)


def test_env_example_exists():
    env_path = os.path.join(PROJECT_ROOT, ".env.example")
    assert os.path.exists(env_path)


def test_wrap_text_single_line():
    """Test that short text stays on one line."""
    mock_font = MagicMock()
    mock_font.getlength.return_value = 50  # Text fits

    result = wrap_text("Short text", mock_font, max_width=100, max_lines=2)

    assert result == ["Short text"]


def test_wrap_text_wraps_long_text():
    """Test that long text wraps to multiple lines."""
    mock_font = MagicMock()
    # Simulate: each word is ~30px, max_width is 70px (fits ~2 words per line)
    def mock_getlength(text):
        return len(text.split()) * 30
    mock_font.getlength.side_effect = mock_getlength

    result = wrap_text("One two three four", mock_font, max_width=70, max_lines=3)

    assert len(result) == 2
    assert result[0] == "One two"
    assert result[1] == "three four"


def test_wrap_text_respects_max_lines():
    """Test that wrap_text respects max_lines limit."""
    mock_font = MagicMock()
    # Each word is 40px, max_width is 50px (one word per line)
    mock_font.getlength.side_effect = lambda text: len(text.split()) * 40

    result = wrap_text("One two three four five", mock_font, max_width=50, max_lines=2)

    assert len(result) == 2
    assert result[0] == "One"
    assert result[1] == "two"


def test_wrap_text_empty_string():
    """Test wrap_text with empty string."""
    mock_font = MagicMock()
    mock_font.getlength.return_value = 0

    result = wrap_text("", mock_font, max_width=100, max_lines=2)

    assert result == []


def test_get_line_height():
    """Test get_line_height calculates correct height."""
    mock_font = MagicMock()
    mock_font.getmetrics.return_value = (14, 4)  # ascent=14, descent=4

    result = get_line_height(mock_font)

    assert result == 20  # 14 + 4 + 2 (spacing)


@patch('weatherstation.ImageFont.truetype')
def test_fit_summary_short_text_uses_max_size(mock_truetype):
    """Test that short text uses the maximum font size."""
    mock_font = MagicMock()
    mock_font.getlength.return_value = 50  # Text fits easily
    mock_truetype.return_value = mock_font

    font, lines = fit_summary_to_lines("Short", "/fake/path.ttf", max_width=200, max_lines=2, max_size=18, min_size=12)

    # Should use max size (18) on first try
    mock_truetype.assert_called_with("/fake/path.ttf", 18)
    assert lines == ["Short"]


@patch('weatherstation.ImageFont.truetype')
def test_fit_summary_long_text_reduces_font_size(mock_truetype):
    """Test that long text triggers font size reduction."""
    call_count = [0]

    def mock_font_factory(path, size):
        call_count[0] += 1
        mock_font = MagicMock()
        # At size 18 and 17: text doesn't fit (each word ~60px, 3 words = 180px > 150px width)
        # At size 16: text fits on 2 lines
        if size >= 17:
            mock_font.getlength.side_effect = lambda text: len(text.split()) * 60
        else:
            mock_font.getlength.side_effect = lambda text: len(text.split()) * 40
        return mock_font

    mock_truetype.side_effect = mock_font_factory

    font, lines = fit_summary_to_lines("One two three", "/fake/path.ttf", max_width=100, max_lines=2, max_size=18, min_size=12)

    # Should have tried sizes 18, 17, then succeeded at 16
    assert call_count[0] == 3
    assert mock_truetype.call_args_list[-1][0] == ("/fake/path.ttf", 16)


@patch('weatherstation.log_message')
@patch('weatherstation.ImageFont.truetype')
def test_fit_summary_respects_minimum_size(mock_truetype, mock_log):
    """Test that minimum size is respected even if text doesn't fit."""
    mock_font = MagicMock()
    # Text never fits - each word is 200px, way over max_width
    mock_font.getlength.side_effect = lambda text: len(text.split()) * 200
    mock_truetype.return_value = mock_font

    font, lines = fit_summary_to_lines("Very long text here", "/fake/path.ttf", max_width=100, max_lines=2, max_size=18, min_size=12)

    # Should end at minimum size (12)
    # Called for sizes 18, 17, 16, 15, 14, 13, 12, then final call at 12
    final_call = mock_truetype.call_args_list[-1]
    assert final_call[0] == ("/fake/path.ttf", 12)

    # Should log error about truncation
    assert mock_log.called
