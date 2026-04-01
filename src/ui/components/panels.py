"""Info panel components for displaying race and session information.

Includes:
- DriverInfoPanel: Shows selected driver details
- SessionInfoPanel: Race header info (name, round, date)
- WeatherPanel: Current weather conditions
"""

from typing import Any, Dict, Optional

import arcade

from src.architecture.event_bus import EventBus, EventType, UIEvent
from src.architecture.state_manager import PlaybackState, StateManager
from src.config.theme import DEFAULT_THEME
from src.ui.component import ArcadeComponent
from src.ui.utils import draw_rectangle_filled, draw_rectangle_outline, draw_text


class DriverInfoPanel(ArcadeComponent):
    """Displays information about the selected driver."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        state_manager: StateManager,
        event_bus: EventBus,
    ):
        """Initialize driver info panel.
        
        Args:
            x, y: Position.
            width, height: Dimensions.
            state_manager: State manager.
            event_bus: Event bus.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.state = state_manager
        self.event_bus = event_bus

        self.driver_data: Optional[Dict[str, Any]] = None

        # Subscribe to driver selection events
        self.event_bus.subscribe(EventType.DRIVER_SELECTED, self._on_driver_selected)

    def _on_driver_selected(self, event: UIEvent) -> None:
        """Handle driver selection."""
        # In a real implementation, fetch driver data from data provider
        self.driver_data = {"number": event.data, "name": f"Driver {event.data}"}

    def set_driver_data(self, data: Dict[str, Any]) -> None:
        """Set driver data to display.
        
        Args:
            data: Driver data dict with 'number', 'name', 'tyre', 'gap', etc.
        """
        self.driver_data = data

    def draw(self, renderer: Any) -> None:
        """Draw the driver info panel."""
        theme = DEFAULT_THEME

        # Draw background
        draw_rectangle_filled(self.x, self.y, self.width, self.height, theme.colors.bg_dark)
        draw_rectangle_outline(self.x, self.y, self.width, self.height, theme.colors.border)

        if not self.driver_data:
            draw_text("Select a driver", self.x + 10, self.y + self.height - 20, color=theme.colors.text_muted)
            return

        # Draw driver info
        y_offset = self.height - 20
        draw_text(
            f"Driver {self.driver_data.get('number')}",
            self.x + 10,
            self.y + y_offset,
            color=theme.colors.text_primary,
            font_size=14,
        )

        y_offset -= 25
        draw_text(
            f"Name: {self.driver_data.get('name', 'N/A')}",
            self.x + 10,
            self.y + y_offset,
            color=theme.colors.text_secondary,
            font_size=12,
        )

        y_offset -= 25
        draw_text(
            f"Tyre: {self.driver_data.get('tyre', 'N/A')}",
            self.x + 10,
            self.y + y_offset,
            color=theme.colors.text_secondary,
            font_size=12,
        )

        y_offset -= 25
        draw_text(
            f"Gap: {self.driver_data.get('gap', 'N/A')}",
            self.x + 10,
            self.y + y_offset,
            color=theme.colors.text_secondary,
            font_size=12,
        )

    def on_resize(self, width: float, height: float) -> None:
        """Handle resize."""
        self.width = width
        self.height = height

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle input."""
        return False

    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        pass

    def on_event(self, event: UIEvent) -> None:
        """Handle events."""
        pass


class SessionInfoPanel(ArcadeComponent):
    """Displays session header information (event name, round, date)."""

    def __init__(self, x: float, y: float, width: float, height: float):
        """Initialize session info panel.
        
        Args:
            x, y: Position.
            width, height: Dimensions.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.session_data: Dict[str, any] = {
            "event": "Loading...",
            "round": 0,
            "date": "",
            "type": "",
        }

    def set_session_data(self, data: Dict[str, Any]) -> None:
        """Set session data to display.
        
        Args:
            data: Session data dict.
        """
        self.session_data = data

    def draw(self, renderer: Any) -> None:
        """Draw the session info panel."""
        theme = DEFAULT_THEME

        # Draw background
        draw_rectangle_filled(self.x, self.y, self.width, self.height, theme.colors.bg_dark)
        draw_rectangle_outline(self.x, self.y, self.width, self.height, theme.colors.border)

        # Draw session info
        y_offset = self.height - 15
        event_name = self.session_data.get("event", "N/A")
        round_num = self.session_data.get("round", 0)
        draw_text(
            f"Round {round_num}: {event_name}",
            self.x + 10,
            self.y + y_offset,
            color=theme.colors.text_primary,
            font_size=13,
            bold=True,
        )

        y_offset -= 22
        session_type = self.session_data.get("type", "Race")
        date = self.session_data.get("date", "")
        draw_text(
            f"{session_type} - {date}",
            self.x + 10,
            self.y + y_offset,
            color=theme.colors.text_secondary,
            font_size=11,
        )

    def on_resize(self, width: float, height: float) -> None:
        """Handle resize."""
        self.width = width
        self.height = height

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle input."""
        return False

    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        pass

    def on_event(self, event: UIEvent) -> None:
        """Handle events."""
        pass


class WeatherPanel(ArcadeComponent):
    """Displays current weather conditions."""

    def __init__(self, x: float, y: float, width: float, height: float):
        """Initialize weather panel.
        
        Args:
            x, y: Position.
            width, height: Dimensions.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.weather_data: Dict[str, Any] = {
            "temp": 0,
            "wind_speed": 0,
            "wind_direction": "N",
            "track_temp": 0,
            "humidity": 0,
        }

    def set_weather_data(self, data: Dict[str, Any]) -> None:
        """Set weather data to display.
        
        Args:
            data: Weather data dict.
        """
        self.weather_data = data

    def draw(self, renderer: Any) -> None:
        """Draw the weather panel."""
        theme = DEFAULT_THEME

        # Draw background
        draw_rectangle_filled(self.x, self.y, self.width, self.height, theme.colors.bg_dark)
        draw_rectangle_outline(self.x, self.y, self.width, self.height, theme.colors.border)

        # Draw weather info
        y_offset = self.height - 15
        temp = self.weather_data.get("temp", 0)
        draw_text(
            f"Temp: {temp}°C",
            self.x + 10,
            self.y + y_offset,
            color=theme.colors.text_primary,
            font_size=11,
        )

        y_offset -= 20
        wind_speed = self.weather_data.get("wind_speed", 0)
        wind_dir = self.weather_data.get("wind_direction", "N")
        draw_text(
            f"Wind: {wind_speed} km/h {wind_dir}",
            self.x + 10,
            self.y + y_offset,
            color=theme.colors.text_secondary,
            font_size=10,
        )

    def on_resize(self, width: float, height: float) -> None:
        """Handle resize."""
        self.width = width
        self.height = height

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle input."""
        return False

    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        pass

    def on_event(self, event: UIEvent) -> None:
        """Handle events."""
        pass
