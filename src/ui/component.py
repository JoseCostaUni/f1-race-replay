"""Base component classes for Arcade and PySide6 UI components.

Defines protocols and abstract base classes that unify component interfaces
across both Arcade (game-loop based) and PySide6 (event-driven) UI frameworks.

Components receive state via dependency injection and communicate via event bus,
not tight coupling to window objects.
"""

from abc import ABC, abstractmethod
from typing import Any, Protocol

from src.architecture.event_bus import UIEvent
from src.architecture.state_manager import PlaybackState


class Component(ABC):
    """Base protocol for all UI components.

    Defines the common interface that all components must implement,
    regardless of whether they're Arcade or PySide6 based.
    """

    @abstractmethod
    def on_state_change(self, state: PlaybackState) -> None:
        """Handle state change notification.

        Called when playback state changes (frame, speed, driver, etc.).
        Components update their internal state and schedule redraw.

        Args:
            state: New PlaybackState.
        """
        pass

    @abstractmethod
    def on_event(self, event: UIEvent) -> None:
        """Handle custom event notification.

        Called when event bus emits an event this component subscribed to.

        Args:
            event: UIEvent with event_type and data.
        """
        pass


class ArcadeComponent(Component):
    """Base class for Arcade-based (drawing) components.

    Arcade components are responsible for:
    - Drawing visual elements to the window
    - Handling mouse/keyboard input
    - Responding to state changes by updating internal state
    - Handling window resize events

    Example:
        >>> class LeaderboardComponent(ArcadeComponent):
        ...     def draw(self, renderer):
        ...         for driver in self.drivers:
        ...             draw_text(...)
    """

    @abstractmethod
    def draw(self, renderer: Any) -> None:
        """Draw the component to the screen.

        Args:
            renderer: Rendering context (Arcade window or custom renderer).
        """
        pass

    @abstractmethod
    def on_resize(self, width: float, height: float) -> None:
        """Handle window resize.

        Called when parent window is resized. Component should recalculate
        layout based on new dimensions.

        Args:
            width: New window width.
            height: New window height.
        """
        pass

    @abstractmethod
    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle mouse/keyboard input.

        Args:
            event_type: Type of input event ("mouse_press", "key_press", etc.)
            **kwargs: Event-specific data (x, y, button, key, modifiers, etc.)

        Returns:
            True if event was consumed (should not propagate), False otherwise.
        """
        pass


class QtComponent(Component):
    """Base class for PySide6/PyQt-based UI components.

    Qt components are responsible for:
    - Building UI via layout managers and widgets
    - Connecting signals/slots
    - Responding to state changes by updating widgets
    - Managing dialogs and interactions

    Example:
        >>> class SettingsDialog(QtComponent):
        ...     def setup_ui(self):
        ...         self.layout = QVBoxLayout()
        ...         self.layout.addWidget(QLabel("Settings"))
    """

    @abstractmethod
    def setup_ui(self) -> None:
        """Build and configure UI widgets.

        Called once during initialization. Subclasses should create all
        widgets, layouts, and connections here.
        """
        pass

    @abstractmethod
    def connect_signals(self) -> None:
        """Connect signals to slots.

        Called after setup_ui(). Subclasses should connect all widget
        signals to slot methods here.
        """
        pass

    @abstractmethod
    def update_ui_state(self) -> None:
        """Update UI to reflect current state.

        Called when state changes or needs sync with internal state.
        Subclasses should update widget values, enabled states, colors, etc.
        """
        pass


class ComponentRegistry:
    """Registry of component instances for easy lookup and management.

    Used by windows to manage multiple components and broadcast events to
    interested components.

    Example:
        >>> registry = ComponentRegistry()
        >>> registry.register("leaderboard", leaderboard_comp)
        >>> registry.register("controls", controls_comp)
        >>> registry.broadcast_state_change(new_state)
    """

    def __init__(self):
        """Initialize component registry."""
        self._components: dict[str, Component] = {}

    def register(self, name: str, component: Component) -> None:
        """Register a component.

        Args:
            name: Unique component name.
            component: Component instance.
        """
        self._components[name] = component

    def get(self, name: str) -> Component | None:
        """Get a registered component.

        Args:
            name: Component name.

        Returns:
            Component instance or None if not found.
        """
        return self._components.get(name)

    def get_all(self) -> dict[str, Component]:
        """Get all registered components.

        Returns:
            Dictionary of all components.
        """
        return self._components.copy()

    def unregister(self, name: str) -> None:
        """Unregister a component.

        Args:
            name: Component name.
        """
        self._components.pop(name, None)

    def broadcast_state_change(self, state: PlaybackState) -> None:
        """Broadcast state change to all components.

        Args:
            state: New PlaybackState.
        """
        for component in self._components.values():
            try:
                component.on_state_change(state)
            except Exception as e:
                print(f"Error in component state change: {e}")

    def broadcast_event(self, event: UIEvent) -> None:
        """Broadcast event to all components.

        Args:
            event: UIEvent to broadcast.
        """
        for component in self._components.values():
            try:
                component.on_event(event)
            except Exception as e:
                print(f"Error in component event handler: {e}")

    def clear(self) -> None:
        """Clear all registered components."""
        self._components.clear()
