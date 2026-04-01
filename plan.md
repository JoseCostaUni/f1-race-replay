# UI Refactor Plan: F1 Race Replay

## TL;DR
Refactor the F1 Race Replay UI from a tightly-coupled, monolithic structure into a modern, event-driven architecture using proper SOLID principles. Build a design system foundation (components, theming, layout, state) first, then apply it to all windows via a big-bang refactor. Maintain Arcade + PySide6 hybrid (Arcade for visualization, PySide6 for dialogs).

## Phase 1: Design System & Architecture Foundation

**Goal**: Establish reusable, decoupled, testable infrastructure before touching existing windows.

### 1.1 Config & Theme System
- **File**: `src/config/theme.py` — Centralized color palette, spacing, typography presets
  - Move all hardcoded colors (#282828, #E8002D, etc.) into theme constants
  - Support light/dark mode switching (no implementation yet, just structure)
  - Use TypedDict or dataclass for type safety
- **File**: `src/config/layout.py` — Layout constants (margins, padding, component widths, breakpoints)
  - Source of truth for all positioning instead of hardcoded values in components
  - Enables responsive design later

### 1.2 Event Bus System
- **File**: `src/architecture/event_bus.py` — Lightweight pub/sub event system
  - Event types: `PlaybackStateChanged`, `FrameIndexChanged`, `DriverSelected`, `SettingsUpdated`, etc.
  - Allows components to communicate without direct coupling
  - Simple implementation: dict of event name → list of callbacks

### 1.3 State Management
- **File**: `src/architecture/state_manager.py` — Single source of truth for playback state
  - Manages: current_frame, paused, playback_speed, selected_driver, settings
  - Emits events on state changes (integrates with event bus)
  - Components read state via getter methods, never access window object directly

### 1.4 Dependency Injection System
- **File**: `src/architecture/dependencies.py` — IoC container for component creation
  - Registers: StateManager, EventBus, Theme, Settings, DataProviders
  - Components receive only what they need (not `window` object)
  - Enables testing (swap real implementations with mocks)

### 1.5 Component Protocols & Base Classes
- **File**: `src/ui/component.py` — Unify Arcade + PySide6 component interfaces
  - `ArcadeComponent` base (draw, on_resize, handle_event)
  - `QtComponent` base (setup_ui, connect_signals)
  - Both inherit common interface: `on_state_change()`, `on_event()`

### 1.6 Layout System (Arcade-only, non-intrusive)
- **File**: `src/ui/layout.py` — Simple grid/flex layout helpers for Arcade
  - Components declare layout constraints instead of hardcoding x, y
  - Solves "fragile positioning" problem
  - Example: `LeaderboardLayout(width=300, margin=20, anchor="top-right")`

---

## Phase 2: Component Refactoring & Organization

**Goal**: Break apart 2000+ line ui_components.py into focused, testable modules.

### 2.1 Split ui_components.py into feature modules
- **Leaderboards** (`src/ui/components/leaderboards.py`)
  - `LeaderboardComponent` (driver standings)
  - `LapTimeLeaderboardComponent` (qualifying)
  - Abstract `BaseLeaderboardComponent` (reduce duplication)

- **Progress & Timeline** (`src/ui/components/progress.py`)
  - `RaceProgressBarComponent` (split into smaller focused classes)
  - `RaceTimelineComponent` (just the timeline, no side effects)
  - `RaceEventMarkerComponent` (reusable event markers)
  - `RaceEventLegendComponent` (legend for statuses: DNF, safety car, etc.)

- **Info Panels** (`src/ui/components/panels.py`)
  - `DriverInfoPanel`
  - `SessionInfoPanel`
  - `WeatherPanel`
  - All use shared styling from theme.py

- **Controls & Overlays** (`src/ui/components/controls.py`)
  - `RaceControlsComponent` (playback buttons, speed slider)
  - `ControlsPopupComponent` → `KeyBindingOverlay`
  - `HelpLegendComponent` (reusable help widget)

- **Telemetry Visualization** (`src/ui/components/telemetry.py`)
  - `QualifyingLapTimeComponent` (sector breakdown chart)
  - `TyreComparisonComponent` (tyre degradation visual)
  - Base class: `ChartComponent` (shared rendering logic)

### 2.2 Create Utility Modules (move from ui_components bottom)
- **Utilities** (`src/ui/utils.py`)
  - `draw_text()`, `draw_box()`, helper methods
  - Move from scattered locations into reusable functions

### 2.3 Implement Protocols (SOLID: Interface Segregation)
- Each component interface is minimal
- Example:
  ```python
  class ArcadeComponent(Protocol):
      def on_state_change(self, state: PlaybackState) -> None: ...
      def on_event(self, event: UIEvent) -> None: ...
      def draw(self, renderer: Renderer) -> None: ...
      def on_input(self, input: InputEvent) -> bool: ...  # return True if consumed
  ```

---

## Phase 3: Window Refactoring

**Goal**: Apply new architecture to main windows (F1RaceReplayWindow, QualifyingReplay, etc.).

### 3.1 Refactor F1RaceReplayWindow (`src/interfaces/race_replay.py`)
**Current state**: 800+ lines, handles rendering, state, telemetry, degradation modeling
**New approach**: Separate concerns

- **Main Window Class** — Arcade window setup, game loop coordination only
  - Responsibilities: `on_draw()` (delegate to renderer), `on_update()` (delegate to state), input routing
  - Constructor receives injected: StateManager, EventBus, ComponentRegistry, DataProviders
  - ~100 lines

- **New**: `RaceReplayRenderer` class (`src/interfaces/race_replay_renderer.py`)
  - Coordinates all component rendering
  - Takes state + components → renders to screen
  - Testable (mock state, verify drawing calls)

- **New**: `TelemetryBroadcaster` class (extracted from window)
  - Handles TCP telemetry streaming to secondary windows
  - Decoupled from window logic
  - Observable: `@event_bus.on(StateChanged) → broadcast_telemetry()`

- **New**: `RaceLogic` class (extracted from degradation/gap calculations)
  - Manages computed_gaps, tyre_degradation, race-specific calculations
  - Subscribes to StateChanged events
  - Provides methods: `get_driver_gaps()`, `get_tyre_degradation()`, etc.

### 3.2 Refactor QualifyingReplay (`src/interfaces/qualifying.py`)
- Same pattern as F1RaceReplayWindow
- Shares components with race (LeaderboardComponent, ControlsPopupComponent, etc.)

### 3.3 Telemetry Architecture (unify PySide6 windows)
- **Base class**: `StreamSubscriber` (extracted from PitWallWindow + TelemetryStreamViewer)
  - Abstract: `setup_ui()`, `on_telemetry_data()`
  - Automatically handles client connection, data subscription
  - Replaces current duplicate code in:
    - `PitWallWindow` (for Insights)
    - `TelemetryStreamViewer`
    - Future insight windows

- **File**: `src/services/stream_subscriber.py`
  - Consolidates TelemetryStreamClient initialization
  - Handles error states, reconnection logic

---

## Phase 4: Testing & Validation Infrastructure

### 4.1 Component Testing Helpers
- **File**: `tests/unit/test_ui_components.py` (framework)
  - Mock StateManager, EventBus, Theme
  - Test component rendering (snapshot tests or render tree assertions)
  - Test state change reactions
  - Example: `test_leaderboard_updates_on_driver_selected()`

### 4.2 Integration Tests
- **File**: `tests/integration/test_race_replay_flow.py`
  - Load real data, simulate playback, assert rendering
  - Validate event flow end-to-end

---

## Implementation Steps (Execution Order)

1. **Create foundation** (Phase 1: no changes to existing windows yet)
   - theme.py + layout.py
   - event_bus.py
   - state_manager.py
   - dependencies.py
   - component.py + layout helpers
   - Tests for foundation ✓

2. **Modularize components** (Phase 2)
   - Split ui_components.py into features/
   - Update imports in existing windows (still use old event patterns, but now modular)
   - No window refactor yet

3. **Refactor windows** (Phase 3 — the big bang)
   - Rewrite F1RaceReplayWindow to use new architecture
   - Rewrite QualifyingReplay
   - Consolidate PySide6 windows via StreamSubscriber
   - Delete old ui_components.py once all references migrated

4. **Test & polish** (Phase 4)
   - Add unit + integration tests
   - Verify all features work
   - Measure performance (lag during playback)

---

## Relevant Files to Modify/Create

**Create (new architecture)**:
- `src/config/theme.py` — theme constants, colors, spacing
- `src/config/layout.py` — layout constants
- `src/architecture/event_bus.py` — pub/sub events
- `src/architecture/state_manager.py` — centralized state
- `src/architecture/dependencies.py` — IoC container
- `src/ui/component.py` — base classes & protocols
- `src/ui/layout.py` — layout helpers
- `src/ui/utils.py` — drawing utilities
- `src/ui/components/leaderboards.py`
- `src/ui/components/progress.py`
- `src/ui/components/panels.py`
- `src/ui/components/controls.py`
- `src/ui/components/telemetry.py`
- `src/interfaces/race_replay_renderer.py`
- `src/interfaces/telemetry_broadcaster.py`
- `src/services/stream_subscriber.py` (base for PySide6 windows)

**Modify (big bang refactor)**:
- `src/interfaces/race_replay.py` — rewrite using new architecture
- `src/interfaces/qualifying.py` — rewrite using new architecture
- `src/gui/pit_wall_window.py` — inherit from StreamSubscriber
- `src/insights/driver_telemetry_window.py` — use new base
- `src/insights/telemetry_stream_viewer.py` — use new base

**Delete**:
- `src/ui_components.py` (split into modular pieces)

---

## Design Patterns & SOLID Principles Applied

| Principle | How It Solves Current Issues |
|-----------|------------------------------|
| **Single Responsibility** | Split giant files (ui_components.py → leaderboards.py, progress.py, etc.). Each class has one reason to change. |
| **Open/Closed** | Components extend base classes; add new component types without modifying existing ones. |
| **Liskov Substitution** | `ArcadeComponent`, `QtComponent` hierarchies ensure subclasses are drop-in replacements. |
| **Interface Segregation** | Components declare small, focused protocols (state_change, events) not giant window dependencies. |
| **Dependency Inversion** | IoC container; components depend on abstractions (StateManager interface) not concrete windows. |
| **Event-Driven Architecture** | No tight coupling via event bus; components emit/subscribe rather than direct method calls. |
| **Template Method** | PitWallWindow → StreamSubscriber; base class handles setup, subclasses implement abstract hooks. |
| **Observer Pattern** | Event bus + state manager implement observable state updates. |

---

## Verification & Testing

### Automated
1. Unit tests: each component behavior isolated (mock state, verify draw calls)
2. Integration tests: full playback flow (load race data, simulate frame updates, assert UI responds)
3. Linting: enforce component protocol compliance
4. Performance: measure frame time before/after refactor (should be same or better)

### Manual
1. Load several race weekends; verify playback works smoothly
2. Test all insights windows; verify telemetry streaming works
3. Test responsive layout (resize window; verify positioning stays consistent)
4. Keyboard shortcuts; mouse interactions

---

## Decisions & Assumptions

1. **Keep Arcade + PySide6 hybrid** — Arcade is excellent for real-time game-like visualization. PySide6 for traditional UI widgets. No need to consolidate.
2. **Event bus over time-travel debugging** — Chose pub/sub over Redux-like immutable state for simplicity (F1 replay is real-time, not heavy undo/redo needs).
3. **Big bang refactor** — Owner wants clean slate. We build new architecture separately, then delete old code. Minimizes "old and new" complexity.
4. **No breaking API** — User-facing behaviors stay the same; only internal architecture changes.

---

## Further Considerations

1. **Theme Persistence** — Should users be able to save custom color schemes? (Not in scope, but design system makes this feasible later)
2. **Performance Monitoring** — Should we add telemetry to track rendering frame times during refactor? (Recommended for validation)
3. **Accessibility** — Current UI has no keyboard-only navigation or screen reader support. Design system enables a11y later if needed.
