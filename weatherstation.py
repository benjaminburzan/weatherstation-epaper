# HOW TO
# sudo raspi-config # Gehe zu “Interfacing Options” → “SPI” und aktiviere es.
# sudo apt install python3-rpi.gpio python3-spidev python3-pip python3-pil python3-numpy git vim python3-rpi-lgpio python3-lgpio python3-aiohttp liblgpio-dev fonts-dejavu python3.11-venv swig build-essential python3-dev python3-cairosvg
# git clone https://github.com/waveshareteam/e-Paper.git
# cd e-Paper/RaspberryPi_JetsonNano/python/
# pip3 install . --break-system-packages
# pip3 install --break-system-packages -r requirements.txt
# Credits Icons: https://github.com/erikflowers/weather-icons

import time
from datetime import datetime
import pirateweather
from waveshare_epd import epd2in13bc
from PIL import Image, ImageDraw, ImageFont
import json

# JSON mit den Übersetzungen laden
with open('translation.json', 'r') as file:
    translations = json.load(file)

# Icons aus Datei laden
with open("icons.json", "r") as file:
    icon_mapping = json.load(file)

# Pirate Weather API-Konfiguration
API_KEY = "moqBQ2WXFEE92AE3gbieHeBjO3wRFqVc"
LATITUDE = 52.5200  # Berlin
LONGITUDE = 13.4050

# Log-Dateipfad
LOG_FILE = "/var/log/weatherstation.log"

# Globale Variablen, um die letzten Temperaturdaten zu speichern
last_temperature = None
last_temperature_max = None
last_summary = None

# Funktion zum Logging mit Timestamp
def log_message(message):
    """Schreibt eine Nachricht mit Timestamp in die Log-Datei."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    with open(LOG_FILE, "a") as log_file:
        log_file.write(log_entry)

    print(f"[{timestamp}] {message}")  # Optional: Konsolenausgabe

def get_weather_icon(weather_icon):
    """Gibt den passenden PNG-Dateinamen zurück oder ein Standard-Icon."""
    #return icon_mapping.get(weather_icon, "wi-day-sunny.png")  # Standard-Icon als Fallback
    icon_filename = icon_mapping.get(weather_icon, "wi-day-sunny.png")  # Fallback-Icon
    return f"weather-icons/{icon_filename}"

# Funktion zum Übersetzen des Wettersummaries
def translate_summary(english_summary):
    """Übersetzt die Wetterzusammenfassung von Englisch nach Deutsch."""
    return translations.get(english_summary, english_summary)  # Rückfall auf den englischen Text, wenn keine Übersetzung vorhanden ist.

# Funktion zum Überprüfen, ob sich die Wetterdaten geändert haben
def should_update_display(temperature, temperature_max, summary):
    """Überprüft, ob sich die Wetterdaten geändert haben."""
    global last_temperature, last_temperature_max, last_summary

    if (temperature != last_temperature or
        temperature_max != last_temperature_max or
        summary != last_summary):
        # Daten haben sich geändert
        last_temperature = temperature
        last_temperature_max = temperature_max
        last_summary = summary
        return True
    return False

# Funktion zum Löschen des Displays und Versetzen in den Ruhezustand
def clear_display_and_sleep(epd):
    """Löscht das Display und versetzt es in den Ruhezustand."""
    epd.Clear()
    epd.sleep()

# Wetterdaten abrufen
def get_weather():
    """Holt Wetterdaten von Pirate Weather und gibt sie formatiert zurück."""
    log_message("Wetterdaten abrufen...")

    try:
        forecast = pirateweather.load_forecast(API_KEY, LATITUDE, LONGITUDE, lang="de", units="si")
        temperature = round(forecast.currently().temperature) if forecast.currently().temperature is not None else 0 # Temperatur runden

        temperature_max = round(forecast.daily().data[0].temperatureMax) if forecast.daily().data[0].temperatureMax is not None else 0  # Max Temperatur runden
        summary = forecast.daily().data[0].summary
        icon = forecast.daily().data[0].icon

        # Rückgabe der Temperaturen und Zusammenfassung
        return temperature, temperature_max, summary, icon
    except Exception as e:
        log_message(f"Fehler beim Abrufen der Wetterdaten: {e}")
        return None, None, "Fehler: Keine Daten"

# Wetter auf dem e-Paper Display anzeigen
def display_weather(epd, temperature, temperature_max, summary, png_icon_path):
    """Zeigt das Wetter auf dem e-Paper Display an."""
    log_message("Zeige Wetter auf e-Paper Display...")

    try:
        epd.init()
        epd.Clear()

        # Erstellt ein leeres Bild (schwarz-weiß)
        image_black = Image.new("1", (epd.height, epd.width), 255)  # Weiß (Querformat)
        draw_black = ImageDraw.Draw(image_black)

        # Erstellt ein leeres Bild für rote Elemente (bei diesem Design genutzt)
        image_red = Image.new("1", (epd.height, epd.width), 255)  # Weiß
        draw_red = ImageDraw.Draw(image_red)

        # Schriftart laden
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
        font = ImageFont.truetype(font_path, 32)  # Größere Schrift für Temperatur
        font_summary = ImageFont.truetype(font_path, 18)  # Kleinere Schrift für die Zusammenfassung

        # Berechne die Höhe und Position des Textes
        temp_height = int(epd.height * 0.4)  # 40% der Höhe für Temperaturdaten
        #summary_height = epd.height - temp_height  # Restliche 60% der Höhe für die Zusammenfassung

        PADDING = 10  # Abstand zu den Rändern

        # Falls Temperatur >= Temperatur-Maximum → Temperatur in ROT anzeigen
        if temperature >= temperature_max:
            draw_red.text((PADDING, PADDING), f"{temperature}°C", font=font, fill=0)  # ROT
        else:
            # Prüfe, ob eine der Zahlen zweistellig ist
            if temperature >= 10 or temperature_max >= 10:
                draw_black.text((PADDING, PADDING), f"{temperature}°/{temperature_max}°", font=font, fill=0)  # Schwarz mit "/" ohne Leerzeichen
            else:
                draw_black.text((PADDING, PADDING), f"{temperature}° / {temperature_max}°", font=font, fill=0)  # Schwarz mit " / " mit Leerzeichen

        # Wetterzusammenfassung im unteren Bereich (60%)
        draw_black.text((PADDING, temp_height - PADDING), summary, font=font_summary, fill=0)  # Schwarz

        # Wetter-Icon anzeigen
        try:
            ICON_SIZE = 40
            weather_icon_img = Image.open(png_icon_path).convert("1")  # In Schwarz-Weiß umwandeln
            weather_icon_img = weather_icon_img.resize((ICON_SIZE, ICON_SIZE))  # Skalieren
            image_black.paste(weather_icon_img, (epd.height - PADDING - weather_icon_img.width, PADDING))  # Positionieren // height because screen gehts rotated by 90 degress
        except Exception as e:
            log_message(f"Fehler beim Laden des Icons: {e}")

        # Drehe das Bild um 90° im Uhrzeigersinn
        image_black = image_black.rotate(180, expand=True)
        image_red = image_red.rotate(180, expand=True)

        # Bilder an das Display senden
        epd.display(epd.getbuffer(image_black), epd.getbuffer(image_red))

        log_message("Anzeige erfolgreich aktualisiert.")
        epd.sleep()
    except Exception as e:
        log_message(f"Fehler bei der Display-Anzeige: {e}")
        epd.sleep()

# Hauptfunktion
def main():
    log_message("Weather Station gestartet.")
    epd = epd2in13bc.EPD()

    while True:
        # Holen der Wetterdaten und zurückgeben der Variablen
        temperature, temperature_max, summary, weather_icon = get_weather()
        png_icon_path = get_weather_icon(weather_icon)

        # Translate daily weather summary into German
        translated_summary = translate_summary(summary)

        log_message(f"Wetterdaten: {temperature}° / {temperature_max}°, {translated_summary} Wetter-Icon: {png_icon_path}")

        if temperature is not None and temperature_max is not None:
            # Anzeige nur aktualisieren, wenn die Daten sich geändert haben
            if should_update_display(temperature, temperature_max, translated_summary):
                display_weather(epd, temperature, temperature_max, translated_summary, png_icon_path)
            else:
                log_message("Keine Änderung der Wetterdaten, Anzeige nicht aktualisiert.")
        else:
            log_message("Fehler bei der Wetterdatenanzeige.")

        log_message("Warte 30 Minuten bis zur nächsten Aktualisierung...")
        time.sleep(1800)  # 30 Minuten warten
        clear_display_and_sleep(epd)  # Versetze das Display in den Ruhezustand

if __name__ == "__main__":
    main()
