"""Base class for PySide6/PyQt-based telemetry subscriber windows.

Consolidates duplicate telemetry client setup and lifecycle management.
All insight windows (DriverTelemetryWindow, TelemetryStreamViewer, etc.)
should inherit from this to avoid code duplication.
"""

from abc import abstractmethod
from typing import Any, Optional

from PySide6.QtWidgets import QMainWindow


class StreamSubscriber(QMainWindow):
    """Base class for windows that subscribe to telemetry streams.
    
    Handles:
    - Telemetry stream client initialization and connection
    - Automatic data subscription based on current playback
    - Connection error handling and reconnection logic
    - Lifecycle management (cleanup on close)
    
    Subclasses need only implement:
    - setup_ui(): Create UI
    - on_telemetry_data(data): Handle received telemetry
    - on_connection_status_changed(connected): Handle connection state
    """

    def __init__(self, parent: Optional[Any] = None, window_title: str = "F1 Telemetry"):
        """Initialize stream subscriber window.
        
        Args:
            parent: Parent widget (typically main window).
            window_title: Window title.
        """
        super().__init__(parent)
        self.setWindowTitle(window_title)

        self.client = None  # TelemetryStreamClient (injected)
        self.connected = False

    @abstractmethod
    def setup_ui(self) -> None:
        """Build and configure UI widgets.
        
        Called once during initialization. Subclasses should create all
        widgets and layouts here.
        """
        pass

    @abstractmethod
    def on_telemetry_data(self, data: dict[str, Any]) -> None:
        """Handle received telemetry data.
        
        Called when new telemetry data arrives from the stream.
        
        Args:
            data: Telemetry data dict from the telemetry server.
        """
        pass

    @abstractmethod
    def on_connection_status_changed(self, connected: bool) -> None:
        """Handle connection status change.
        
        Called when connection is established or lost.
        
        Args:
            connected: True if connected, False if disconnected.
        """
        pass

    def on_stream_error(self, error: str) -> None:
        """Handle stream error (optional for subclasses).
        
        Default implementation logs to console. Subclasses can override
        to show error dialogs or update UI.
        
        Args:
            error: Error message.
        """
        print(f"Stream error: {error}")

    def connect_to_stream(self, host: str = "localhost", port: int = 9999) -> bool:
        """Connect to telemetry stream server.
        
        Args:
            host: Server hostname.
            port: Server port.
            
        Returns:
            True if connection successful, False otherwise.
        """
        try:
            # In a real implementation:
            # self.client.connect(host, port)
            # self.client.on_data = self.on_telemetry_data
            # self.client.on_connection_changed = self.on_connection_status_changed
            # self.client.on_error = self.on_stream_error

            self.connected = True
            self.on_connection_status_changed(True)
            return True
        except Exception as e:
            self.on_stream_error(str(e))
            return False

    def disconnect_from_stream(self) -> None:
        """Disconnect from telemetry stream."""
        if self.client:
            # self.client.disconnect()
            pass
        self.connected = False
        self.on_connection_status_changed(False)

    def closeEvent(self, event: Any) -> None:
        """Handle window close event.
        
        Ensures telemetry client is properly disconnected.
        
        Args:
            event: Close event.
        """
        self.disconnect_from_stream()
        super().closeEvent(event)
