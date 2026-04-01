"""Tests for event bus system.

Tests:
- Event subscription and emission
- Multiple subscribers for same event
- Event data payload
- Unsubscribe functionality
"""

import pytest
from src.architecture.event_bus import EventBus, EventType, UIEvent


class TestEventBus:
    """Test EventBus pub/sub system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.bus = EventBus()
        self.received_events = []

    def _capture_event(self, event: UIEvent):
        """Callback to capture received events."""
        self.received_events.append(event)

    def test_subscribe_and_emit(self):
        """Test basic subscription and emission."""
        self.bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._capture_event)
        self.bus.emit(EventType.FRAME_INDEX_CHANGED, 42)

        assert len(self.received_events) == 1
        assert self.received_events[0].data == 42

    def test_multiple_subscribers(self):
        """Test multiple subscribers for same event."""
        received1 = []
        received2 = []

        self.bus.subscribe(EventType.FRAME_INDEX_CHANGED, lambda e: received1.append(e))
        self.bus.subscribe(EventType.FRAME_INDEX_CHANGED, lambda e: received2.append(e))

        self.bus.emit(EventType.FRAME_INDEX_CHANGED, 10)

        assert len(received1) == 1
        assert len(received2) == 1

    def test_unsubscribe(self):
        """Test unsubscribe functionality."""
        unsub = self.bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._capture_event)

        self.bus.emit(EventType.FRAME_INDEX_CHANGED, 10)
        unsub()
        self.bus.emit(EventType.FRAME_INDEX_CHANGED, 20)

        # Should only have first event
        assert len(self.received_events) == 1
        assert self.received_events[0].data == 10

    def test_no_subscribers(self):
        """Test emit with no subscribers doesn't crash."""
        self.bus.emit(EventType.FRAME_INDEX_CHANGED, 42)
        assert len(self.received_events) == 0

    def test_event_data_payload(self):
        """Test events with complex data payloads."""
        complex_data = {"frame": 42, "drivers": [1, 2, 3]}
        self.bus.subscribe(EventType.DATA_LOADED, self._capture_event)
        self.bus.emit(EventType.DATA_LOADED, complex_data)

        assert self.received_events[0].data == complex_data

    def test_subscriber_count(self):
        """Test subscriber count method."""
        assert self.bus.subscriber_count(EventType.FRAME_INDEX_CHANGED) == 0

        self.bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._capture_event)
        assert self.bus.subscriber_count(EventType.FRAME_INDEX_CHANGED) == 1

        self.bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._capture_event)
        assert self.bus.subscriber_count(EventType.FRAME_INDEX_CHANGED) == 2

    def test_clear_event_type(self):
        """Test clearing subscribers for specific event type."""
        self.bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._capture_event)
        self.bus.subscribe(EventType.DRIVER_SELECTED, self._capture_event)

        self.bus.clear(EventType.FRAME_INDEX_CHANGED)

        assert self.bus.subscriber_count(EventType.FRAME_INDEX_CHANGED) == 0
        assert self.bus.subscriber_count(EventType.DRIVER_SELECTED) == 1

    def test_clear_all(self):
        """Test clearing all subscribers."""
        self.bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._capture_event)
        self.bus.subscribe(EventType.DRIVER_SELECTED, self._capture_event)

        self.bus.clear()

        assert self.bus.subscriber_count(EventType.FRAME_INDEX_CHANGED) == 0
        assert self.bus.subscriber_count(EventType.DRIVER_SELECTED) == 0


if __name__ == "__main__":
    pytest.main([__file__])
