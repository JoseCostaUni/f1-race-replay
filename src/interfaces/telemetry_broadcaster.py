"""Telemetry broadcaster for streaming race data to secondary windows.

Extracts telemetry broadcasting logic from the main race window.
Listens to state changes and broadcasts telemetry data to clients over TCP.
"""

import json
from typing import Any, Dict, Optional

from src.architecture.event_bus import EventBus, EventType, UIEvent
from src.architecture.state_manager import PlaybackState, StateManager


class TelemetryBroadcaster:
    """Broadcasts telemetry data to secondary windows.
    
    Decouples telemetry streaming from race window logic.
    Listens to state change events and broadcasts current telemetry to all
    connected clients.
    
    In a real implementation, this would:
    - Maintain TCP socket connections to clients
    - Serialize state/telemetry to JSON
    - Send data on state changes
    """

    def __init__(self, state_manager: StateManager, event_bus: EventBus, port: int = 9999):
        """Initialize broadcaster.
        
        Args:
            state_manager: State manager to broadcast from.
            event_bus: Event bus to subscribe to state changes.
            port: Port to broadcast on (default TCP 9999).
        """
        self.state = state_manager
        self.event_bus = event_bus
        self.port = port

        self.clients: Dict[str, Any] = {}  # Connected clients
        self.last_telemetry: Optional[Dict[str, Any]] = None

        # Subscribe to state changes
        self.event_bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._on_frame_changed)
        self.event_bus.subscribe(EventType.DRIVER_SELECTED, self._on_driver_selected)
        self.event_bus.subscribe(EventType.PLAYBACK_STATE_CHANGED, self._on_state_changed)

    def _on_frame_changed(self, event: UIEvent) -> None:
        """Handle frame change event."""
        self._broadcast_telemetry()

    def _on_driver_selected(self, event: UIEvent) -> None:
        """Handle driver selection event."""
        self._broadcast_telemetry()

    def _on_state_changed(self, event: UIEvent) -> None:
        """Handle state change event."""
        self._broadcast_telemetry()

    def _broadcast_telemetry(self) -> None:
        """Broadcast current telemetry to all connected clients.
        
        In a real implementation, this would:
        1. Gather telemetry data from data providers based on current frame
        2. Serialize to JSON
        3. Send to all connected clients over TCP
        """
        telemetry = self._gather_telemetry()
        self.last_telemetry = telemetry

        # Would send to clients here
        # for client in self.clients.values():
        #     client.send(json.dumps(telemetry))

    def _gather_telemetry(self) -> Dict[str, Any]:
        """Gather current telemetry data.
        
        Returns:
            Dict with current state and telemetry.
        """
        state = self.state.get_state()

        return {
            "frame": state.current_frame,
            "paused": state.paused,
            "speed": state.playback_speed,
            "selected_driver": state.selected_driver_number,
            "timestamp": None,  # Would be set by data provider
        }

    def start_server(self) -> None:
        """Start the telemetry server.
        
        In a real implementation, this would:
        - Bind to TCP port
        - Listen for client connections
        - Accept and register new clients
        """
        pass

    def stop_server(self) -> None:
        """Stop the telemetry server."""
        self.clients.clear()

    def register_client(self, client_id: str, client: Any) -> None:
        """Register a connected client.
        
        Args:
            client_id: Unique client identifier.
            client: Client connection object.
        """
        self.clients[client_id] = client

    def unregister_client(self, client_id: str) -> None:
        """Unregister a disconnected client.
        
        Args:
            client_id: Client identifier.
        """
        self.clients.pop(client_id, None)
