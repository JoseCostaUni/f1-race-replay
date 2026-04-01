"""Centralized theme and color palette for F1 Race Replay UI.

This module provides a single source of truth for all colors, spacing, and typography
used throughout the application. Enables consistent styling and future theme switching
(light/dark modes).
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ColorPalette:
    """Color palette for the F1 Race Replay UI."""

    # Primary Colors
    primary: str = "#E8002D"  # F1 Red
    primary_dark: str = "#B80024"
    primary_light: str = "#FF4444"

    # Neutral/Background Colors
    bg_dark: str = "#282828"  # Main background
    bg_medium: str = "#303030"
    bg_light: str = "#3A3A3A"
    bg_lighter: str = "#4A4A4A"

    # Text Colors
    text_primary: str = "#F0F0F0"  # Primary text (light gray)
    text_secondary: str = "#CCCCCC"  # Secondary text
    text_muted: str = "#808080"  # Muted text
    text_disabled: str = "#555555"

    # Status Colors
    success: str = "#00AA00"  # Green
    warning: str = "#FFAA00"  # Orange
    error: str = "#FF4444"  # Red
    info: str = "#00CCFF"  # Cyan

    # Driver/Team Colors (F1 2024 season)
    driver_1: str = "#FF8700"  # McLaren Orange
    driver_2: str = "#DC0000"  # Ferrari Red
    driver_3: str = "#0082FA"  # Mercedes Blue
    driver_4: str = "#1E3050"  # Red Bull Navy
    driver_5: str = "#2D826D"  # Aston Martin Green
    driver_6: str = "#FFF500"  # Alfa Romeo Yellow
    driver_7: str = "#0A0E27"  # Alpine Dark Blue
    driver_8: str = "#46B8F1"  # Williams Light Blue
    driver_9: str = "#B6BABD"  # Haas Silver
    driver_10: str = "#FF69B4"  # Kick Sauber Pink

    # Special Status Colors
    dnf: str = "#FF4444"  # Did Not Finish
    safety_car: str = "#FFFF00"  # Safety Car
    virtual_safety_car: str = "#FFAA00"  # Virtual Safety Car
    red_flag: str = "#CC0000"  # Red Flag

    # UI Element Colors
    border: str = "#444444"
    border_hover: str = "#666666"
    button_bg: str = "#404040"
    button_hover: str = "#505050"
    button_active: str = "#E8002D"
    overlay_bg: str = "rgba(40, 40, 40, 0.9)"  # Semi-transparent dark

    # Tyre Component Colors
    tyre_soft: str = "#FF0000"  # Red
    tyre_medium: str = "#FFFF00"  # Yellow
    tyre_hard: str = "#FFFFFF"  # White
    tyre_intermediate: str = "#00FF00"  # Green
    tyre_wet: str = "#0099FF"  # Blue


@dataclass
class Spacing:
    """Standard spacing values (in pixels)."""

    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 24
    xxl: int = 32


@dataclass
class Typography:
    """Font sizes and styles (in pixels)."""

    # Font sizes
    size_xs: int = 10
    size_sm: int = 12
    size_base: int = 14
    size_lg: int = 16
    size_xl: int = 18
    size_2xl: int = 24
    size_3xl: int = 32

    # Font names (will need to match what arcade provides)
    font_default: str = "arial"
    font_monospace: str = "courier"


@dataclass
class Theme:
    """Complete theme configuration."""

    colors: ColorPalette = None
    spacing: Spacing = None
    typography: Typography = None

    def __post_init__(self):
        """Initialize theme components."""
        if self.colors is None:
            self.colors = ColorPalette()
        if self.spacing is None:
            self.spacing = Spacing()
        if self.typography is None:
            self.typography = Typography()


# Default theme instance
DEFAULT_THEME = Theme()


def get_driver_color(driver_index: int) -> str:
    """Get color for a specific driver by index.

    Args:
        driver_index: Driver index (0-based). Wraps around if > 9.

    Returns:
        Hex color string for the driver.
    """
    colors = [
        DEFAULT_THEME.colors.driver_1,
        DEFAULT_THEME.colors.driver_2,
        DEFAULT_THEME.colors.driver_3,
        DEFAULT_THEME.colors.driver_4,
        DEFAULT_THEME.colors.driver_5,
        DEFAULT_THEME.colors.driver_6,
        DEFAULT_THEME.colors.driver_7,
        DEFAULT_THEME.colors.driver_8,
        DEFAULT_THEME.colors.driver_9,
        DEFAULT_THEME.colors.driver_10,
    ]
    return colors[driver_index % len(colors)]


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#FF0000").

    Returns:
        Tuple of (R, G, B) values (0-255).
    """
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color string.

    Args:
        r, g, b: RGB values (0-255).

    Returns:
        Hex color string (e.g., "#FF0000").
    """
    return f"#{r:02X}{g:02X}{b:02X}"
