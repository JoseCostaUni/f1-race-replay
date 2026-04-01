"""Layout configuration and positioning helpers for F1 Race Replay UI.

Centralizes all layout constants, margins, and positioning rules to make the UI
responsive and maintainable.
"""

from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


class Anchor(Enum):
    """Anchor points for component positioning."""

    TOP_LEFT = "top-left"
    TOP_CENTER = "top-center"
    TOP_RIGHT = "top-right"
    CENTER_LEFT = "center-left"
    CENTER = "center"
    CENTER_RIGHT = "center-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_RIGHT = "bottom-right"


class Point(NamedTuple):
    """2D point."""

    x: float
    y: float


@dataclass
class ComponentLayout:
    """Layout configuration for a single component."""

    width: float
    height: float
    margin_top: float = 0
    margin_bottom: float = 0
    margin_left: float = 0
    margin_right: float = 0
    padding: float = 8
    anchor: Anchor = Anchor.TOP_LEFT

    @property
    def margin_horizontal(self) -> float:
        """Total horizontal margin."""
        return self.margin_left + self.margin_right

    @property
    def margin_vertical(self) -> float:
        """Total vertical margin."""
        return self.margin_top + self.margin_bottom

    @property
    def inner_width(self) -> float:
        """Width available for content."""
        return self.width - (2 * self.padding)

    @property
    def inner_height(self) -> float:
        """Height available for content."""
        return self.height - (2 * self.padding)


@dataclass
class RaceReplayLayout:
    """Layout configuration for race replay window."""

    # Window margins
    margin: int = 20
    right_ui_margin: int = 320  # Right-side UI panel width

    # Leaderboard
    leaderboard_width: int = 300
    leaderboard_x: int = 0  # Calculated as window.width - right_ui_margin + margin
    leaderboard_y: int = 220
    leaderboard_height: int = 600

    # Driver info panel
    driver_info_width: int = 300
    driver_info_height: int = 180
    driver_info_x: int = 0  # Calculated
    driver_info_y: int = 20

    # Race controls
    controls_height: int = 60
    controls_y: int = 0  # Calculated from window.height - controls_height - margin

    # Race progress bar
    progress_bar_height: int = 120
    progress_bar_margin_bottom: int = 80

    # Weather panel
    weather_width: int = 150
    weather_height: int = 80
    weather_x: int = 20
    weather_y: int = 20

    # Session info panel
    session_info_width: int = 280
    session_info_height: int = 80
    session_info_x: int = 300
    session_info_y: int = 20

    def get_leaderboard_position(self, window_width: float, window_height: float) -> Point:
        """Calculate leaderboard position based on window size."""
        x = max(self.margin, window_width - self.right_ui_margin + self.margin)
        return Point(x, self.leaderboard_y)

    def get_driver_info_position(self, window_width: float) -> Point:
        """Calculate driver info position based on window size."""
        x = max(self.margin, window_width - self.right_ui_margin + self.margin)
        return Point(x, self.driver_info_y)

    def get_controls_position(self, window_height: float) -> Point:
        """Calculate controls position (bottom of window)."""
        y = window_height - self.controls_height - self.margin
        return Point(self.margin, y)

    def get_progress_bar_position(self, window_height: float) -> Point:
        """Calculate progress bar position."""
        y = window_height - self.controls_height - self.progress_bar_height - self.progress_bar_margin_bottom
        return Point(self.margin, y)


@dataclass
class QualifyingLayout(RaceReplayLayout):
    """Layout configuration for qualifying replay window (inherits from race)."""

    # Qualifying has slightly different layout
    leaderboard_width: int = 350
    progress_bar_height: int = 80


@dataclass
class InsightWindowLayout:
    """Layout configuration for insight windows (PySide6)."""

    default_width: int = 1200
    default_height: int = 800
    min_width: int = 800
    min_height: int = 600

    # Panel layouts
    chart_padding: int = 16
    sidebar_width: int = 250
    toolbar_height: int = 40


class LayoutManager:
    """Manages layout calculations for responsive UI."""

    def __init__(self, layout_config: ComponentLayout):
        """Initialize layout manager.

        Args:
            layout_config: Layout configuration dataclass.
        """
        self.config = layout_config

    def calculate_grid(
        self, cols: int, rows: int, available_width: float, available_height: float
    ) -> list[list[ComponentLayout]]:
        """Calculate grid layout for components.

        Args:
            cols: Number of columns.
            rows: Number of rows.
            available_width: Total available width.
            available_height: Total available height.

        Returns:
            2D list of ComponentLayout for each grid cell.
        """
        col_width = available_width / cols
        row_height = available_height / rows

        grid = []
        for r in range(rows):
            row = []
            for c in range(cols):
                layout = ComponentLayout(
                    width=col_width,
                    height=row_height,
                    margin_left=c * col_width,
                    margin_top=r * row_height,
                )
                row.append(layout)
            grid.append(row)

        return grid

    def calculate_flex(self, components_count: int, direction: str = "row") -> list[ComponentLayout]:
        """Calculate flex layout for components.

        Args:
            components_count: Number of components to layout.
            direction: "row" or "column".

        Returns:
            List of ComponentLayout for each component.
        """
        # This is a simple implementation; can be enhanced with flex properties
        layouts = []
        for i in range(components_count):
            layout = ComponentLayout(
                width=100 / components_count if direction == "row" else 100,
                height=100 if direction == "row" else 100 / components_count,
            )
            layouts.append(layout)
        return layouts


# Default layout instances
RACE_REPLAY_LAYOUT = RaceReplayLayout()
QUALIFYING_LAYOUT = QualifyingLayout()
INSIGHT_WINDOW_LAYOUT = InsightWindowLayout()
