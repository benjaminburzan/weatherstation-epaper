import os
import sys
import time
from datetime import datetime
import json

import pirateweather
from waveshare_epd import epd2in13bc
from PIL import Image, ImageDraw, ImageFont

# Configuration (from environment variables)
# API
API_KEY = os.environ.get("PIRATE_WEATHER_API_KEY")
LATITUDE = float(os.environ.get("LATITUDE", "52.5200"))
LONGITUDE = float(os.environ.get("LONGITUDE", "13.4050"))
LANGUAGE = os.environ.get("LANGUAGE", "de")
UNITS = os.environ.get("UNITS", "si")
TEMP_SYMBOL = "°F" if UNITS == "us" else "°C"

# Display
FONT_SIZE_TEMPERATURE = int(os.environ.get("FONT_SIZE_TEMPERATURE", "32"))
FONT_SIZE_SUMMARY = int(os.environ.get("FONT_SIZE_SUMMARY", "18"))
MIN_FONT_SIZE_SUMMARY = int(os.environ.get("MIN_FONT_SIZE_SUMMARY", "10"))
ICON_SIZE = int(os.environ.get("ICON_SIZE", "40"))
PADDING = int(os.environ.get("PADDING", "10"))
FLIP_DISPLAY = os.environ.get("FLIP_DISPLAY", "false").lower() == "true"

# Timing
UPDATE_INTERVAL_SECONDS = int(os.environ.get("UPDATE_INTERVAL_SECONDS", "1800"))

# Paths
FONT_PATH = os.environ.get("FONT_PATH", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
LOG_FILE = os.environ.get("LOG_FILE", "/var/log/weatherstation.log")

# Load icon mapping from file
with open("icons.json", "r") as file:
    icon_mapping = json.load(file)


def log_message(message):
    """Writes a message with timestamp to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry)

    print(f"[{timestamp}] {message}")


def get_weather_icon(weather_icon):
    """Returns the matching PNG filename or a default icon."""
    icon_filename = icon_mapping.get(weather_icon, "wi-day-sunny.png")  # Fallback icon
    return f"weather-icons/{icon_filename}"


class WeatherStation:
    """Encapsulates weather station state and operations."""

    def __init__(self):
        self.last_temperature = None
        self.last_temperature_max = None
        self.last_summary = None
        self.epd = epd2in13bc.EPD()

    def should_update_display(self, temperature, temperature_max, summary):
        """Check if weather data has changed."""
        if (temperature != self.last_temperature or
            temperature_max != self.last_temperature_max or
            summary != self.last_summary):
            self.last_temperature = temperature
            self.last_temperature_max = temperature_max
            self.last_summary = summary
            return True
        return False

    def run(self):
        """Main loop."""
        log_message("Weather Station started.")

        while True:
            # Fetch weather data
            temperature, temperature_max, summary, weather_icon = get_weather()
            png_icon_path = get_weather_icon(weather_icon)

            # Summary is already translated by the API via lang parameter
            log_message(f"Weather data: {temperature}° / {temperature_max}°, {summary} Icon: {png_icon_path}")

            if temperature is not None and temperature_max is not None:
                # Only update display if data has changed
                if self.should_update_display(temperature, temperature_max, summary):
                    display_weather(self.epd, temperature, temperature_max, summary, png_icon_path)
                else:
                    log_message("No change in weather data, display not updated.")
            else:
                log_message("Error displaying weather data.")

            log_message(f"Waiting {UPDATE_INTERVAL_SECONDS // 60} minutes until next update...")
            time.sleep(UPDATE_INTERVAL_SECONDS)
            clear_display_and_sleep(self.epd)


def clear_display_and_sleep(epd):
    """Clears the display and puts it into sleep mode."""
    epd.Clear()
    epd.sleep()


def get_weather():
    """Fetches weather data from Pirate Weather and returns it formatted."""
    log_message("Fetching weather data...")

    try:
        forecast = pirateweather.load_forecast(API_KEY, LATITUDE, LONGITUDE, lang=LANGUAGE, units=UNITS)
        temperature = round(forecast.currently().temperature) if forecast.currently().temperature is not None else 0  # Round temperature

        temperature_max = round(forecast.daily().data[0].temperatureMax) if forecast.daily().data[0].temperatureMax is not None else 0  # Round max temperature
        summary = forecast.daily().data[0].summary
        icon = forecast.daily().data[0].icon

        return temperature, temperature_max, summary, icon
    except (pirateweather.PirateWeatherError, ConnectionError, TimeoutError) as e:
        log_message(f"Error fetching weather data: {e}")
        return None, None, "Error: No data", None


def get_fitting_font_size(text, max_width, font_path, max_size, min_size=MIN_FONT_SIZE_SUMMARY):
    """Returns a font size that fits the text within max_width."""
    for size in range(max_size, min_size - 1, -1):
        font = ImageFont.truetype(font_path, size)
        text_width = font.getlength(text)
        if text_width <= max_width:
            return size
    return min_size


def display_weather(epd, temperature, temperature_max, summary, png_icon_path):
    """Displays the weather on the e-Paper display."""
    log_message("Displaying weather on e-Paper display...")

    try:
        epd.init()
        epd.Clear()

        # Create empty black/white image (landscape orientation)
        image_black = Image.new("1", (epd.height, epd.width), 255)  # White
        draw_black = ImageDraw.Draw(image_black)

        # Create empty image for red elements
        image_red = Image.new("1", (epd.height, epd.width), 255)  # White
        draw_red = ImageDraw.Draw(image_red)

        # Load fonts
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE_TEMPERATURE)
        available_width = epd.height - (2 * PADDING)  # epd.height is width in landscape
        summary_font_size = get_fitting_font_size(summary, available_width, FONT_PATH, FONT_SIZE_SUMMARY)
        font_summary = ImageFont.truetype(FONT_PATH, summary_font_size)

        # Calculate text height and position (40% for temperature data)
        temp_height = int(epd.height * 0.4)

        # If temperature >= max temperature, display in RED
        if temperature >= temperature_max:
            draw_red.text((PADDING, PADDING), f"{temperature}{TEMP_SYMBOL}", font=font, fill=0)  # Red
        else:
            # Check if either number is double-digit
            if temperature >= 10 or temperature_max >= 10:
                draw_black.text((PADDING, PADDING), f"{temperature}°/{temperature_max}{TEMP_SYMBOL}", font=font, fill=0)  # Black with "/" no spaces
            else:
                draw_black.text((PADDING, PADDING), f"{temperature}° / {temperature_max}{TEMP_SYMBOL}", font=font, fill=0)  # Black with " / " with spaces

        # Weather summary in lower area
        draw_black.text((PADDING, temp_height - PADDING), summary, font=font_summary, fill=0)  # Black

        # Display weather icon
        try:
            weather_icon_img = Image.open(png_icon_path).convert("1")  # Convert to black/white
            weather_icon_img = weather_icon_img.resize((ICON_SIZE, ICON_SIZE))  # Scale
            image_black.paste(weather_icon_img, (epd.height - PADDING - weather_icon_img.width, PADDING))  # Position (height because screen is rotated 90 degrees)
        except (FileNotFoundError, IOError, OSError) as e:
            log_message(f"Error loading icon: {e}")

        # Rotate image for display orientation
        rotation = 270 if FLIP_DISPLAY else 90
        image_black = image_black.rotate(rotation, expand=True)
        image_red = image_red.rotate(rotation, expand=True)

        # Send images to display
        epd.display(epd.getbuffer(image_black), epd.getbuffer(image_red))

        log_message("Display updated successfully.")
        epd.sleep()
    except Exception as e:
        log_message(f"Error in display: {type(e).__name__}: {e}")
        epd.sleep()

def main():
    if not API_KEY:
        log_message("ERROR: PIRATE_WEATHER_API_KEY environment variable not set")
        sys.exit(1)

    station = WeatherStation()
    station.run()


if __name__ == "__main__":
    main()
