"""Layout calculation helpers for responsive Arcade UI.

Provides utilities for calculating component positions and sizes based on
window dimensions and layout constraints. Replaces hardcoded x, y, width, height
values with a declarative layout system.

Example:
    >>> layout_helper = LayoutHelper()
    >>> leaderboard_bounds = layout_helper.anchor_component(
    ...     window_width=1920,
    ...     window_height=1080,
    ...     component_width=300,
    ...     component_height=600,
    ...     anchor="top-right",
    ...     margin_right=20,
    ...     margin_top=20
    ... )
"""

from dataclasses import dataclass
from enum import Enum
from typing import NamedTuple


class Anchor(Enum):
    """Anchor points for positioning."""

    TOP_LEFT = "top-left"
    TOP_CENTER = "top-center"
    TOP_RIGHT = "top-right"
    CENTER_LEFT = "center-left"
    CENTER = "center"
    CENTER_RIGHT = "center-right"
    BOTTOM_LEFT = "bottom-left"
    BOTTOM_CENTER = "bottom-center"
    BOTTOM_RIGHT = "bottom-right"


class Bounds(NamedTuple):
    """Component bounding box."""

    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        """Right edge position."""
        return self.x + self.width

    @property
    def bottom(self) -> float:
        """Bottom edge position."""
        return self.y + self.height

    @property
    def center_x(self) -> float:
        """Center X position."""
        return self.x + self.width / 2

    @property
    def center_y(self) -> float:
        """Center Y position."""
        return self.y + self.height / 2

    def contains_point(self, x: float, y: float) -> bool:
        """Check if point is inside bounds.

        Args:
            x, y: Point coordinates.

        Returns:
            True if point is inside bounds.
        """
        return self.x <= x <= self.right and self.y <= y <= self.bottom


class LayoutHelper:
    """Layout calculation helper for responsive positioning."""

    @staticmethod
    def anchor_component(
        window_width: float,
        window_height: float,
        component_width: float,
        component_height: float,
        anchor: Anchor | str = Anchor.TOP_LEFT,
        margin_left: float = 0,
        margin_right: float = 0,
        margin_top: float = 0,
        margin_bottom: float = 0,
    ) -> Bounds:
        """Calculate component bounds based on anchor point.

        Args:
            window_width: Parent window width.
            window_height: Parent window height.
            component_width: Component width.
            component_height: Component height.
            anchor: Anchor point.
            margin_left: Left margin.
            margin_right: Right margin.
            margin_top: Top margin.
            margin_bottom: Bottom margin.

        Returns:
            Bounds (x, y, width, height) for the component.

        Example:
            >>> bounds = LayoutHelper.anchor_component(
            ...     window_width=1920,
            ...     window_height=1080,
            ...     component_width=300,
            ...     component_height=600,
            ...     anchor="top-right",
            ...     margin_right=20,
            ...     margin_top=20
            ... )
            >>> print(f"Position: ({bounds.x}, {bounds.y})")
        """
        if isinstance(anchor, str):
            anchor = Anchor(anchor)

        x, y = 0, 0

        match anchor:
            case Anchor.TOP_LEFT:
                x = margin_left
                y = window_height - component_height - margin_top

            case Anchor.TOP_CENTER:
                x = (window_width - component_width) / 2
                y = window_height - component_height - margin_top

            case Anchor.TOP_RIGHT:
                x = window_width - component_width - margin_right
                y = window_height - component_height - margin_top

            case Anchor.CENTER_LEFT:
                x = margin_left
                y = (window_height - component_height) / 2

            case Anchor.CENTER:
                x = (window_width - component_width) / 2
                y = (window_height - component_height) / 2

            case Anchor.CENTER_RIGHT:
                x = window_width - component_width - margin_right
                y = (window_height - component_height) / 2

            case Anchor.BOTTOM_LEFT:
                x = margin_left
                y = margin_bottom

            case Anchor.BOTTOM_CENTER:
                x = (window_width - component_width) / 2
                y = margin_bottom

            case Anchor.BOTTOM_RIGHT:
                x = window_width - component_width - margin_right
                y = margin_bottom

        return Bounds(x, y, component_width, component_height)

    @staticmethod
    def grid_layout(
        window_width: float,
        window_height: float,
        cols: int,
        rows: int,
        margin: float = 0,
        gap: float = 0,
    ) -> list[list[Bounds]]:
        """Calculate grid layout for multiple components.

        Args:
            window_width: Parent window width.
            window_height: Parent window height.
            cols: Number of columns.
            rows: Number of rows.
            margin: Margin around edge of grid.
            gap: Gap between cells.

        Returns:
            2D list of Bounds for each grid cell.

        Example:
            >>> grid = LayoutHelper.grid_layout(
            ...     window_width=1920,
            ...     window_height=1080,
            ...     cols=3,
            ...     rows=2,
            ...     margin=20,
            ...     gap=10
            ... )
            >>> for row in grid:
            ...     for cell in row:
            ...         print(f"Cell: {cell}")
        """
        available_width = window_width - 2 * margin
        available_height = window_height - 2 * margin

        cell_width = (available_width - (cols - 1) * gap) / cols
        cell_height = (available_height - (rows - 1) * gap) / rows

        grid = []
        for r in range(rows):
            row = []
            for c in range(cols):
                x = margin + c * (cell_width + gap)
                y = margin + r * (cell_height + gap)
                row.append(Bounds(x, y, cell_width, cell_height))
            grid.append(row)

        return grid

    @staticmethod
    def flex_layout(
        window_width: float,
        window_height: float,
        count: int,
        direction: str = "row",
        margin: float = 0,
        gap: float = 0,
    ) -> list[Bounds]:
        """Calculate flex layout for components (row or column).

        Args:
            window_width: Parent window width.
            window_height: Parent window height.
            count: Number of components.
            direction: "row" or "column".
            margin: Margin around edge.
            gap: Gap between items.

        Returns:
            List of Bounds for each component.

        Example:
            >>> rects = LayoutHelper.flex_layout(
            ...     window_width=1920,
            ...     window_height=1080,
            ...     count=4,
            ...     direction="row",
            ...     margin=20,
            ...     gap=10
            ... )
        """
        if direction == "row":
            available_width = window_width - 2 * margin
            item_width = (available_width - (count - 1) * gap) / count
            item_height = window_height - 2 * margin

            return [
                Bounds(
                    margin + i * (item_width + gap),
                    margin,
                    item_width,
                    item_height,
                )
                for i in range(count)
            ]

        elif direction == "column":
            available_height = window_height - 2 * margin
            item_width = window_width - 2 * margin
            item_height = (available_height - (count - 1) * gap) / count

            return [
                Bounds(
                    margin,
                    margin + i * (item_height + gap),
                    item_width,
                    item_height,
                )
                for i in range(count)
            ]

        else:
            raise ValueError(f"Invalid direction: {direction}")

    @staticmethod
    def scale_component(
        component_bounds: Bounds,
        scale_x: float,
        scale_y: float | None = None,
    ) -> Bounds:
        """Scale a component's bounds.

        Args:
            component_bounds: Original bounds.
            scale_x: X scale factor.
            scale_y: Y scale factor (defaults to scale_x if not provided).

        Returns:
            Scaled bounds.
        """
        if scale_y is None:
            scale_y = scale_x

        return Bounds(
            component_bounds.x,
            component_bounds.y,
            component_bounds.width * scale_x,
            component_bounds.height * scale_y,
        )

    @staticmethod
    def offset_component(
        component_bounds: Bounds,
        offset_x: float,
        offset_y: float,
    ) -> Bounds:
        """Offset a component's position.

        Args:
            component_bounds: Original bounds.
            offset_x: X offset.
            offset_y: Y offset.

        Returns:
            Offset bounds.
        """
        return Bounds(
            component_bounds.x + offset_x,
            component_bounds.y + offset_y,
            component_bounds.width,
            component_bounds.height,
        )
