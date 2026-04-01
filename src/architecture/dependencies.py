"""Dependency injection container for F1 Race Replay.

Implements a simple IoC (Inversion of Control) container that manages component
creation and dependency resolution. Components receive only what they need, not
the entire window object.

Example:
    >>> container = DIContainer()
    >>> container.register("state", StateManager(event_bus))
    >>> state = container.resolve("state")
"""

from typing import Any, Callable, Dict, Generic, TypeVar, Union

T = TypeVar("T")


class DIContainer:
    """Simple dependency injection container.

    Supports:
    - Singleton registration (same instance returned each time)
    - Factory registration (new instance created each time)
    - Lazy initialization (dependencies created on-demand)
    """

    def __init__(self):
        """Initialize the container."""
        self._singletons: Dict[str, Any] = {}
        self._factories: Dict[str, Callable[[], Any]] = {}

    def register_singleton(self, name: str, instance: Any) -> None:
        """Register a singleton instance.

        Args:
            name: Dependency name.
            instance: Instance to register (will be reused).

        Example:
            >>> event_bus = EventBus()
            >>> container.register_singleton("event_bus", event_bus)
        """
        self._singletons[name] = instance

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """Register a factory function.

        Creates a new instance each time the dependency is resolved.

        Args:
            name: Dependency name.
            factory: Callable that creates the dependency.

        Example:
            >>> container.register_factory("state", 
            ...     lambda: StateManager(container.resolve("event_bus")))
        """
        self._factories[name] = factory

    def resolve(self, name: str) -> Any:
        """Resolve a dependency.

        Args:
            name: Dependency name to resolve.

        Returns:
            The resolved dependency instance.

        Raises:
            KeyError: If dependency is not registered.
        """
        if name in self._singletons:
            return self._singletons[name]

        if name in self._factories:
            return self._factories[name]()

        raise KeyError(f"Dependency '{name}' not registered")

    def has(self, name: str) -> bool:
        """Check if a dependency is registered.

        Args:
            name: Dependency name.

        Returns:
            True if dependency is registered.
        """
        return name in self._singletons or name in self._factories

    def clear(self) -> None:
        """Clear all registered dependencies."""
        self._singletons.clear()
        self._factories.clear()


# Global container instance
_global_container: DIContainer | None = None


def get_container() -> DIContainer:
    """Get the global dependency injection container (singleton).

    Returns:
        The global DIContainer instance.
    """
    global _global_container
    if _global_container is None:
        _global_container = DIContainer()
    return _global_container


class ServiceLocator:
    """Service locator pattern wrapper for easier dependency access.

    Useful for components that need multiple dependencies.

    Example:
        >>> locator = ServiceLocator(container)
        >>> state = locator.get_state_manager()
        >>> event_bus = locator.get_event_bus()
    """

    def __init__(self, container: DIContainer):
        """Initialize locator.

        Args:
            container: DIContainer instance.
        """
        self._container = container

    def get_event_bus(self):
        """Get event bus.

        Returns:
            EventBus instance.
        """
        return self._container.resolve("event_bus")

    def get_state_manager(self):
        """Get state manager.

        Returns:
            StateManager instance.
        """
        return self._container.resolve("state")

    def get_theme(self):
        """Get theme.

        Returns:
            Theme instance.
        """
        return self._container.resolve("theme")

    def get_settings(self):
        """Get settings.

        Returns:
            Settings instance.
        """
        return self._container.resolve("settings")

    def get(self, name: str):
        """Get a dependency by name.

        Args:
            name: Dependency name.

        Returns:
            The dependency instance.
        """
        return self._container.resolve(name)
