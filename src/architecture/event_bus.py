"""Event bus system for decoupled component communication.

Implements a lightweight pub/sub event system that allows components to communicate
without direct coupling. Events are identified by name and can carry arbitrary data.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List


@dataclass
class UIEvent:
    """Base class for all UI events."""

    event_type: str
    data: Any = None


# Pre-defined event types
class EventType:
    """Standard event types used throughout the application."""

    # Playback events
    PLAYBACK_STATE_CHANGED = "playback_state_changed"
    FRAME_INDEX_CHANGED = "frame_index_changed"
    PLAYBACK_SPEED_CHANGED = "playback_speed_changed"
    PAUSED_TOGGLED = "paused_toggled"

    # Selection events
    DRIVER_SELECTED = "driver_selected"
    LAP_SELECTED = "lap_selected"

    # Settings events
    SETTINGS_UPDATED = "settings_updated"
    THEME_CHANGED = "theme_changed"

    # Window events
    WINDOW_RESIZED = "window_resized"
    WINDOW_CLOSED = "window_closed"

    # Data events
    DATA_LOADED = "data_loaded"
    DATA_UPDATED = "data_updated"
    DATA_ERROR = "data_error"

    # Telemetry events
    TELEMETRY_RECEIVED = "telemetry_received"
    CONNECTION_STATUS_CHANGED = "connection_status_changed"


class EventCallback:
    """Type alias for event callback functions."""

    pass


class EventBus:
    """Lightweight pub/sub event bus for component communication.

    Features:
    - Type-safe event subscriptions
    - Multiple subscribers per event
    - Event data payload support
    - Async-ready (though currently synchronous)
    - Memory efficient (no retained event history)
    """

    def __init__(self):
        """Initialize the event bus."""
        self._subscribers: Dict[str, List[Callable[[UIEvent], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[UIEvent], None]) -> Callable[[], None]:
        """Subscribe to an event type.

        Args:
            event_type: Event type to subscribe to (use EventType constants).
            callback: Function to call when event is emitted. Receives UIEvent.

        Returns:
            Unsubscribe function (call to remove subscription).

        Example:
            >>> bus = EventBus()
            >>> def on_frame_changed(event):
            ...     print(f"Frame: {event.data}")
            >>> unsub = bus.subscribe(EventType.FRAME_INDEX_CHANGED, on_frame_changed)
            >>> bus.emit(EventType.FRAME_INDEX_CHANGED, 42)
            >>> unsub()  # Stop listening
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        self._subscribers[event_type].append(callback)

        # Return unsubscribe function
        def unsubscribe():
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                pass

        return unsubscribe

    def emit(self, event_type: str, data: Any = None) -> None:
        """Emit an event to all subscribers.

        Args:
            event_type: Event type to emit.
            data: Event data payload (optional).
        """
        if event_type not in self._subscribers:
            return

        event = UIEvent(event_type=event_type, data=data)
        for callback in self._subscribers[event_type]:
            try:
                callback(event)
            except Exception as e:
                # Log error but continue processing other subscribers
                print(f"Error in event callback for {event_type}: {e}")

    def clear(self, event_type: str | None = None) -> None:
        """Clear subscribers.

        Args:
            event_type: Specific event type to clear. If None, clears all.
        """
        if event_type:
            self._subscribers[event_type] = []
        else:
            self._subscribers.clear()

    def subscriber_count(self, event_type: str) -> int:
        """Get number of subscribers for an event type.

        Args:
            event_type: Event type to check.

        Returns:
            Number of subscribers.
        """
        return len(self._subscribers.get(event_type, []))

    def has_subscribers(self, event_type: str) -> bool:
        """Check if event type has any subscribers.

        Args:
            event_type: Event type to check.

        Returns:
            True if event has subscribers, False otherwise.
        """
        return self.subscriber_count(event_type) > 0


# Global event bus instance (shared across application)
_global_event_bus: EventBus | None = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance (singleton pattern).

    Returns:
        The global EventBus instance.
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus


def reset_event_bus() -> None:
    """Reset the global event bus (mainly for testing).

    Clears all subscribers.
    """
    bus = get_event_bus()
    bus.clear()
