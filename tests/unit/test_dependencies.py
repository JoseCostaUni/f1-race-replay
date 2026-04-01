"""Tests for dependency injection container.

Tests:
- Singleton registration and resolution
- Factory registration
- Dependency lookup
- Error handling
"""

import pytest
from src.architecture.dependencies import DIContainer, ServiceLocator


class TestDIContainer:
    """Test dependency injection container."""

    def setup_method(self):
        """Set up test fixtures."""
        self.container = DIContainer()

    def test_register_and_resolve_singleton(self):
        """Test registering and resolving singleton."""
        obj = {"name": "test"}
        self.container.register_singleton("test_obj", obj)

        resolved = self.container.resolve("test_obj")

        assert resolved is obj  # Same instance

    def test_register_and_resolve_factory(self):
        """Test registering and resolving factory."""
        counter = {"count": 0}

        def factory():
            counter["count"] += 1
            return {"id": counter["count"]}

        self.container.register_factory("test_obj", factory)

        obj1 = self.container.resolve("test_obj")
        obj2 = self.container.resolve("test_obj")

        assert obj1["id"] == 1
        assert obj2["id"] == 2  # Different instances

    def test_resolve_nonexistent_dependency(self):
        """Test resolving non-existent dependency raises error."""
        with pytest.raises(KeyError):
            self.container.resolve("nonexistent")

    def test_has_dependency(self):
        """Test checking if dependency exists."""
        self.container.register_singleton("test", {})

        assert self.container.has("test") == True
        assert self.container.has("nonexistent") == False

    def test_clear_dependencies(self):
        """Test clearing all dependencies."""
        self.container.register_singleton("test1", {})
        self.container.register_singleton("test2", {})

        self.container.clear()

        assert self.container.has("test1") == False
        assert self.container.has("test2") == False

    def test_factory_dependency_resolution(self):
        """Test factory that depends on other registered dependencies."""
        self.container.register_singleton("config", {"debug": True})

        def service_factory():
            config = self.container.resolve("config")
            return {"config": config}

        self.container.register_factory("service", service_factory)

        service = self.container.resolve("service")
        assert service["config"]["debug"] == True


class TestServiceLocator:
    """Test service locator pattern."""

    def setup_method(self):
        """Set up test fixtures."""
        self.container = DIContainer()
        self.locator = ServiceLocator(self.container)

    def test_service_locator_delegates_to_container(self):
        """Test that service locator delegates to container."""
        # Register mock services
        self.container.register_singleton("event_bus", {"type": "EventBus"})
        self.container.register_singleton("state", {"type": "StateManager"})

        event_bus = self.locator.get_event_bus()
        state = self.locator.get_state_manager()

        assert event_bus["type"] == "EventBus"
        assert state["type"] == "StateManager"

    def test_get_by_name(self):
        """Test resolving service by name."""
        self.container.register_singleton("custom_service", {"data": "test"})

        service = self.locator.get("custom_service")
        assert service["data"] == "test"


if __name__ == "__main__":
    pytest.main([__file__])
