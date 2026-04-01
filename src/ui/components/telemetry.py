"""Telemetry visualization components (charts, graphs, etc.).

Includes:
- ChartComponent: Abstract base for chart components
- QualifyingLapTimeComponent: Sector times breakdown visualization
- TyreComparisonComponent: Tyre degradation visualization
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional

import arcade

from src.architecture.event_bus import EventBus, EventType, UIEvent
from src.architecture.state_manager import PlaybackState, StateManager
from src.config.theme import DEFAULT_THEME
from src.ui.component import ArcadeComponent
from src.ui.utils import draw_rectangle_filled, draw_rectangle_outline, draw_text, draw_line


class ChartComponent(ArcadeComponent):
    """Abstract base class for chart/graph components."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        state_manager: StateManager,
        event_bus: EventBus,
    ):
        """Initialize chart component.
        
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

    @abstractmethod
    def draw(self, renderer: Any) -> None:
        """Draw the chart."""
        pass

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

    def _draw_axes(
        self, margin: float = 40, x_label: str = "", y_label: str = ""
    ) -> tuple[float, float, float, float]:
        """Draw chart axes and return usable area.
        
        Args:
            margin: Margin around chart.
            x_label: X-axis label.
            y_label: Y-axis label.
            
        Returns:
            Tuple of (x_start, y_start, x_end, y_end) for usable area.
        """
        theme = DEFAULT_THEME

        # Draw background
        draw_rectangle_filled(self.x, self.y, self.width, self.height, theme.colors.bg_dark)
        draw_rectangle_outline(self.x, self.y, self.width, self.height, theme.colors.border)

        # Calculate usable area
        x_start = self.x + margin
        y_start = self.y + margin
        x_end = self.x + self.width - margin
        y_end = self.y + self.height - margin

        # Draw axes
        draw_line(x_start, y_start, x_start, y_end, color=theme.colors.border, width=2)
        draw_line(x_start, y_start, x_end, y_start, color=theme.colors.border, width=2)

        # Draw labels
        if x_label:
            draw_text(x_label, (x_start + x_end) / 2, self.y + 10, color=theme.colors.text_secondary)
        if y_label:
            draw_text(y_label, self.x + 10, (y_start + y_end) / 2, color=theme.colors.text_secondary)

        return x_start, y_start, x_end, y_end


class QualifyingLapTimeComponent(ChartComponent):
    """Visualizes sector times for qualifying session."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        state_manager: StateManager,
        event_bus: EventBus,
    ):
        """Initialize sector times chart."""
        super().__init__(x, y, width, height, state_manager, event_bus)
        self.lap_data: List[Dict[str, Any]] = []

    def set_lap_data(self, laps: List[Dict[str, Any]]) -> None:
        """Set lap data to display.
        
        Args:
            laps: List of lap dicts with 'lap_num', 'sector1', 'sector2', 'sector3', 'total'.
        """
        self.lap_data = laps

    def draw(self, renderer: Any) -> None:
        """Draw the sector times chart."""
        theme = DEFAULT_THEME

        x_start, y_start, x_end, y_end = self._draw_axes(
            margin=40, x_label="Lap", y_label="Time (s)"
        )

        if not self.lap_data:
            draw_text(
                "No lap data", (x_start + x_end) / 2, (y_start + y_end) / 2,
                color=theme.colors.text_muted
            )
            return

        # Find min/max times for scaling
        all_times = []
        for lap in self.lap_data:
            all_times.extend([lap.get(f"sector{i}", 0) for i in [1, 2, 3]])

        min_time = min(all_times) if all_times else 0
        max_time = max(all_times) if all_times else 100
        time_range = max_time - min_time if max_time > min_time else 1

        # Draw bars for each lap
        usable_width = x_end - x_start
        usable_height = y_end - y_start
        bar_width = usable_width / (len(self.lap_data) * 4) if self.lap_data else 0

        for lap_idx, lap in enumerate(self.lap_data):
            for sector_idx in range(3):
                sector_time = lap.get(f"sector{sector_idx + 1}", 0)

                # Calculate bar height
                bar_height = (sector_time - min_time) / time_range * usable_height

                # Calculate position
                bar_x = x_start + (lap_idx * 4 + sector_idx) * bar_width
                bar_y = y_start

                # Draw bar (different color per sector)
                colors = [theme.colors.primary, theme.colors.warning, theme.colors.error]
                draw_rectangle_filled(
                    bar_x, bar_y, bar_width - 2, bar_height, colors[sector_idx]
                )

    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        # Update chart based on selected lap
        pass


class TyreComparisonComponent(ChartComponent):
    """Visualizes tyre degradation over race distance."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        state_manager: StateManager,
        event_bus: EventBus,
    ):
        """Initialize tyre comparison chart."""
        super().__init__(x, y, width, height, state_manager, event_bus)
        self.tyre_data: Dict[str, List[float]] = {}

    def set_tyre_data(self, data: Dict[str, List[float]]) -> None:
        """Set tyre degradation data.
        
        Args:
            data: Dict mapping driver_num to list of tyre health values over race.
        """
        self.tyre_data = data

    def draw(self, renderer: Any) -> None:
        """Draw the tyre degradation chart."""
        theme = DEFAULT_THEME

        x_start, y_start, x_end, y_end = self._draw_axes(
            margin=40, x_label="Race Distance", y_label="Tyre Health (%)"
        )

        if not self.tyre_data:
            draw_text(
                "No tyre data",  (x_start + x_end) / 2, (y_start + y_end) / 2,
                color=theme.colors.text_muted
            )
            return

        # Draw line for each driver
        for driver_num, tyre_health in self.tyre_data.items():
            if not tyre_health:
                continue

            usable_width = x_end - x_start
            usable_height = y_end - y_start
            x_step = usable_width / len(tyre_health)

            # Draw line connecting points
            for i in range(len(tyre_health) - 1):
                x1 = x_start + i * x_step
                y1 = y_start + (tyre_health[i] / 100) * usable_height

                x2 = x_start + (i + 1) * x_step
                y2 = y_start + (tyre_health[i + 1] / 100) * usable_height

                draw_line(x1, y1, x2, y2, color=theme.colors.primary, width=2)

                # Draw point
                arcade.draw_circle_filled(x1, y1, 2, theme.colors.primary)

    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        pass
