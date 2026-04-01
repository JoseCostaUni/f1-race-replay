"""Integration tests for architecture components working together.

Tests:
- Event bus + state manager integration
- Component registry with state changes
- Full playback flow simulation
"""

import pytest
from src.architecture.event_bus import EventBus, EventType, reset_event_bus
from src.architecture.state_manager import StateManager, PlaybackState
from src.ui.component import ComponentRegistry, ArcadeComponent
from src.ui.layout import LayoutHelper, Anchor, Bounds


class MockComponent(ArcadeComponent):
    """Mock component for testing."""

    def __init__(self, name: str):
        """Initialize mock component."""
        self.name = name
        self.state_changes = []
        self.events_received = []

    def draw(self, renderer):
        """Mock draw."""
        pass

    def on_resize(self, width: float, height: float):
        """Mock resize."""
        pass

    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Mock input."""
        return False

    def on_state_change(self, state: PlaybackState):
        """Capture state changes."""
        self.state_changes.append(state)

    def on_event(self, event):
        """Capture events."""
        self.events_received.append(event)


class TestComponentRegistry:
    """Test component registry with state management."""

    def setup_method(self):
        """Set up test fixtures."""
        reset_event_bus()
        self.event_bus = EventBus()
        self.state_manager = StateManager(self.event_bus)
        self.registry = ComponentRegistry()

    def test_register_and_get_component(self):
        """Test registering and retrieving components."""
        component = MockComponent("test")
        self.registry.register("test_component", component)

        retrieved = self.registry.get("test_component")
        assert retrieved is component

    def test_broadcast_state_change(self):
        """Test broadcasting state changes to all components."""
        comp1 = MockComponent("comp1")
        comp2 = MockComponent("comp2")

        self.registry.register("comp1", comp1)
        self.registry.register("comp2", comp2)

        new_state = PlaybackState(current_frame=42)
        self.registry.broadcast_state_change(new_state)

        assert len(comp1.state_changes) == 1
        assert comp1.state_changes[0].current_frame == 42
        assert len(comp2.state_changes) == 1

    def test_state_manager_and_registry_integration(self):
        """Test state manager emitting events that components receive."""
        component = MockComponent("test")
        self.registry.register("test", component)

        # Connect component to event bus
        def forward_event(event):
            component.on_event(event)

        self.event_bus.subscribe(EventType.FRAME_INDEX_CHANGED, forward_event)

        # Change state
        self.state_manager.set_frame(100)

        # Component should have received event
        assert len(component.events_received) == 1
        assert component.events_received[0].data == 100


class TestLayoutHelper:
    """Test layout calculation helpers."""

    def test_anchor_component_top_left(self):
        """Test top-left anchor."""
        bounds = LayoutHelper.anchor_component(
            window_width=800,
            window_height=600,
            component_width=100,
            component_height=50,
            anchor=Anchor.TOP_LEFT,
            margin_left=10,
            margin_top=10,
        )

        assert bounds.x == 10
        assert bounds.y == 600 - 50 - 10

    def test_anchor_component_top_right(self):
        """Test top-right anchor."""
        bounds = LayoutHelper.anchor_component(
            window_width=800,
            window_height=600,
            component_width=100,
            component_height=50,
            anchor=Anchor.TOP_RIGHT,
            margin_right=10,
            margin_top=10,
        )

        assert bounds.x == 800 - 100 - 10
        assert bounds.y == 600 - 50 - 10

    def test_anchor_component_center(self):
        """Test center anchor."""
        bounds = LayoutHelper.anchor_component(
            window_width=800,
            window_height=600,
            component_width=100,
            component_height=50,
            anchor=Anchor.CENTER,
        )

        assert bounds.x == (800 - 100) / 2
        assert bounds.y == (600 - 50) / 2

    def test_grid_layout(self):
        """Test grid layout calculation."""
        grid = LayoutHelper.grid_layout(
            window_width=800,
            window_height=600,
            cols=2,
            rows=2,
            margin=10,
            gap=5,
        )

        assert len(grid) == 2  # 2 rows
        assert len(grid[0]) == 2  # 2 cols

        # Check first cell positioning
        first_cell = grid[0][0]
        assert first_cell.x == 10

    def test_flex_layout(self):
        """Test flex layout (row)."""
        rects = LayoutHelper.flex_layout(
            window_width=800,
            window_height=600,
            count=4,
            direction="row",
            margin=10,
            gap=5,
        )

        assert len(rects) == 4

        # Check all same height
        for rect in rects:
            assert rect.height == 600 - 20

    def test_bounds_contains_point(self):
        """Test point-in-bounds check."""
        bounds = Bounds(x=100, y=100, width=50, height=50)

        assert bounds.contains_point(125, 125) == True
        assert bounds.contains_point(100, 100) == True
        assert bounds.contains_point(150, 150) == True
        assert bounds.contains_point(99, 99) == False
        assert bounds.contains_point(151, 151) == False


if __name__ == "__main__":
    pytest.main([__file__])
