"""Control and overlay components for playback and help.

Includes:
- RaceControlsComponent: Playback controls (play/pause, speed, etc.)
- KeyBindingOverlay: Help overlay with keyboard shortcuts (formerly ControlsPopupComponent)
- HelpLegendComponent: Reusable help/legend widget
"""

from typing import Any, Dict, List, Optional, Tuple

import arcade

from src.architecture.event_bus import EventBus, EventType, UIEvent
from src.architecture.state_manager import PlaybackState, StateManager
from src.config.theme import DEFAULT_THEME
from src.ui.component import ArcadeComponent
from src.ui.utils import draw_rectangle_filled, draw_rectangle_outline, draw_text


class HelpLegendComponent(ArcadeComponent):
    """Reusable help/legend widget for displaying keyboard shortcuts."""

    def __init__(self, x: float = 20, y: float = 220, visible: bool = True):
        """Initialize help legend.
        
        Args:
            x, y: Position.
            visible: Initial visibility state.
        """
        self.x = x
        self.y = y
        self._visible = visible

        self.controls_text_offset = 180
        self._text = arcade.Text("", 0, 0, arcade.color.CYAN, 14)

    @property
    def visible(self) -> bool:
        """Get visibility state."""
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        """Set visibility state."""
        self._visible = value

    def toggle_visibility(self) -> bool:
        """Toggle visibility.
        
        Returns:
            New visibility state.
        """
        self._visible = not self._visible
        return self._visible

    def draw(self, renderer: Any) -> None:
        """Draw the help legend."""
        if not self._visible:
            return

        theme = DEFAULT_THEME

        # Draw help button/label
        line_y = self.y - self.controls_text_offset
        draw_rectangle_filled(self.x, line_y - 8, 120, 18, theme.colors.button_bg)
        draw_rectangle_outline(self.x, line_y - 8, 120, 18, theme.colors.border)
        draw_text(
            "Help (H)",
            self.x + 5,
            line_y,
            color=theme.colors.primary,
            font_size=12,
        )

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


class KeyBindingOverlay(ArcadeComponent):
    """Overlay showing keyboard shortcuts and controls."""

    def __init__(self, x: float = 20, y: float = 20):
        """Initialize key binding overlay.
        
        Args:
            x, y: Position.
        """
        self.x = x
        self.y = y
        self.visible = False

        self.keybindings: List[Tuple[str, str]] = [
            ("Space", "Play / Pause"),
            ("→ / ←", "Next / Previous Frame"),
            ("↑ / ↓", "Faster / Slower"),
            ("M", "Mute / Unmute"),
            ("H", "Help"),
            ("Q", "Quit"),
            ("Click Driver", "Select Driver"),
            ("Drag Timeline", "Seek Frame"),
        ]

    def draw(self, renderer: Any) -> None:
        """Draw the overlay."""
        if not self.visible:
            return

        theme = DEFAULT_THEME

        # Draw semi-transparent background
        arcade.draw_rectangle_filled(
            self.x + 200,
            self.y + 200,
            400,
            400,
            (40, 40, 40, 200),
        )
        draw_rectangle_outline(self.x + 10, self.y + 10, 380, 380, theme.colors.border)

        # Draw title
        draw_text(
            "CONTROLS",
            self.x + 30,
            self.y + 350,
            color=theme.colors.primary,
            font_size=16,
            bold=True,
        )

        # Draw keybindings
        y_offset = 320
        for key, action in self.keybindings:
            draw_text(f"{key}:", self.x + 30, self.y + y_offset, color=theme.colors.text_primary, font_size=12)
            draw_text(
                action, self.x + 120, self.y + y_offset, color=theme.colors.text_secondary, font_size=11
            )
            y_offset -= 25

    def toggle(self) -> bool:
        """Toggle overlay visibility.
        
        Returns:
            New visibility state.
        """
        self.visible = not self.visible
        return self.visible

    def on_resize(self, width: float, height: float) -> None:
        """Handle resize."""
        pass

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle input."""
        if event_type == "key_press" and kwargs.get("key") == "h":
            self.toggle()
            return True
        return False

    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        pass

    def on_event(self, event: UIEvent) -> None:
        """Handle events."""
        pass


class RaceControlsComponent(ArcadeComponent):
    """Playback controls (play/pause, speed, etc.)."""

    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        state_manager: StateManager,
        event_bus: EventBus,
    ):
        """Initialize race controls.
        
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

        self.button_area_play_pause = (x + 10, y + 10, 40, 40)
        self.button_area_next_frame = (x + 55, y + 10, 40, 40)
        self.button_area_prev_frame = (x + 100, y + 10, 40, 40)

        # Speed buttons
        self.speeds = [0.5, 1.0, 1.5, 2.0]
        self.speed_index = 1  # Default 1.0x

        self.help_legend = HelpLegendComponent(x, y + 50)

    def draw(self, renderer: Any) -> None:
        """Draw the controls."""
        theme = DEFAULT_THEME

        # Draw background
        draw_rectangle_filled(self.x, self.y, self.width, self.height, theme.colors.bg_dark)
        draw_rectangle_outline(self.x, self.y, self.width, self.height, theme.colors.border)

        # Play/Pause button
        paused = self.state.get_paused()
        button_text = "III" if paused else ">"
        draw_rectangle_filled(
            self.button_area_play_pause[0],
            self.button_area_play_pause[1],
            self.button_area_play_pause[2],
            self.button_area_play_pause[3],
            theme.colors.button_active if paused else theme.colors.button_hover,
        )
        draw_text(
            button_text,
            self.button_area_play_pause[0] + 12,
            self.button_area_play_pause[1] + 15,
            color=theme.colors.text_primary,
            font_size=14,
        )

        # Next frame button
        draw_rectangle_filled(
            self.button_area_next_frame[0],
            self.button_area_next_frame[1],
            self.button_area_next_frame[2],
            self.button_area_next_frame[3],
            theme.colors.button_bg,
        )
        draw_text(
            "»",
            self.button_area_next_frame[0] + 12,
            self.button_area_next_frame[1] + 10,
            color=theme.colors.text_primary,
            font_size=18,
        )

        # Previous frame button
        draw_rectangle_filled(
            self.button_area_prev_frame[0],
            self.button_area_prev_frame[1],
            self.button_area_prev_frame[2],
            self.button_area_prev_frame[3],
            theme.colors.button_bg,
        )
        draw_text(
            "«",
            self.button_area_prev_frame[0] + 12,
            self.button_area_prev_frame[1] + 10,
            color=theme.colors.text_primary,
            font_size=18,
        )

        # Speed indicator
        current_speed = self.state.get_playback_speed()
        draw_text(
            f"Speed: {current_speed:.1f}x",
            self.x + 150,
            self.y + 25,
            color=theme.colors.text_secondary,
            font_size=12,
        )

        # Draw help button
        self.help_legend.draw(renderer)

    def on_resize(self, width: float, height: float) -> None:
        """Handle resize."""
        self.width = width
        self.height = height

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle input."""
        if event_type == "mouse_press":
            x, y = kwargs.get("x", 0), kwargs.get("y", 0)

            # Check play/pause button
            if (
                self.button_area_play_pause[0] <= x <= self.button_area_play_pause[0] + 40
                and self.button_area_play_pause[1] <= y <= self.button_area_play_pause[1] + 40
            ):
                self.state.toggle_paused()
                return True

            # Check next frame button
            if (
                self.button_area_next_frame[0] <= x <= self.button_area_next_frame[0] + 40
                and self.button_area_next_frame[1] <= y <= self.button_area_next_frame[1] + 40
            ):
                self.state.set_frame(self.state.get_frame() + 1)
                return True

            # Check previous frame button
            if (
                self.button_area_prev_frame[0] <= x <= self.button_area_prev_frame[0] + 40
                and self.button_area_prev_frame[1] <= y <= self.button_area_prev_frame[1] + 40
            ):
                self.state.set_frame(max(0, self.state.get_frame() - 1))
                return True

        elif event_type == "key_press":
            key = kwargs.get("key", "")
            if key == "space":
                self.state.toggle_paused()
                return True
            elif key == "right":
                self.state.set_frame(self.state.get_frame() + 1)
                return True
            elif key == "left":
                self.state.set_frame(max(0, self.state.get_frame() - 1))
                return True

        return False

    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        pass

    def on_event(self, event: UIEvent) -> None:
        """Handle events."""
        pass
