"""Tests for state management system.

Tests:
- State getter/setter functionality
- Event emission on state change
- State immutability (copy on write)
- Multiple state updates
"""

import pytest
from src.architecture.event_bus import EventBus, EventType, reset_event_bus
from src.architecture.state_manager import StateManager, PlaybackState


class TestStateManager:
    """Test StateManager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_event_bus()
        self.event_bus = EventBus()
        self.state_manager = StateManager(self.event_bus)
        self.received_events = []

    def _capture_event(self, event):
        """Capture events for testing."""
        self.received_events.append(event)

    def test_get_state(self):
        """Test retrieving current state."""
        state = self.state_manager.get_state()
        assert state.current_frame == 0
        assert state.paused == False
        assert state.playback_speed == 1.0

    def test_set_frame(self):
        """Test setting frame index."""
        self.event_bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._capture_event)

        self.state_manager.set_frame(42)

        assert self.state_manager.get_frame() == 42
        assert len(self.received_events) == 1
        assert self.received_events[0].data == 42

    def test_set_frame_no_change_no_event(self):
        """Test that setting same frame doesn't emit event."""
        self.event_bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._capture_event)

        self.state_manager.set_frame(10)
        self.state_manager.set_frame(10)  # Same value

        assert len(self.received_events) == 1  # Only emitted once

    def test_toggle_paused(self):
        """Test toggling paused state."""
        self.event_bus.subscribe(EventType.PAUSED_TOGGLED, self._capture_event)

        result = self.state_manager.toggle_paused()

        assert result == True
        assert self.state_manager.get_paused() == True
        assert self.received_events[0].data == True

    def test_set_playback_speed(self):
        """Test setting playback speed."""
        self.event_bus.subscribe(EventType.PLAYBACK_SPEED_CHANGED, self._capture_event)

        self.state_manager.set_playback_speed(2.0)

        assert self.state_manager.get_playback_speed() == 2.0
        assert self.received_events[0].data == 2.0

    def test_set_invalid_speed(self):
        """Test that invalid speed raises error."""
        with pytest.raises(ValueError):
            self.state_manager.set_playback_speed(0)

        with pytest.raises(ValueError):
            self.state_manager.set_playback_speed(-1)

    def test_select_driver(self):
        """Test driver selection."""
        self.event_bus.subscribe(EventType.DRIVER_SELECTED, self._capture_event)

        self.state_manager.select_driver(3)

        assert self.state_manager.get_selected_driver() == 3
        assert self.received_events[0].data == 3

    def test_deselect_driver(self):
        """Test deselecting driver."""
        self.event_bus.subscribe(EventType.DRIVER_SELECTED, self._capture_event)

        self.state_manager.select_driver(3)
        self.received_events.clear()

        self.state_manager.select_driver(None)

        assert self.state_manager.get_selected_driver() is None
        assert self.received_events[0].data is None

    def test_set_setting(self):
        """Test setting and getting settings."""
        self.event_bus.subscribe(EventType.SETTINGS_UPDATED, self._capture_event)

        self.state_manager.set_setting("theme", "dark")

        assert self.state_manager.get_setting("theme") == "dark"
        assert self.received_events[0].data["key"] == "theme"

    def test_reset_state(self):
        """Test resetting to default state."""
        self.state_manager.set_frame(100)
        self.state_manager.set_paused(True)

        self.state_manager.reset()

        assert self.state_manager.get_frame() == 0
        assert self.state_manager.get_paused() == False

    def test_state_immutability(self):
        """Test that state is immutable (copy on write)."""
        state1 = self.state_manager.get_state()
        self.state_manager.set_frame(42)
        state2 = self.state_manager.get_state()

        # Different states
        assert state1.current_frame == 0
        assert state2.current_frame == 42


if __name__ == "__main__":
    pytest.main([__file__])
