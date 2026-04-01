"""Leaderboard components for displaying driver standings and lap times.

Includes:
- LeaderboardComponent: Race leaderboard with driver info 
- LapTimeLeaderboardComponent: Qualifying leaderboard with sector times
- BaseLeaderboardComponent: Abstract base to reduce duplication
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional

import arcade

from src.architecture.event_bus import EventBus, EventType, UIEvent
from src.architecture.state_manager import PlaybackState, StateManager
from src.config.theme import DEFAULT_THEME, get_driver_color
from src.ui.component import ArcadeComponent
from src.ui.utils import draw_rectangle_filled, draw_rectangle_outline, draw_text


class BaseLeaderboardComponent(ArcadeComponent):
    """Abstract base for leaderboard components.
    
    Handles common leaderboard functionality like:
    - Driver positioning and sorting
    - Color coding by team/driver
    - Text rendering with proper alignment
    - Mouse interaction for driver selection
    """

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        state_manager: StateManager,
        event_bus: EventBus,
    ):
        """Initialize leaderboard component.
        
        Args:
            x, y: Position in window.
            width, height: Dimensions.
            state_manager: State manager for accessing playback state.
            event_bus: Event bus for emitting/subscribing to events.
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.state = state_manager
        self.event_bus = event_bus

        self.drivers: List[Dict[str, Any]] = []
        self.selected_driver: Optional[int] = None
        self.visible = True

        # Subscribe to state changes
        self.event_bus.subscribe(EventType.DRIVER_SELECTED, self._on_driver_selected)

    def _on_driver_selected(self, event: UIEvent) -> None:
        """Handle driver selection event."""
        self.selected_driver = event.data

    @abstractmethod
    def draw(self, renderer: Any) -> None:
        """Draw the leaderboard."""
        pass

    @abstractmethod
    def on_resize(self, width: float, height: float) -> None:
        """Handle window resize."""
        pass

    @abstractmethod
    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle mouse/keyboard input."""
        pass

    def on_state_change(self, state: PlaybackState) -> None:
        """Update when playback state changes."""
        # Components typically update their internal representation here
        pass

    def on_event(self, event: UIEvent) -> None:
        """Handle custom events."""
        pass


class LeaderboardComponent(BaseLeaderboardComponent):
    """Race leaderboard displaying driver standings, positions, and gaps."""

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 300,
        height: float = 600,
        state_manager: Optional[StateManager] = None,
        event_bus: Optional[EventBus] = None,
    ):
        """Initialize race leaderboard.
        
        Args:
            x, y: Position.
            width, height: Dimensions.
            state_manager: State manager (injected).
            event_bus: Event bus (injected).
        """
        if state_manager is None or event_bus is None:
            raise ValueError("state_manager and event_bus are required")

        super().__init__(x, y, width, height, state_manager, event_bus)

    def set_drivers(self, drivers: List[Dict[str, Any]]) -> None:
        """Set driver data for display.
        
        Args:
            drivers: List of driver dicts with keys like 'number', 'name', 'gap', 'tyre'.
        """
        self.drivers = drivers

    def draw(self, renderer: Any) -> None:
        """Draw the leaderboard."""
        if not self.visible or not self.drivers:
            return

        theme = DEFAULT_THEME
        row_height = 30
        starting_y = self.y + self.height - row_height

        # Draw background
        draw_rectangle_filled(self.x, self.y, self.width, self.height, theme.colors.bg_dark)
        draw_rectangle_outline(self.x, self.y, self.width, self.height, theme.colors.border)

        # Draw header
        draw_rectangle_filled(
            self.x, starting_y, self.width, row_height, theme.colors.bg_medium
        )
        draw_text("POS", self.x + 5, starting_y + 15, color=theme.colors.text_primary, font_size=12)
        draw_text(
            "DRIVER", self.x + 40, starting_y + 15, color=theme.colors.text_primary, font_size=12
        )
        draw_text(
            "GAP", self.x + self.width - 50, starting_y + 15, color=theme.colors.text_primary, font_size=12
        )

        # Draw drivers
        for i, driver in enumerate(self.drivers[:15]):  # Show top 15
            row_y = starting_y - (i + 1) * row_height

            # Highlight selected driver
            bg_color = theme.colors.button_active if driver.get("number") == self.selected_driver else theme.colors.bg_light

            draw_rectangle_filled(self.x, row_y, self.width, row_height, bg_color)
            draw_rectangle_outline(self.x, row_y, self.width, row_height, theme.colors.border, 1)

            # Driver color indicator
            driver_color = get_driver_color(i)
            draw_rectangle_filled(self.x + 2, row_y + 2, 6, row_height - 4, driver_color)

            # Position
            position = str(driver.get("position", i + 1))
            draw_text(position, self.x + 12, row_y + 15, color=theme.colors.text_primary, font_size=11)

            # Driver name/number
            driver_name = driver.get("name", f"P{driver.get('number', i + 1)}")
            draw_text(driver_name, self.x + 40, row_y + 15, color=theme.colors.text_primary, font_size=11)

            # Gap
            gap = driver.get("gap", "")
            draw_text(
                gap, self.x + self.width - 50, row_y + 15, color=theme.colors.text_secondary, font_size=10
            )

    def on_resize(self, width: float, height: float) -> None:
        """Handle window resize."""
        # Update position if needed (responsive layout)
        pass

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle mouse clicks to select drivers."""
        if event_type == "mouse_press":
            x, y = kwargs.get("x", 0), kwargs.get("y", 0)
            if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
                # Calculate which driver was clicked
                row_height = 30
                row_index = int((self.y + self.height - y) / row_height) - 1
                if 0 <= row_index < len(self.drivers):
                    driver = self.drivers[row_index]
                    self.event_bus.emit(EventType.DRIVER_SELECTED, driver.get("number"))
                    return True
        return False


class LapTimeLeaderboardComponent(BaseLeaderboardComponent):
    """Qualifying leaderboard with sector times breakdown."""

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        width: float = 350,
        height: float = 600,
        state_manager: Optional[StateManager] = None,
        event_bus: Optional[EventBus] = None,
    ):
        """Initialize qualifying leaderboard."""
        if state_manager is None or event_bus is None:
            raise ValueError("state_manager and event_bus are required")

        super().__init__(x, y, width, height, state_manager, event_bus)

    def set_qualifying_data(self, drivers: List[Dict[str, Any]]) -> None:
        """Set qualifying session data.
        
        Args:
            drivers: List of driver dicts with 'number', 'name', 'lap_time', 'sector_times'.
        """
        self.drivers = drivers

    def draw(self, renderer: Any) -> None:
        """Draw the qualifying leaderboard."""
        if not self.visible or not self.drivers:
            return

        theme = DEFAULT_THEME
        row_height = 25
        starting_y = self.y + self.height - row_height

        # Draw background
        draw_rectangle_filled(self.x, self.y, self.width, self.height, theme.colors.bg_dark)
        draw_rectangle_outline(self.x, self.y, self.width, self.height, theme.colors.border)

        # Draw header
        headers = ["POS", "DRIVER", "LAP TIME", "S1", "S2", "S3"]
        col_widths = [30, 80, 70, 50, 50, 50]
        current_x = self.x

        draw_rectangle_filled(self.x, starting_y, self.width, row_height, theme.colors.bg_medium)

        for header, col_width in zip(headers, col_widths):
            draw_text(
                header,
                current_x + 5,
                starting_y + 12,
                color=theme.colors.text_primary,
                font_size=10,
            )
            current_x += col_width

        # Draw drivers
        for i, driver in enumerate(self.drivers[:20]):
            row_y = starting_y - (i + 1) * row_height

            # Highlight selected
            bg_color = (
                theme.colors.button_active
                if driver.get("number") == self.selected_driver
                else theme.colors.bg_light
            )
            draw_rectangle_filled(self.x, row_y, self.width, row_height, bg_color)
            draw_rectangle_outline(self.x, row_y, self.width, row_height, theme.colors.border, 1)

            # Draw row data
            current_x = self.x
            position = str(driver.get("position", i + 1))
            draw_text(position, current_x + 5, row_y + 12, color=theme.colors.text_primary, font_size=9)
            current_x += 30

            driver_name = driver.get("name", f"P{driver.get('number', i + 1)}")
            draw_text(driver_name, current_x + 5, row_y + 12, color=theme.colors.text_primary, font_size=9)
            current_x += 80

            lap_time = driver.get("lap_time", "")
            draw_text(
                lap_time, current_x + 5, row_y + 12, color=theme.colors.text_secondary, font_size=9
            )
            current_x += 70

            sectors = driver.get("sector_times", [])
            for sector_time in sectors:
                draw_text(sector_time, current_x + 5, row_y + 12, color=theme.colors.text_muted, font_size=8)
                current_x += 50

    def on_resize(self, width: float, height: float) -> None:
        """Handle window resize."""
        pass

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle mouse input."""
        return False
