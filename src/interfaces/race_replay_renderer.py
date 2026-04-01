"""Renderer for race replay window.

Coordinates all component rendering in a testable, decoupled manner.
The window passes state/components to the renderer; the renderer just draws.
"""

from typing import Any, Dict, List

from src.architecture.state_manager import PlaybackState
from src.ui.component import ArcadeComponent, ComponentRegistry


class RaceReplayRenderer:
    """Coordinates rendering of all race replay components.
    
    Decouples rendering logic from window management. A window passes:
    - Rendering context (arcade window or canvas)
    - Current state (frame, paused, etc.)
    - Component registry
    
    The renderer handles drawing components in the right order, with proper
    layering and coordinate calculations.
    """

    def __init__(self, component_registry: ComponentRegistry):
        """Initialize renderer.
        
        Args:
            component_registry: Registry containing all UI components.
        """
        self.components = component_registry
        self.render_order: List[str] = [
            # Draw in this order: backgrounds first, overlays last
            "session_info",
            "weather",
            "driver_info",
            "progress_bar",
            "leaderboard",
            "controls",
            "legend",
            "overlay",
        ]

    def render(self, renderer: Any, state: PlaybackState, window_width: float, window_height: float) -> None:
        """Render all components to screen.
        
        Args:
            renderer: Rendering context (Arcade window object).
            state: Current playback state.
            window_width: Window width in pixels.
            window_height: Window height in pixels.
        """
        # Update all components with current state
        self.components.broadcast_state_change(state)

        # Draw components in order
        for component_name in self.render_order:
            component = self.components.get(component_name)
            if component:
                try:
                    # Handle window resize
                    component.on_resize(window_width, window_height)

                    # Draw component
                    component.draw(renderer)
                except Exception as e:
                    print(f"Error rendering {component_name}: {e}")

    def broadcast_input(self, event_type: str, **kwargs) -> bool:
        """Broadcast input event to components.
        
        Components are tried in reverse order (overlays get priority).
        
        Args:
            event_type: Type of input event.
            **kwargs: Event-specific data.
            
        Returns:
            True if event was consumed, False otherwise.
        """
        # Try components in reverse render order (overlays first)
        for component_name in reversed(self.render_order):
            component = self.components.get(component_name)
            if component:
                try:
                    if component.handle_input(event_type, **kwargs):
                        return True  # Event consumed
                except Exception as e:
                    print(f"Error handling input in {component_name}: {e}")

        return False
