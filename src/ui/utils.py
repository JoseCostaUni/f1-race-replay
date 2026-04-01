"""UI utility functions for Arcade-based rendering.

Provides common drawing helpers, text rendering, color manipulation, and
other utilities used across components.
"""

import arcade
from typing import Tuple


# Type aliases
Color = Tuple[int, int, int] | Tuple[int, int, int, int]  # RGB or RGBA
HexColor = str  # "RRGGBB" or "#RRGGBB"


def draw_text(
    text: str,
    x: float,
    y: float,
    color: Color | HexColor = (255, 255, 255),
    font_size: int = 14,
    anchor_x: str = "left",
    anchor_y: str = "bottom",
    bold: bool = False,
    italic: bool = False,
    font_name: str = "Arial",
) -> None:
    """Draw text at screen position.

    Args:
        text: Text to draw.
        x, y: Position in pixels.
        color: RGB/RGBA tuple or hex string.
        font_size: Font size in pixels.
        anchor_x: Horizontal anchor ("left", "center", "right").
        anchor_y: Vertical anchor ("bottom", "center", "top").
        bold: Use bold font.
        italic: Use italic font.
        font_name: Font name.
    """
    if isinstance(color, str):
        color = hex_to_rgb(color)

    arcade.draw_text(
        text,
        x,
        y,
        color=color,
        font_size=font_size,
        anchor_x=anchor_x,
        anchor_y=anchor_y,
        bold=bold,
        italic=italic,
        font_name=font_name,
    )


def draw_rectangle_outline(
    x: float,
    y: float,
    width: float,
    height: float,
    color: Color | HexColor = (255, 255, 255),
    border_width: int = 2,
) -> None:
    """Draw rectangle outline.

    Args:
        x, y: Top-left position.
        width, height: Dimensions.
        color: RGB/RGBA tuple or hex string.
        border_width: Border thickness in pixels.
    """
    if isinstance(color, str):
        color = hex_to_rgb(color)

    arcade.draw_rectangle_outline(
        x + width / 2,
        y + height / 2,
        width,
        height,
        color=color,
        border_width=border_width,
    )


def draw_rectangle_filled(
    x: float,
    y: float,
    width: float,
    height: float,
    color: Color | HexColor = (255, 255, 255),
) -> None:
    """Draw filled rectangle.

    Args:
        x, y: Top-left position.
        width, height: Dimensions.
        color: RGB/RGBA tuple or hex string.
    """
    if isinstance(color, str):
        color = hex_to_rgb(color)

    arcade.draw_rectangle_filled(
        x + width / 2,
        y + height / 2,
        width,
        height,
        color=color,
    )


def draw_rectangle_with_text(
    x: float,
    y: float,
    width: float,
    height: float,
    text: str,
    bg_color: Color | HexColor = (64, 64, 64),
    text_color: Color | HexColor = (255, 255, 255),
    font_size: int = 14,
    padding: float = 8,
) -> None:
    """Draw a rectangle with centered text inside.

    Args:
        x, y: Top-left position.
        width, height: Dimensions.
        text: Text to display.
        bg_color: Background color.
        text_color: Text color.
        font_size: Font size.
        padding: Padding around text.
    """
    draw_rectangle_filled(x, y, width, height, bg_color)

    text_x = x + width / 2
    text_y = y + height / 2

    draw_text(
        text,
        text_x,
        text_y,
        color=text_color,
        font_size=font_size,
        anchor_x="center",
        anchor_y="center",
    )


def draw_circle(
    x: float,
    y: float,
    radius: float,
    color: Color | HexColor = (255, 255, 255),
) -> None:
    """Draw filled circle.

    Args:
        x, y: Center position.
        radius: Circle radius.
        color: RGB/RGBA tuple or hex string.
    """
    if isinstance(color, str):
        color = hex_to_rgb(color)

    arcade.draw_circle_filled(x, y, radius, color)


def draw_circle_outline(
    x: float,
    y: float,
    radius: float,
    color: Color | HexColor = (255, 255, 255),
    border_width: int = 2,
) -> None:
    """Draw circle outline.

    Args:
        x, y: Center position.
        radius: Circle radius.
        color: RGB/RGBA tuple or hex string.
        border_width: Border thickness.
    """
    if isinstance(color, str):
        color = hex_to_rgb(color)

    arcade.draw_circle_outline(x, y, radius, color, border_width)


def draw_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: Color | HexColor = (255, 255, 255),
    width: int = 1,
) -> None:
    """Draw a line.

    Args:
        x1, y1: Start point.
        x2, y2: End point.
        color: RGB/RGBA tuple or hex string.
        width: Line width.
    """
    if isinstance(color, str):
        color = hex_to_rgb(color)

    arcade.draw_line(x1, y1, x2, y2, color, width)


def draw_triangle(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    x3: float,
    y3: float,
    color: Color | HexColor = (255, 255, 255),
) -> None:
    """Draw filled triangle.

    Args:
        x1, y1, x2, y2, x3, y3: Triangle vertices.
        color: RGB/RGBA tuple or hex string.
    """
    if isinstance(color, str):
        color = hex_to_rgb(color)

    arcade.draw_triangle_filled(x1, y1, x2, y2, x3, y3, color)


def hex_to_rgb(hex_color: str) -> Color:
    """Convert hex color to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#FF0000" or "FF0000").

    Returns:
        RGB tuple (R, G, B).
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 6:
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    elif len(hex_color) == 8:
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4, 6))
    else:
        raise ValueError(f"Invalid hex color: {hex_color}")


# ========================
# Track & Race Utilities
# ========================

import numpy as np
from typing import List, Dict, Any


def build_track_from_example_lap(example_lap, track_width=200):
    """Build track geometry from example lap telemetry.
    
    Args:
        example_lap: DataFrame or dict with X, Y, DRS columns
        track_width: Width of the track in pixels
        
    Returns:
        Tuple of (plot_x_ref, plot_y_ref, x_inner, y_inner, x_outer, y_outer,
                  x_min, x_max, y_min, y_max, drs_zones)
    """
    drs_zones = _plot_drs_zones(example_lap)
    plot_x_ref = example_lap["X"]
    plot_y_ref = example_lap["Y"]

    # compute tangents
    dx = np.gradient(plot_x_ref)
    dy = np.gradient(plot_y_ref)

    norm = np.sqrt(dx**2 + dy**2)
    norm[norm == 0] = 1.0
    dx /= norm
    dy /= norm

    nx = -dy
    ny = dx

    x_outer = plot_x_ref + nx * (track_width / 2)
    y_outer = plot_y_ref + ny * (track_width / 2)
    x_inner = plot_x_ref - nx * (track_width / 2)
    y_inner = plot_y_ref - ny * (track_width / 2)

    # world bounds
    x_min = min(plot_x_ref.min(), x_inner.min(), x_outer.min())
    x_max = max(plot_x_ref.max(), x_inner.max(), x_outer.max())
    y_min = min(plot_y_ref.min(), y_inner.min(), y_outer.min())
    y_max = max(plot_y_ref.max(), y_inner.max(), y_outer.max())

    return (plot_x_ref, plot_y_ref, x_inner, y_inner, x_outer, y_outer,
            x_min, x_max, y_min, y_max, drs_zones)


def _plot_drs_zones(example_lap):
    """Plot DRS zones along the track.
    
    Args:
        example_lap: DataFrame or dict with X, Y, DRS columns
        
    Returns:
        List of DRS zone dictionaries
    """
    x_val = example_lap["X"]
    y_val = example_lap["Y"]
    drs_zones = []
    drs_start = None

    for i, val in enumerate(example_lap["DRS"]):
        if val in [10, 12, 14]:
            if drs_start is None:
                drs_start = i
        else:
            if drs_start is not None:
                drs_end = i - 1
                zone = {
                    "start": {"x": x_val.iloc[drs_start], "y": y_val.iloc[drs_start], "index": drs_start},
                    "end": {"x": x_val.iloc[drs_end], "y": y_val.iloc[drs_end], "index": drs_end}
                }
                drs_zones.append(zone)
                drs_start = None
    
    # Handle case where DRS zone extends to end of lap
    if drs_start is not None:
        drs_end = len(example_lap["DRS"]) - 1
        zone = {
            "start": {"x": x_val.iloc[drs_start], "y": y_val.iloc[drs_start], "index": drs_start},
            "end": {"x": x_val.iloc[drs_end], "y": y_val.iloc[drs_end], "index": drs_end}
        }
        drs_zones.append(zone)
    
    return drs_zones


def extract_race_events(frames: List[dict], track_statuses: List[dict], total_laps: int) -> List[dict]:
    """Extract race events from frame data for the progress bar.
    
    This function analyzes the telemetry frames to identify:
    - DNF events (when a driver stops appearing)
    - Leader changes (when the P1 position changes hands)
    - Flag events (from track_statuses)
    
    Args:
        frames: List of frame dictionaries from telemetry
        track_statuses: List of track status events
        total_laps: Total number of laps in the race
        
    Returns:
        List of event dictionaries for the progress bar
    """
    # Import here to avoid circular imports
    from src.ui.components.progress import RaceProgressBarComponent
    
    events = []
    
    if not frames:
        return events
        
    n_frames = len(frames)
    
    # Track drivers present in each frame
    prev_drivers = set()
    
    # Sample frames at regular intervals for performance (every 25 frames = 1 second)
    sample_rate = 25
    
    for i in range(0, n_frames, sample_rate):
        frame = frames[i]
        drivers_data = frame.get("drivers", {})
        current_drivers = set(drivers_data.keys())
        
        # Detect DNFs (drivers who disappeared)
        if prev_drivers:
            dnf_drivers = prev_drivers - current_drivers
            for driver_code in dnf_drivers:
                # Get the lap from previous frame if available
                prev_frame = frames[max(0, i - sample_rate)]
                driver_info = prev_frame.get("drivers", {}).get(driver_code, {})
                lap = driver_info.get("lap", "?")
                
                events.append({
                    "type": RaceProgressBarComponent.EVENT_DNF,
                    "frame": i,
                    "label": driver_code,
                    "lap": lap,
                })
        
        prev_drivers = current_drivers
    
    # Add flag events from track_statuses
    for status in track_statuses:
        status_code = str(status.get("status", ""))
        start_time = status.get("start_time", 0)
        end_time = status.get("end_time")
        
        # Convert time to frame (assuming 25 FPS)
        fps = 25
        start_frame = int(start_time * fps)
        end_frame = int(end_time * fps) if end_time else start_frame + 250  # Default 10 seconds
        
        # This prevents rendering artifacts from pre-race track status events
        # that shouldn't appear on the timeline... Events that span frame 0
        # (start < 0 but end > 0) are kept; the drawing code will clamp them
        if end_frame <= 0:
            continue
        
        # Note: The drawing code also clamps, but normalizing here improves data quality
        if n_frames > 0:
            end_frame = min(end_frame, n_frames)
        
        event_type = None
        if status_code == "2":  # Yellow flag
            event_type = RaceProgressBarComponent.EVENT_YELLOW_FLAG
        elif status_code == "4":  # Safety Car
            event_type = RaceProgressBarComponent.EVENT_SAFETY_CAR
        elif status_code == "5":  # Red flag
            event_type = RaceProgressBarComponent.EVENT_RED_FLAG
        elif status_code in ("6", "7"):  # VSC
            event_type = RaceProgressBarComponent.EVENT_VSC
            
        if event_type:
            events.append({
                "type": event_type,
                "frame": start_frame,
                "end_frame": end_frame,
                "label": "",
                "lap": None,
            })
    
    return events


def draw_finish_line(window, session_type: str = 'R') -> None:
    """Draw checkered finish line on the track.
    
    Args:
        window: The arcade window object (must have track geometry attributes)
        session_type: 'R' for race or 'Q' for qualifying
    """
    if session_type not in ['R', 'Q']:
        print("Invalid session type for finish line drawing...")
        return

    start_inner = None
    start_outer = None

    if session_type == 'Q' and len(window.inner_pts) > 0 and len(window.outer_pts) > 0:
        start_inner = window.inner_pts[0]
        start_outer = window.outer_pts[0]
    elif session_type == 'R' and len(window.screen_inner_points) > 0 and len(window.screen_outer_points) > 0:
        start_inner = window.screen_inner_points[0]
        start_outer = window.screen_outer_points[0]
    else:
        return
    
    # Draw checkered finish line
    if start_inner and start_outer:
        num_squares = 20
        extension = 20
            
        # Calculate direction vector and normalize
        dx = start_outer[0] - start_inner[0]
        dy = start_outer[1] - start_inner[1]
        length = np.sqrt(dx**2 + dy**2)
            
        if length > 0:
            # Normalize direction (unit vector)
            dx_norm = dx / length
            dy_norm = dy / length
                
            # Extend line beyond track limits
            extended_inner = (start_inner[0] - extension * dx_norm, 
                             start_inner[1] - extension * dy_norm)
            extended_outer = (start_outer[0] + extension * dx_norm, 
                             start_outer[1] + extension * dy_norm)
            
            # Draw checkered pattern across extended line
            for i in range(num_squares):
                t1 = i / num_squares  # start of segment
                t2 = (i + 1) / num_squares  # end of segment
                
                x1 = extended_inner[0] + t1 * (extended_outer[0] - extended_inner[0])
                y1 = extended_inner[1] + t1 * (extended_outer[1] - extended_inner[1])
                x2 = extended_inner[0] + t2 * (extended_outer[0] - extended_inner[0])
                y2 = extended_inner[1] + t2 * (extended_outer[1] - extended_inner[1])
                
                color = arcade.color.WHITE if i % 2 == 0 else arcade.color.BLACK
                arcade.draw_line(x1, y1, x2, y2, color, 6)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex color string.

    Args:
        r, g, b: RGB values (0-255).

    Returns:
        Hex color string (e.g., "#FF0000").
    """
    return f"#{r:02X}{g:02X}{b:02X}"


def brighten_color(color: Color | HexColor, amount: float = 0.2) -> Color:
    """Brighten a color.

    Args:
        color: RGB/RGBA tuple or hex string.
        amount: Brightness increase (0.0-1.0).

    Returns:
        Brightened RGB tuple.
    """
    if isinstance(color, str):
        color = hex_to_rgb(color)

    return tuple(min(255, int(c * (1 + amount))) for c in color[:3])


def darken_color(color: Color | HexColor, amount: float = 0.2) -> Color:
    """Darken a color.

    Args:
        color: RGB/RGBA tuple or hex string.
        amount: Darkness increase (0.0-1.0).

    Returns:
        Darkened RGB tuple.
    """
    if isinstance(color, str):
        color = hex_to_rgb(color)

    return tuple(max(0, int(c * (1 - amount))) for c in color[:3])


def blend_colors(color1: Color, color2: Color, ratio: float = 0.5) -> Color:
    """Blend two colors.

    Args:
        color1, color2: RGB/RGBA tuples.
        ratio: Blend ratio (0.0 = color1, 1.0 = color2).

    Returns:
        Blended RGB tuple.
    """
    return tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(color1[:3], color2[:3]))


def is_point_in_rect(
    point_x: float,
    point_y: float,
    rect_x: float,
    rect_y: float,
    rect_width: float,
    rect_height: float,
) -> bool:
    """Check if point is inside rectangle.

    Args:
        point_x, point_y: Point coordinates.
        rect_x, rect_y: Rectangle top-left.
        rect_width, rect_height: Rectangle dimensions.

    Returns:
        True if point is inside rectangle.
    """
    return (
        rect_x <= point_x <= rect_x + rect_width
        and rect_y <= point_y <= rect_y + rect_height
    )


def truncate_text(text: str, max_length: int = 20, suffix: str = "...") -> str:
    """Truncate text to max length.

    Args:
        text: Text to truncate.
        max_length: Maximum length.
        suffix: Suffix to add if truncated.

    Returns:
        Truncated text.
    """
    if len(text) > max_length:
        return text[: max_length - len(suffix)] + suffix
    return text
