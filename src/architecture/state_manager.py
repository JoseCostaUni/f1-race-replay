"""Centralized state management for F1 Race Replay.

Manages all playback state (frame index, paused, speed, selected driver) and emits
events when state changes. Components read state via this manager, never directly
access window objects.
"""

from dataclasses import dataclass, field
from typing import Any, Dict

from src.architecture.event_bus import EventBus, EventType


@dataclass
class PlaybackState:
    """Immutable representation of playback state."""

    current_frame: int = 0
    paused: bool = False
    playback_speed: float = 1.0
    selected_driver_number: int | None = None
    selected_lap: int | None = None
    settings: Dict[str, Any] = field(default_factory=dict)

    def copy(self, **kwargs) -> "PlaybackState":
        """Create a copy with updated values.

        Args:
            **kwargs: Fields to update.

        Returns:
            New PlaybackState with updated values.
        """
        current_dict = {
            "current_frame": self.current_frame,
            "paused": self.paused,
            "playback_speed": self.playback_speed,
            "selected_driver_number": self.selected_driver_number,
            "selected_lap": self.selected_lap,
            "settings": self.settings.copy(),
        }
        current_dict.update(kwargs)
        return PlaybackState(**current_dict)


class StateManager:
    """Centralized state management with event notification.

    Manages playback state and emits events when state changes. Components should
    subscribe to events rather than polling state.

    Example:
        >>> manager = StateManager(event_bus)
        >>> manager.set_frame(42)
        >>> # Event automatically emitted:
        >>> # EventType.FRAME_INDEX_CHANGED with data=42
    """

    def __init__(self, event_bus: EventBus):
        """Initialize state manager.

        Args:
            event_bus: EventBus instance for emitting state change events.
        """
        self._state = PlaybackState()
        self._event_bus = event_bus

    # Getters (components use these to read state)

    def get_state(self) -> PlaybackState:
        """Get current state snapshot.

        Returns:
            Current PlaybackState.
        """
        return self._state

    def get_frame(self) -> int:
        """Get current frame index.

        Returns:
            Current frame number.
        """
        return self._state.current_frame

    def get_paused(self) -> bool:
        """Get paused state.

        Returns:
            True if playback is paused, False if playing.
        """
        return self._state.paused

    def get_playback_speed(self) -> float:
        """Get playback speed multiplier.

        Returns:
            Speed multiplier (1.0 = normal, 2.0 = 2x, 0.5 = half speed).
        """
        return self._state.playback_speed

    def get_selected_driver(self) -> int | None:
        """Get selected driver number.

        Returns:
            Driver number (1-20) or None if no driver selected.
        """
        return self._state.selected_driver_number

    def get_selected_lap(self) -> int | None:
        """Get selected lap number.

        Returns:
            Lap number or None if no lap selected.
        """
        return self._state.selected_lap

    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value.

        Args:
            key: Setting key.
            default: Default value if not found.

        Returns:
            Setting value or default.
        """
        return self._state.settings.get(key, default)

    # Setters (trigger state changes and emit events)

    def set_frame(self, frame: int) -> None:
        """Set current frame index.

        Args:
            frame: New frame index.

        Emits:
            EventType.FRAME_INDEX_CHANGED with data=frame
        """
        if self._state.current_frame != frame:
            self._state = self._state.copy(current_frame=frame)
            self._event_bus.emit(EventType.FRAME_INDEX_CHANGED, frame)

    def set_paused(self, paused: bool) -> None:
        """Set paused state.

        Args:
            paused: True to pause, False to resume.

        Emits:
            EventType.PAUSED_TOGGLED with data=paused
        """
        if self._state.paused != paused:
            self._state = self._state.copy(paused=paused)
            self._event_bus.emit(EventType.PAUSED_TOGGLED, paused)

    def toggle_paused(self) -> bool:
        """Toggle paused state.

        Returns:
            New paused state.

        Emits:
            EventType.PAUSED_TOGGLED
        """
        new_paused = not self._state.paused
        self.set_paused(new_paused)
        return new_paused

    def set_playback_speed(self, speed: float) -> None:
        """Set playback speed multiplier.

        Args:
            speed: Speed multiplier (must be > 0).

        Emits:
            EventType.PLAYBACK_SPEED_CHANGED with data=speed
        """
        if speed <= 0:
            raise ValueError(f"Playback speed must be > 0, got {speed}")

        if self._state.playback_speed != speed:
            self._state = self._state.copy(playback_speed=speed)
            self._event_bus.emit(EventType.PLAYBACK_SPEED_CHANGED, speed)

    def select_driver(self, driver_number: int | None) -> None:
        """Select a driver.

        Args:
            driver_number: Driver number (1-20) or None to deselect.

        Emits:
            EventType.DRIVER_SELECTED with data=driver_number
        """
        if self._state.selected_driver_number != driver_number:
            self._state = self._state.copy(selected_driver_number=driver_number)
            self._event_bus.emit(EventType.DRIVER_SELECTED, driver_number)

    def select_lap(self, lap_number: int | None) -> None:
        """Select a lap.

        Args:
            lap_number: Lap number or None to deselect.

        Emits:
            EventType.LAP_SELECTED with data=lap_number
        """
        if self._state.selected_lap != lap_number:
            self._state = self._state.copy(selected_lap=lap_number)
            self._event_bus.emit(EventType.LAP_SELECTED, lap_number)

    def set_setting(self, key: str, value: Any) -> None:
        """Set a setting value.

        Args:
            key: Setting key.
            value: Setting value.

        Emits:
            EventType.SETTINGS_UPDATED with data={'key': key, 'value': value}
        """
        if self._state.settings.get(key) != value:
            new_settings = self._state.settings.copy()
            new_settings[key] = value
            self._state = self._state.copy(settings=new_settings)
            self._event_bus.emit(EventType.SETTINGS_UPDATED, {"key": key, "value": value})

    def reset(self) -> None:
        """Reset state to defaults.

        Emits:
            EventType.PLAYBACK_STATE_CHANGED with new state
        """
        self._state = PlaybackState()
        self._event_bus.emit(EventType.PLAYBACK_STATE_CHANGED, self._state)
