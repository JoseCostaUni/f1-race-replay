"""Race-specific logic and calculations.

Extracts degradation modeling, gap calculations, and other race logic
from the main window. Subscribes to state changes to maintain derived data.
"""

from typing import Any, Dict, List, Optional

from src.architecture.event_bus import EventBus, EventType, UIEvent
from src.architecture.state_manager import PlaybackState, StateManager


class RaceLogic:
    """Manages race-specific calculations and derived data.
    
    Responsible for:
    - Computing driver gaps and positions
    - Tracking tyre degradation
    - Maintaining race state (DNFs, pit stops, etc.)
    - Providing data to components
    
    Separates race logic from rendering/window management.
    """

    def __init__(self, state_manager: StateManager, event_bus: EventBus):
        """Initialize race logic.
        
        Args:
            state_manager: State manager.
            event_bus: Event bus.
        """
        self.state = state_manager
        self.event_bus = event_bus

        self.drivers: List[Dict[str, Any]] = []
        self.gaps: Dict[int, float] = {}  # driver_number -> gap_to_leader
        self.tyre_degradation: Dict[int, List[float]] = {}  # driver_number -> [health...]
        self.dnf_drivers: set[int] = set()

        # Subscribe to frame changes (recalculate derived data)
        self.event_bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._on_frame_changed)

    def _on_frame_changed(self, event: UIEvent) -> None:
        """Handle frame change - recalculate derived data."""
        self._recalculate_gaps()
        self._recalculate_tyre_degradation()

    def set_drivers(self, drivers: List[Dict[str, Any]]) -> None:
        """Set initial driver list.
        
        Args:
            drivers: List of driver data dicts.
        """
        self.drivers = drivers

    def _recalculate_gaps(self) -> None:
        """Recalculate driver gaps based on current frame."""
        # In a real implementation:
        # 1. Get telemetry data for current frame from data provider
        # 2. Calculate each driver's position and gap to leader
        # 3. Update self.gaps
        pass

    def _recalculate_tyre_degradation(self) -> None:
        """Recalculate tyre degradation based on current frame."""
        # In a real implementation:
        # 1. Get telemetry data for current frame
        # 2. Calculate tyre health/degradation
        # 3. Update self.tyre_degradation
        pass

    def get_driver_gaps(self) -> Dict[int, float]:
        """Get current gaps to leader.
        
        Returns:
            Dict mapping driver_number to gap in seconds.
        """
        return self.gaps.copy()

    def get_tyre_degradation(self) -> Dict[int, List[float]]:
        """Get tyre degradation data.
        
        Returns:
            Dict mapping driver_number to list of health values over race.
        """
        return {k: v.copy() for k, v in self.tyre_degradation.items()}

    def mark_dnf(self, driver_number: int) -> None:
        """Mark driver as DNF (Did Not Finish).
        
        Args:
            driver_number: Driver number.
        """
        self.dnf_drivers.add(driver_number)

    def is_dnf(self, driver_number: int) -> bool:
        """Check if driver is DNF.
        
        Args:
            driver_number: Driver number.
            
        Returns:
            True if driver DNF, False otherwise.
        """
        return driver_number in self.dnf_drivers

    def get_dnf_drivers(self) -> set[int]:
        """Get set of DNF drivers.
        
        Returns:
            Set of driver numbers that DNF'd.
        """
        return self.dnf_drivers.copy()
