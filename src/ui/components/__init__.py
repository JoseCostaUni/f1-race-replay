"""UI components module for F1 Race Replay.

Modular, reusable UI components split by feature domain instead of monolithic files.
"""

# Leaderboards
from src.ui.components.leaderboards import (
    LeaderboardComponent,
    LapTimeLeaderboardComponent,
    BaseLeaderboardComponent,
)

# Panels (info, weather, driver info)
from src.ui.components.panels import (
    DriverInfoPanel,
    SessionInfoPanel,
    WeatherPanel,
)

# Controls and overlays
from src.ui.components.controls import (
    HelpLegendComponent,
    KeyBindingOverlay,
    RaceControlsComponent,
    QualifyingSegmentSelectorComponent,
)

# Progress and timeline
from src.ui.components.progress import (
    RaceProgressBarComponent,
    RaceTimelineComponent,
    RaceEventMarkerComponent,
    RaceEventLegendComponent,
)

# Telemetry visualization
from src.ui.components.telemetry import (
    QualifyingLapTimeComponent,
    TyreComparisonComponent,
    ChartComponent,
)

# Legacy compatibility aliases (for backward compatibility during migration)
LegendComponent = HelpLegendComponent
ControlsPopupComponent = KeyBindingOverlay
DriverInfoComponent = DriverInfoPanel
SessionInfoComponent = SessionInfoPanel
WeatherComponent = WeatherPanel

__all__ = [
    # Leaderboards
    "LeaderboardComponent",
    "LapTimeLeaderboardComponent",
    "BaseLeaderboardComponent",
    # Panels
    "DriverInfoPanel",
    "SessionInfoPanel",
    "WeatherPanel",
    # Controls
    "HelpLegendComponent",
    "KeyBindingOverlay",
    "RaceControlsComponent",
    "QualifyingSegmentSelectorComponent",
    # Progress
    "RaceProgressBarComponent",
    "RaceTimelineComponent",
    "RaceEventMarkerComponent",
    "RaceEventLegendComponent",
    # Telemetry
    "QualifyingLapTimeComponent",
    "TyreComparisonComponent",
    "ChartComponent",
    # Legacy aliases
    "LegendComponent",
    "ControlsPopupComponent",
    "DriverInfoComponent",
    "SessionInfoComponent",
    "WeatherComponent",
]
