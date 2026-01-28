#!/usr/bin/env python3
"""Generate simplified weather icons optimized for e-paper displays."""

import math
from PIL import Image, ImageDraw

SIZE = 48
LINE_WIDTH = 3
BLACK = (0, 0, 0, 255)
TRANSPARENT = (0, 0, 0, 0)


def create_canvas():
    """Create a transparent 48x48 canvas."""
    return Image.new("RGBA", (SIZE, SIZE), TRANSPARENT)


def draw_sun(draw, cx, cy, outer_r, inner_r, num_rays=8):
    """Draw a sun with rays at given center position."""
    # Draw center circle
    draw.ellipse(
        [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
        fill=BLACK
    )
    # Draw rays as triangles
    for i in range(num_rays):
        angle = (2 * math.pi * i) / num_rays - math.pi / 2
        # Ray tip
        tip_x = cx + outer_r * math.cos(angle)
        tip_y = cy + outer_r * math.sin(angle)
        # Ray base (two points on circle)
        base_angle = math.pi / (num_rays * 1.5)
        base1_x = cx + inner_r * math.cos(angle - base_angle)
        base1_y = cy + inner_r * math.sin(angle - base_angle)
        base2_x = cx + inner_r * math.cos(angle + base_angle)
        base2_y = cy + inner_r * math.sin(angle + base_angle)
        draw.polygon([(tip_x, tip_y), (base1_x, base1_y), (base2_x, base2_y)], fill=BLACK)


def draw_cloud(draw, x_offset=0, y_offset=0, scale=1.0):
    """Draw a simple cloud shape."""
    # Cloud is made of overlapping circles
    def sc(v):
        return int(v * scale)

    cx, cy = 24 + x_offset, 28 + y_offset
    # Main body (large ellipse)
    draw.ellipse([cx - sc(14), cy - sc(8), cx + sc(14), cy + sc(8)], fill=BLACK)
    # Left bump
    draw.ellipse([cx - sc(16), cy - sc(12), cx - sc(4), cy], fill=BLACK)
    # Right bump
    draw.ellipse([cx, cy - sc(14), cx + sc(12), cy - sc(2)], fill=BLACK)
    # Top bump
    draw.ellipse([cx - sc(8), cy - sc(16), cx + sc(4), cy - sc(4)], fill=BLACK)


def generate_sunny():
    """Sun icon - solid circle with rays."""
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    draw_sun(draw, 24, 24, 22, 10, num_rays=8)
    return img


def generate_cloudy():
    """Cloud icon - single bold cloud."""
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    draw_cloud(draw, y_offset=-4)
    return img


def generate_partly_cloudy():
    """Sun with cloud - small sun top-left, cloud overlay."""
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    # Small sun in top-left
    draw_sun(draw, 14, 14, 14, 6, num_rays=8)
    # Cloud overlapping bottom-right
    draw_cloud(draw, x_offset=4, y_offset=2, scale=0.9)
    return img


def generate_rain():
    """Cloud with rain drops."""
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    # Cloud at top
    draw_cloud(draw, y_offset=-10, scale=0.85)
    # Rain lines (diagonal)
    for i, x in enumerate([14, 24, 34]):
        y_start = 30 + (i % 2) * 3
        draw.line([(x, y_start), (x - 4, y_start + 12)], fill=BLACK, width=LINE_WIDTH)
    return img


def generate_snow():
    """Cloud with snowflakes."""
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    # Cloud at top
    draw_cloud(draw, y_offset=-10, scale=0.85)
    # Snowflakes as asterisks
    for cx, cy in [(14, 36), (24, 40), (34, 34)]:
        r = 4
        # Draw 3-line asterisk
        for angle in [0, 60, 120]:
            rad = math.radians(angle)
            x1 = cx + r * math.cos(rad)
            y1 = cy + r * math.sin(rad)
            x2 = cx - r * math.cos(rad)
            y2 = cy - r * math.sin(rad)
            draw.line([(x1, y1), (x2, y2)], fill=BLACK, width=2)
    return img


def generate_sleet():
    """Cloud with mix of rain and snow."""
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    # Cloud at top
    draw_cloud(draw, y_offset=-10, scale=0.85)
    # Rain line
    draw.line([(16, 32), (12, 44)], fill=BLACK, width=LINE_WIDTH)
    # Snow dot
    draw.ellipse([21, 36, 27, 42], fill=BLACK)
    # Rain line
    draw.line([(34, 30), (30, 42)], fill=BLACK, width=LINE_WIDTH)
    return img


def generate_fog():
    """Horizontal parallel lines."""
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    # Draw 4 horizontal lines of varying lengths
    lines = [
        (8, 12, 40),   # y, x_start, x_end
        (6, 20, 42),
        (10, 28, 38),
        (8, 36, 40),
    ]
    y_positions = [10, 20, 30, 40]
    for i, y in enumerate(y_positions):
        x_start, x_end = lines[i][0], lines[i][2]
        draw.line([(x_start, y), (x_end, y)], fill=BLACK, width=LINE_WIDTH)
    return img


def generate_thunderstorm():
    """Cloud with lightning bolt."""
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    # Cloud at top
    draw_cloud(draw, y_offset=-12, scale=0.8)
    # Lightning bolt
    bolt = [
        (28, 24),
        (22, 34),
        (26, 34),
        (20, 46),
        (30, 32),
        (26, 32),
        (32, 24),
    ]
    draw.polygon(bolt, fill=BLACK)
    return img


def generate_hail():
    """Cloud with hailstones."""
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    # Cloud at top
    draw_cloud(draw, y_offset=-10, scale=0.85)
    # Hailstones as circles
    for cx, cy in [(12, 36), (24, 34), (36, 38), (18, 44), (30, 42)]:
        r = 3
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BLACK)
    return img


def generate_wind():
    """Curved horizontal wind lines."""
    img = create_canvas()
    draw = ImageDraw.Draw(img)
    # Three curved wind lines
    # Top line
    draw.arc([4, 6, 40, 22], start=180, end=0, fill=BLACK, width=LINE_WIDTH)
    # Middle line (longer)
    draw.arc([8, 18, 44, 34], start=180, end=0, fill=BLACK, width=LINE_WIDTH)
    # Bottom line
    draw.arc([4, 30, 36, 46], start=180, end=0, fill=BLACK, width=LINE_WIDTH)
    return img


def main():
    """Generate all icons and save to weather-icons/."""
    icons = {
        "wi-day-sunny.png": generate_sunny,
        "wi-day-cloudy.png": generate_partly_cloudy,
        "wi-cloudy.png": generate_cloudy,
        "wi-rain.png": generate_rain,
        "wi-snow-wind.png": generate_snow,
        "wi-sleet.png": generate_sleet,
        "wi-fog.png": generate_fog,
        "wi-thunderstorm.png": generate_thunderstorm,
        "wi-hail.png": generate_hail,
        "wi-strong-wind.png": generate_wind,
    }

    for filename, generator in icons.items():
        img = generator()
        path = f"weather-icons/{filename}"
        img.save(path, "PNG")
        print(f"Generated: {path}")

    print(f"\nGenerated {len(icons)} icons in weather-icons/")


if __name__ == "__main__":
    main()
