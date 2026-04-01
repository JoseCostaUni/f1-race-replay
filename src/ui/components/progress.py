"""Progress bar and timeline components for race replay.

Includes:
- RaceTimelineComponent: Displays race progress timeline with event markers
- RaceEventMarkerComponent: Reusable event marker (DNF, safety car, etc.)
- RaceEventLegendComponent: Legend showing event status meanings
- RaceProgressBarComponent: Combined progress + controls
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional, Tuple

import arcade

from src.architecture.event_bus import EventBus, EventType, UIEvent
from src.architecture.state_manager import PlaybackState, StateManager
from src.config.theme import DEFAULT_THEME
from src.ui.component import ArcadeComponent
from src.ui.utils import draw_rectangle_filled, draw_rectangle_outline, draw_text, draw_line


class RaceEventMarkerComponent(ArcadeComponent):
    """Reusable race event marker (DNF, safety car, red flag, etc.)."""

    def __init__(self, event_type: str, frame: int, label: str):
        """Initialize event marker.
        
        Args:
            event_type: Type of event (dnf, safety_car, etc.)
            frame: Frame number where event occurred.
            label: Display label for the event.
        """
        self.event_type = event_type
        self.frame = frame
        self.label = label

    def draw(self, renderer: Any) -> None:
        """Draw the event marker."""
        pass

    def on_resize(self, width: float, height: float) -> None:
        """Handle resize."""
        pass

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle input."""
        return False

    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        pass

    def on_event(self, event: UIEvent) -> None:
        """Handle events."""
        pass


class RaceEventLegendComponent(ArcadeComponent):
    """Legend showing what different event colors/symbols mean."""

    def __init__(self, x: float = 20, y: float = 20):
        """Initialize legend.
        
        Args:
            x, y: Position in window.
        """
        self.x = x
        self.y = y
        self.visible = True

    def draw(self, renderer: Any) -> None:
        """Draw the event legend."""
        if not self.visible:
            return

        theme = DEFAULT_THEME
        events = [
            ("DNF", theme.colors.dnf),
            ("Safety Car", theme.colors.safety_car),
            ("V-SC", theme.colors.virtual_safety_car),
            ("Red Flag", theme.colors.red_flag),
        ]

        current_y = self.y
        for label, color in events:
            # Color box
            draw_rectangle_filled(self.x, current_y - 10, 12, 12, color)

            # Label
            draw_text(label, self.x + 20, current_y - 5, color=theme.colors.text_primary, font_size=11)

            current_y -= 20

    def on_resize(self, width: float, height: float) -> None:
        """Handle resize."""
        pass

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle input."""
        return False

    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        pass

    def on_event(self, event: UIEvent) -> None:
        """Handle events."""
        pass


class RaceTimelineComponent(ArcadeComponent):
    """Displays race progress as a timeline with event markers."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        state_manager: StateManager,
        event_bus: EventBus,
    ):
        """Initialize timeline.
        
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

        self.total_frames = 0
        self.events: List[RaceEventMarkerComponent] = []
        self.is_dragging = False

        # Subscribe to state changes
        self.event_bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._on_frame_changed)

    def _on_frame_changed(self, event: UIEvent) -> None:
        """Handle frame change event."""
        # Timeline updates when frame changes
        pass

    def set_total_frames(self, total: int) -> None:
        """Set total number of frames in the race.
        
        Args:
            total: Total frame count.
        """
        self.total_frames = total

    def add_event(self, event: RaceEventMarkerComponent) -> None:
        """Add an event marker.
        
        Args:
            event: Event marker to add.
        """
        self.events.append(event)

    def draw(self, renderer: Any) -> None:
        """Draw the timeline."""
        if self.total_frames <= 0:
            return

        theme = DEFAULT_THEME

        # Draw background
        draw_rectangle_filled(self.x, self.y, self.width, self.height, theme.colors.bg_medium)
        draw_rectangle_outline(self.x, self.y, self.width, self.height, theme.colors.border)

        # Draw timeline track
        track_y = self.y + self.height // 2
        draw_line(
            self.x + 10,
            track_y,
            self.x + self.width - 10,
            track_y,
            color=theme.colors.border,
            width=2,
        )

        # Draw current position indicator
        current_frame = self.state.get_frame()
        progress_ratio = current_frame / self.total_frames if self.total_frames > 0 else 0
        indicator_x = self.x + 10 + (self.width - 20) * progress_ratio

        draw_rectangle_filled(indicator_x - 5, track_y - 10, 10, 20, theme.colors.primary)

        # Draw event markers
        for evt in self.events:
            event_ratio = evt.frame / self.total_frames if self.total_frames > 0 else 0
            marker_x = self.x + 10 + (self.width - 20) * event_ratio
            draw_rectangle_filled(marker_x - 2, track_y - 5, 4, 10, evt.event_type)

    def on_resize(self, width: float, height: float) -> None:
        """Handle resize."""
        self.width = width - 20

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle mouse input to seek timeline."""
        if event_type == "mouse_press":
            x = kwargs.get("x", 0)
            if self.x <= x <= self.x + self.width:
                # Calculate frame from mouse position
                progress_ratio = (x - self.x - 10) / (self.width - 20)
                new_frame = int(self.total_frames * progress_ratio)
                self.event_bus.emit(EventType.FRAME_INDEX_CHANGED, new_frame)
                self.is_dragging = True
                return True

        elif event_type == "mouse_release":
            self.is_dragging = False

        elif event_type == "mouse_motion" and self.is_dragging:
            x = kwargs.get("x", 0)
            if self.x <= x <= self.x + self.width:
                progress_ratio = (x - self.x - 10) / (self.width - 20)
                new_frame = int(self.total_frames * progress_ratio)
                self.event_bus.emit(EventType.FRAME_INDEX_CHANGED, new_frame)
                return True

        return False

    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        pass

    def on_event(self, event: UIEvent) -> None:
        """Handle events."""
        pass


class RaceProgressBarComponent(ArcadeComponent):
    """Combined progress bar with timeline, events, and legend."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        state_manager: StateManager,
        event_bus: EventBus,
    ):
        """Initialize progress bar.
        
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

        # Sub-components
        self.timeline = RaceTimelineComponent(
            x, y + 40, width, 40, state_manager, event_bus
        )
        self.legend = RaceEventLegendComponent(x, y + 80)

    def set_total_frames(self, total: int) -> None:
        """Set total frames."""
        self.timeline.set_total_frames(total)

    def add_event(self, event: RaceEventMarkerComponent) -> None:
        """Add event marker."""
        self.timeline.add_event(event)

    def draw(self, renderer: Any) -> None:
        """Draw the progress bar and sub-components."""
        self.timeline.draw(renderer)
        self.legend.draw(renderer)

    def on_resize(self, width: float, height: float) -> None:
        """Handle resize."""
        self.width = width
        self.timeline.on_resize(width, height)

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle input."""
        return self.timeline.handle_input(event_type, **kwargs)

    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        self.timeline.on_state_change(state)
        self.legend.on_state_change(state)

    def on_event(self, event: UIEvent) -> None:
        """Handle events."""
        self.timeline.on_event(event)
        self.legend.on_event(event)
