# 1. Issue Description and Requirements

## Issue Description

I identified two bugs in the race replay's leaderboard system, both originating from the same underlying mechanism. The application determines each driver's position on the leaderboard by computing a one-dimensional progress value called `progress_m`, which represents how many meters the car has covered since the start of the race. To obtain this value, each car's `(x, y)` telemetry coordinates are projected onto the track's reference centerline spline using the `_project_to_reference()` method, yielding a distance along the spline. That distance is then combined with the current lap number to produce a cumulative race distance:

```
progress_m = (lap - 1) * track_length + projected_m
```

This approach works well during normal racing, but it has two significant failure modes described below.

### End-of-Race Leaderboard Shuffling

When drivers complete their final lap and begin the cool-down lap, the leaderboard starts shuffling their positions erratically. Two drivers who may have crossed the line several seconds apart keep swapping places on the UI, sometimes multiple times per second.

The root cause is that the system has no concept of a driver being "finished." It continuously recalculates `progress_m` from the car's live coordinates, even after the driver has crossed the finish line. During the cool-down lap, drivers slow down significantly and take different racing lines than they would under race conditions. This introduces noise into the projected distance values. For two drivers whose finish times were close together, these noisy projections can overlap frame-to-frame, causing the sorting algorithm to flip their relative positions back and forth.

In practice this means the final standings on the leaderboard are unstable for the last portion of the replay, which undermines the whole point of showing race results.

### Pit Lane Progress Jitter

The second bug manifests when a driver enters the pit lane. Their progress indicator on the leaderboard begins to behave erratically — snapping backward, freezing in place for several frames, and then jumping forward abruptly.

The issue comes down to geometry. The `_project_to_reference()` method finds the nearest point on the main track centerline spline for a given `(x, y)` coordinate. When a car is on the main circuit this gives a sensible, monotonically increasing distance. But the pit lane is a physically separate path that runs alongside (and sometimes behind) the main straight. When the car is in the pit lane, the closest point on the main spline doesn't advance smoothly — it might stay roughly the same for multiple frames, or even move backwards depending on the curvature of the track and the pit entry angle.

The result is that a car driving perfectly smoothly through the pits shows chaotic progress values on the leaderboard, which is both visually distracting and functionally misleading.

## Requirements

### Functional Requirements
1. The system must determine the exact moment each driver crosses the finish line on their final lap, with enough precision to correctly order all finishing drivers.
2. Once a driver has completed the race, their leaderboard position must become fixed. No further recalculation of their progress should take place based on post-race coordinates.
3. Progress through the pit lane must be represented smoothly, with values that advance consistently in the forward direction without visual glitches.

### Non-Functional Requirements
1. The fix must not degrade the performance of the real-time rendering loop. Any additional computation should be done at initialization time, when the telemetry data is first loaded into memory.
2. The implementation should favor using data already available in the FastF1 telemetry frames rather than introducing custom heuristics or approximations.

### Edge Cases
* Drivers who retire before completing the final lap must not be marked as having finished the race.
* Some drivers begin the race from the pit lane rather than the grid, so pit detection logic must handle `in_pit` being true from the very first frame.
* On lap 1, cars positioned behind the start/finish line on the grid have a projected distance that wraps around (appears very large). The existing correction for this must not conflict with the new finish-detection logic.

---

# 2. Changes to the source code files

All modifications were made in a single file: `src/interfaces/race_replay.py`. The changes can be grouped into two areas: the initialization of the replay window and the runtime progress calculation.

### Changes to `__init__` — pre-calculating finish times

I introduced a new instance variable `self.driver_finish_times`, which is a dictionary mapping each driver's three-letter code to the timestamp at which they completed the race. This dictionary is populated during the constructor by iterating through every loaded telemetry frame.

For each frame, the code inspects every driver's current lap number. The first time a driver's lap exceeds `total_laps`, that frame's timestamp is recorded as their finish time. The check `if code not in self.driver_finish_times` ensures that only the first occurrence is captured — subsequent frames where the driver remains on `total_laps + 1` are ignored. This way I get the exact moment of crossing, not some later timestamp from the cool-down lap.

```python
self.driver_finish_times = {}
if self.total_laps is not None and frames:
    for frame in frames:
        frame_time = frame.get("t", 0.0)
        for code, pos in frame.get("drivers", {}).items():
            if code not in self.driver_finish_times:
                lap_raw = pos.get("lap", 1)
                try:
                    lap = int(lap_raw)
                except (ValueError, TypeError):
                    lap = 1
                if lap > self.total_laps:
                    self.driver_finish_times[code] = frame_time
```

This loop adds a negligible amount of time to the startup phase since it is simply reading data that is already in memory. It does not affect the render loop at all.

### Changes to the progress calculation

The progress calculation logic appears in two separate methods within the file: the main per-frame update method and the leaderboard sorting/ranking method. Both were modified with the same branching logic to ensure consistent behavior between the visual display and the internal state.

Previously, both locations always called `_project_to_reference()` on the driver's coordinates and used that to compute `progress_m`. After the change, the code now checks for three distinct cases before computing progress:

```python
if self.total_laps is not None and lap > self.total_laps and code in self.driver_finish_times:
    # Case 1: Driver has already finished the race — assign a locked progress value
    finish_time = self.driver_finish_times[code]
    base_finish_m = self.total_laps * self._ref_total_length
    progress_m = float(base_finish_m + (100000.0 - finish_time))

else:
    if pos.get("in_pit", False):
        # Case 2: Driver is in the pit lane — use FastF1's cumulative distance
        projected_m = float(pos.get("dist", 0.0))
    else:
        # Case 3: Normal on-track racing — project (x, y) onto the centerline as before
        projected_m = self._project_to_reference(x, y)

    progress_m = float((max(lap, 1) - 1) * self._ref_total_length + projected_m)

driver_progress[code] = progress_m
```

It was important to apply this in both locations. If only one method was updated, the leaderboard rendering and the internal progress state would diverge, potentially causing other visual inconsistencies.

---

# 3. Design of the fix

The fix was implemented across three separate commits, each addressing one layer of the problem. This staging approach was chosen to make the changes easier to review and to allow individual stages to be reverted independently if they introduced regressions.

### Stage 1 — Pre-calculating exact finish times

The first step was establishing a reliable source of truth for when each driver finishes the race. I considered two approaches: detecting the finish in real time during the replay loop, or scanning the telemetry data in advance during initialization. I went with the second option because all the frame data is already loaded into memory before the replay starts, so iterating through it one additional time carries minimal cost and avoids adding any state-tracking complexity to the render loop.

The implementation loops through every frame and checks each driver's lap number. When a driver's lap first exceeds `total_laps`, that frame's timestamp is saved in `self.driver_finish_times`. The `if code not in self.driver_finish_times` guard is essential here — without it, the timestamp would keep getting overwritten on every subsequent frame (since the driver's lap stays at `total_laps + 1` for the remainder of the replay), and the precision of the actual crossing moment would be lost.

After this loop runs, there is a complete dictionary mapping every finishing driver to their exact finish timestamp. Drivers who retired before the final lap simply never appear in this dictionary, which naturally handles that edge case.

### Stage 2 — Locking the leaderboard after finishing

With the finish times available, the next step was to prevent the leaderboard from recalculating positions for drivers who have already completed the race. The challenge here was doing this without overhauling the existing sorting mechanism. The leaderboard ranks drivers by their `progress_m` value — the higher the value, the higher the position. So I needed to assign each finished driver a deterministic, constant `progress_m` that also preserves the correct finishing order among them.

The formula I arrived at is:

```
progress_m = base_finish_m + (100000.0 - finish_time)
```

This works in two parts. First, `base_finish_m` is set to `total_laps * track_length`, which is the theoretical distance at the exact finish line. This value alone already guarantees that any finished driver is placed ahead of any driver still racing (who will always have a lower cumulative distance). Second, the term `(100000.0 - finish_time)` serves as a tiebreaker among the finished drivers. Since a smaller finish time means the driver finished earlier, subtracting it from a large constant (100,000) produces a larger value for faster finishers. For example, a driver finishing at t=5400s gets a modifier of 94,600, while a driver finishing at t=5410s gets 94,590 — correctly placing the earlier finisher ahead.

The constant 100,000 is arbitrary but chosen to be comfortably larger than any realistic F1 race duration in seconds (a typical race lasts around 5,000–7,000 seconds). Once a driver enters this branch, their `progress_m` is computed purely from the pre-calculated finish time and never changes again, which completely eliminates the shuffling problem.

### Stage 3 — Using FastF1 telemetry for pit lane progress

The pit lane fix ended up being more straightforward than expected. Each telemetry frame that FastF1 provides already contains two relevant fields that were not being used: `in_pit` (a boolean indicating whether the car is in the pit lane) and `dist` (the cumulative distance driven by the car along its actual path, including through the pit lane).

The key insight is that FastF1's `dist` value is computed from the car's real driven trajectory, not from a projection onto the track centerline. This means it advances smoothly and linearly even when the car is in the pit lane, since it follows the actual path the car took rather than trying to map it to a different reference line.

The change is conceptually simple: when `in_pit` is true, `_project_to_reference()` is bypassed entirely and `dist` is used directly as the projected distance. The rest of the progress calculation (combining with lap count) remains the same. Despite being a small change in terms of lines of code, the visual improvement is significant — cars going through the pits now show steady, consistent forward progress instead of erratic jumps.

As with the leaderboard lock, this change was applied in both locations where progress is calculated to maintain consistency between the rendered leaderboard and the internal state.
