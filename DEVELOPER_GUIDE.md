# Quick Reference: Modern UI Architecture

**For developers working with the refactored F1 Race Replay UI.**

---

## 🎯 Core Concepts

### 1. **Event Bus** — Publish/Subscribe Communication
```python
from src.architecture.event_bus import EventBus, EventType, get_event_bus

bus = get_event_bus()

# Subscribe to events
def on_frame_changed(event):
    print(f"Frame: {event.data}")

bus.subscribe(EventType.FRAME_INDEX_CHANGED, on_frame_changed)

# Emit events
bus.emit(EventType.FRAME_INDEX_CHANGED, 42)

# Unsubscribe
unsub = bus.subscribe(EventType.DRIVER_SELECTED, handler)
unsub()  # Stop listening
```

### 2. **State Management** — Single Source of Truth
```python
from src.architecture.state_manager import StateManager
from src.architecture.event_bus import get_event_bus

state = StateManager(get_event_bus())

# Read state (no side effects)
frame = state.get_frame()
is_paused = state.get_paused()
selected = state.get_selected_driver()

# Modify state (auto-emits events)
state.set_frame(100)
state.set_paused(True)
state.select_driver(3)

# State is immutable internally
state_snapshot = state.get_state()
print(state_snapshot.current_frame)
```

### 3. **Dependency Injection** — Explicit Dependencies
```python
from src.architecture.dependencies import DIContainer

container = DIContainer()

# Register dependencies
container.register_singleton("event_bus", event_bus)
container.register_singleton("state", state_manager)
container.register_factory("my_service", lambda: MyService())

# Resolve in your code
service = container.resolve("my_service")

# Service Locator pattern
locator = ServiceLocator(container)
state = locator.get_state_manager()
```

### 4. **Theme & Colors** — Centralized Design System
```python
from src.config.theme import DEFAULT_THEME, get_driver_color

# Access theme colors
bg_color = DEFAULT_THEME.colors.bg_dark  # "#282828"
text_color = DEFAULT_THEME.colors.text_primary  # "#F0F0F0"
error_color = DEFAULT_THEME.colors.error  # "#FF4444"

# Get driver-specific colors
color = get_driver_color(driver_index=2)  # Rotate through 10 colors

# Spacing/Typography
margin = DEFAULT_THEME.spacing.lg  # 16
font_size = DEFAULT_THEME.typography.size_lg  # 16
```

### 5. **Layout Helpers** — Responsive Positioning
```python
from src.ui.layout import LayoutHelper, Anchor, Bounds

# Anchor a component to window corner
bounds = LayoutHelper.anchor_component(
    window_width=1920,
    window_height=1080,
    component_width=300,
    component_height=600,
    anchor=Anchor.TOP_RIGHT,
    margin_right=20,
    margin_top=20
)
print(bounds.x, bounds.y)  # Position

# Grid layout
grid = LayoutHelper.grid_layout(
    window_width=1920, window_height=1080,
    cols=3, rows=2,
    margin=20, gap=10
)
for row in grid:
    for cell in row:
        draw_at(cell.x, cell.y, cell.width, cell.height)

# Flex layout (row)
rects = LayoutHelper.flex_layout(
    window_width=1920, window_height=1080,
    count=4,  # 4 items
    direction="row",
    margin=20, gap=10
)
```

### 6. **Drawing Utilities** — No Hardcoded Arcade Calls
```python
from src.ui.utils import draw_text, draw_rectangle_filled, draw_line, hex_to_rgb

# Text
draw_text("Hello", 100, 100, color="#FF0000", font_size=14)

# Shapes
draw_rectangle_filled(x, y, width, height, color="#282828")
draw_line(100, 100, 200, 200, color="#FFFFFF", width=2)

# Color conversion
rgb = hex_to_rgb("#FF0000")  # (255, 0, 0)
hex_color = rgb_to_hex(255, 0, 0)  # "#FF0000"
```

---

## 🧩 Creating Components

### Arcade Component (for draws to screen)
```python
from src.ui.component import ArcadeComponent
from src.architecture.state_manager import StateManager
from src.architecture.event_bus import EventBus, EventType, UIEvent
from src.architecture.state_manager import PlaybackState

class MyComponent(ArcadeComponent):
    def __init__(self, x: float, y: float, width: float, height: float,
                 state_manager: StateManager, event_bus: EventBus):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.state = state_manager
        self.event_bus = event_bus
        
        # Subscribe to events
        self.event_bus.subscribe(EventType.FRAME_INDEX_CHANGED, self._on_frame)
    
    def _on_frame(self, event: UIEvent) -> None:
        """Handle frame change event."""
        print(f"Frame changed to {event.data}")
    
    def draw(self, renderer) -> None:
        """Draw the component."""
        from src.ui.utils import draw_rectangle_filled, draw_text
        draw_rectangle_filled(self.x, self.y, self.width, self.height, "#282828")
        draw_text(f"Frame: {self.state.get_frame()}", self.x + 10, self.y + 10)
    
    def on_resize(self, width: float, height: float) -> None:
        """Handle window resize."""
        self.width = width
    
    def handle_input(self, event_type: str, **kwargs) -> bool:
        """Handle mouse/keyboard input."""
        if event_type == "mouse_press":
            x, y = kwargs.get("x", 0), kwargs.get("y", 0)
            if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
                return True  # Consumed event
        return False
    
    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        # Components receive state updates here
        pass
    
    def on_event(self, event: UIEvent) -> None:
        """Handle custom events."""
        pass
```

### Qt Component (for PySide6 dialogs)
```python
from src.ui.component import QtComponent
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QLabel

class MyDialog(QtComponent):
    def setup_ui(self) -> None:
        """Build UI."""
        layout = QVBoxLayout()
        label = QLabel("Hello")
        layout.addWidget(label)
        # ... add more widgets
    
    def connect_signals(self) -> None:
        """Connect signals to slots."""
        # button.clicked.connect(self.on_button_clicked)
        pass
    
    def update_ui_state(self) -> None:
        """Update UI to reflect state changes."""
        # label.setText(f"Frame: {state.get_frame()}")
        pass
    
    def on_state_change(self, state: PlaybackState) -> None:
        """React to state changes."""
        self.update_ui_state()
    
    def on_event(self, event: UIEvent) -> None:
        """Handle events."""
        pass
```

---

## 🚀 Using Components in a Window

```python
import arcade
from src.architecture.event_bus import EventBus, get_event_bus
from src.architecture.state_manager import StateManager
from src.ui.component import ComponentRegistry
from src.interfaces.race_replay_renderer import RaceReplayRenderer
from src.ui.components.leaderboards import LeaderboardComponent
from src.ui.components.controls import RaceControlsComponent

class F1RaceReplayWindow(arcade.Window):
    def __init__(self):
        super().__init__(1920, 1080, "F1 Race Replay")
        
        # Set up architecture
        self.event_bus = get_event_bus()
        self.state = StateManager(self.event_bus)
        self.components = ComponentRegistry()
        self.renderer = RaceReplayRenderer(self.components)
        
        # Register components
        leaderboard = LeaderboardComponent(
            x=1600, y=220, width=300, height=600,
            state_manager=self.state,
            event_bus=self.event_bus
        )
        self.components.register("leaderboard", leaderboard)
        
        controls = RaceControlsComponent(
            x=20, y=20, width=1200, height=60,
            state_manager=self.state,
            event_bus=self.event_bus
        )
        self.components.register("controls", controls)
    
    def on_draw(self):
        arcade.start_render()
        self.renderer.render(self, self.state.get_state(), self.width, self.height)
    
    def on_key_press(self, key, modifiers):
        self.renderer.broadcast_input("key_press", key=key, modifiers=modifiers)
    
    def on_mouse_press(self, x, y, button, modifiers):
        self.renderer.broadcast_input("mouse_press", x=x, y=y, button=button)
    
    def on_update(self, delta_time):
        # Update playback logic
        if not self.state.get_paused():
            current = self.state.get_frame()
            speed = self.state.get_playback_speed()
            new_frame = current + int(speed)
            self.state.set_frame(new_frame)
```

---

## 📊 Testing Components

```python
import pytest
from src.architecture.event_bus import EventBus, get_event_bus, reset_event_bus
from src.architecture.state_manager import StateManager
from src.ui.components.leaderboards import LeaderboardComponent

@pytest.fixture
def setup():
    reset_event_bus()
    event_bus = EventBus()
    state = StateManager(event_bus)
    return event_bus, state

def test_leaderboard_updates_on_driver_selected(setup):
    event_bus, state = setup
    leaderboard = LeaderboardComponent(
        x=0, y=0, width=300, height=600,
        state_manager=state,
        event_bus=event_bus
    )
    
    # Set drivers
    leaderboard.set_drivers([
        {"number": 1, "name": "Driver 1"},
        {"number": 2, "name": "Driver 2"},
    ])
    
    # Select driver
    state.select_driver(1)
    
    # Verify component state updated
    assert leaderboard.selected_driver == 1

def test_state_manager_emits_events(setup):
    event_bus, state = setup
    events = []
    
    def capture(event):
        events.append(event)
    
    event_bus.subscribe("FRAME_INDEX_CHANGED", capture)
    state.set_frame(42)
    
    assert len(events) == 1
    assert events[0].data == 42
```

---

## 🔄 Event Types Reference

```python
from src.architecture.event_bus import EventType

# Playback control
EventType.FRAME_INDEX_CHANGED      # data: int (frame number)
EventType.PLAYBACK_STATE_CHANGED   # data: PlaybackState
EventType.PAUSED_TOGGLED           # data: bool
EventType.PLAYBACK_SPEED_CHANGED   # data: float

# Selection
EventType.DRIVER_SELECTED          # data: int (driver number)
EventType.LAP_SELECTED             # data: int (lap number)

# Settings
EventType.SETTINGS_UPDATED         # data: {"key": str, "value": any}
EventType.THEME_CHANGED            # data: str (theme name)

# Window
EventType.WINDOW_RESIZED           # data: {"width": int, "height": int}
EventType.WINDOW_CLOSED            # data: None

# Data
EventType.DATA_LOADED              # data: dict
EventType.DATA_UPDATED             # data: dict
EventType.DATA_ERROR               # data: str (error message)

# Telemetry
EventType.TELEMETRY_RECEIVED       # data: dict
EventType.CONNECTION_STATUS_CHANGED # data: bool
```

---

## 📁 File Structure Quick Reference

```
src/
├── config/              # Design system
│   ├── theme.py        # Colors, spacing, typography
│   └── layout.py       # Layout constants
├── architecture/        # Core infrastructure
│   ├── event_bus.py    # Pub/sub events
│   ├── state_manager.py # State management
│   └── dependencies.py  # IoC container
├── ui/                 # UI framework
│   ├── component.py    # Base classes
│   ├── layout.py       # Positioning helpers
│   ├── utils.py        # Drawing utilities
│   └── components/     # Feature components
│       ├── leaderboards.py
│       ├── progress.py
│       ├── panels.py
│       ├── controls.py
│       └── telemetry.py
├── interfaces/         # Windows/main logic
│   ├── race_replay.py  # Main window (to be refactored)
│   ├── race_replay_renderer.py
│   ├── race_logic.py
│   └── telemetry_broadcaster.py
└── services/
    └── stream_subscriber.py # PySide6 base

tests/
├── unit/
│   ├── test_event_bus.py
│   ├── test_state_manager.py
│   └── test_dependencies.py
└── integration/
    └── test_architecture.py
```

---

## 🎓 Common Patterns

### Pattern 1: Component reacts to state
```python
def on_state_change(self, state: PlaybackState) -> None:
    self.current_frame = state.current_frame
    self.is_paused = state.paused
    # Redraw happens automatically on next on_draw() call
```

### Pattern 2: Component emits event
```python
def handle_input(self, event_type: str, **kwargs) -> bool:
    if event_type == "mouse_press":
        # User clicked → emit event
        self.event_bus.emit(EventType.DRIVER_SELECTED, driver_number)
        return True
```

### Pattern 3: Subscribe to event
```python
def __init__(self, ...):
    self.event_bus.subscribe(EventType.DRIVER_SELECTED, self._on_driver_selected)

def _on_driver_selected(self, event: UIEvent) -> None:
    self.selected_driver = event.data
```

### Pattern 4: Responsive layout
```python
def on_resize(self, width: float, height: float) -> None:
    # Recalculate position for new window size
    bounds = LayoutHelper.anchor_component(
        window_width=width,
        window_height=height,
        component_width=300,
        component_height=600,
        anchor=Anchor.TOP_RIGHT,
        margin_right=20
    )
    self.x, self.y = bounds.x, bounds.y
```

---

## 🐛 Debugging Tips

1. **Check event subscriptions**: 
   ```python
   count = event_bus.subscriber_count(EventType.FRAME_INDEX_CHANGED)
   print(f"Subscribers: {count}")
   ```

2. **Monitor state changes**:
   ```python
   def debug_state_change(event):
       print(f"State changed: {event.data}")
   
   event_bus.subscribe(EventType.PLAYBACK_STATE_CHANGED, debug_state_change)
   ```

3. **Test component in isolation**:
   ```python
   # No window needed, just mock state/event_bus
   event_bus = EventBus()
   state = StateManager(event_bus)
   component = MyComponent(0, 0, 100, 100, state, event_bus)
   ```

4. **Verify colors**:
   ```python
   from src.config.theme import DEFAULT_THEME
   print(DEFAULT_THEME.colors.primary)  # Check actual color
   ```

---

**For more details, see:**
- 📖 [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) — Full architecture overview
- 📋 [plan.md](plan.md) — Original refactor plan
- 🧪 `tests/` — Working test examples
