# Zombie Blast 3D (ZB3D)

A from-scratch 2.5D polygonal raycasting renderer inspired by *Doom* (1993), written in pure Python with no engine or rendering libraries. The core is analytic ray–segment intersection against arbitrary wall geometry, solved per ray with Cramer's rule. On top of that sit fisheye-corrected perspective projection, distance- and orientation-based shading, depth-tested billboard sprites, and wall-sliding collision. A first-person zombie shooter is built on the engine as its test application.

CMU 15-112 term project (Spring 2026). Placed **2nd in the course-wide Term Project Showcase**, the top pure-Python entry.

> *The year is 2027. AI has taken over every task. Human brains, unused, began to rot. They now roam the world as zombies, hungry for the last independent mind. That mind is yours.*

---

## Running

```bash
pip install cmu-graphics
python ZB3D.py
```

Keep these assets in the same folder as `ZB3D.py`:

| File | Use |
|---|---|
| `ZB3D_Title.png` | Title screen |
| `doomkoz.png`, `godKoz.png` | HUD face (normal / god mode) |
| `shotgunSound.mp3`, `emptyShotgun.mp3` | Fire / dry fire |
| `zombieBite.mp3`, `deathSound.mp3` | Taking damage / death |

Default settings are 1280×720, 160 rays, 30 steps/sec — tuned to run in the CS Academy sandbox. Locally it runs at 320 rays / 60 fps by changing `app.numRays` and `app.stepsPerSecond`.

## Controls

| Key | Action |
|---|---|
| ↑ / ↓ | Move forward / back |
| ← / → | Turn |
| Space | Shoot |
| T | Toggle 3D view / 2D radar |
| P | Pause (shows controls) |
| R | Restart |
| Enter | Advance title → story → game |

**Cheats (hold together):** `G`+`U`+`N` — full-auto shotgun with infinite ammo. `G`+`O`+`D` — god mode.
**Dev keys** (`app.devMode = True`): `H` take 20 damage, `I` +5 score.

---

## How It Works

### Polygonal raycaster
The map is not a grid. Walls are arbitrary line segments, so the renderer can't use grid DDA. Instead, every ray is intersected against every wall segment analytically.

For a ray `P + t·r` and a wall `W₁ + u·w`, the intersection is the 2×2 linear system

```
| rdx  -wdx | | t |   | wx1 - px |
| rdy  -wdy | | u | = | wy1 - py |
```

solved with Cramer's rule (`solveMatrixCramer`). A hit is valid when `t ≥ 0` (in front of the player) and `0 ≤ u ≤ 1` (on the segment). A zero determinant means the ray and wall are parallel. `getRayHit` keeps the nearest valid hit.

### 3D projection
- One ray per vertical screen strip across an 80° FOV.
- Fisheye correction: distance is multiplied by `cos(rayAngle − playerAngle)` to get perpendicular distance.
- Strip height = `scaleConstant · screenHeight / dist`.
- Shading in `getFillColor`: face shading by wall orientation (horizontal 1.0, vertical 0.8, diagonal 0.9) times distance falloff clamped to 50%.
- Ceiling and floor are drawn first (painter's algorithm), then walls, then sprites.

### Zombie sprites
- Zombies are billboarded: angle to the zombie is normalized to [−π, π], culled outside the FOV, and mapped to a screen column.
- Size scales inversely with distance (capped at 80% of screen height).
- Occlusion: the zombie is skipped if the wall ray in its screen column is closer than the zombie.
- Zombies are sorted far-to-near and drawn back to front.
- Each zombie is a procedurally drawn humanoid with a health bar.

### Collision
- Player and zombies use point-to-line distance against each wall, with a bounding-box rejection test first to skip distant walls.
- X and Y movement are tested independently, so you slide along walls instead of sticking to them.

### Combat
- The shotgun hits every zombie inside a 10° cone that has line of sight (a ray toward the zombie must not hit a wall first).
- Base damage is 52–65, scaled by angle from center and by distance (down to 10% at 1000 units).
- 12-step fire cooldown drives the muzzle flash animation.

### Game loop and difficulty
- State machine: `menu → storyboard → playing → gameOver`, with pause as an overlay.
- Zombies spawn at four fixed points and seek the player at 1.2 units/step, dealing 30 damage/sec within 32 units.
- Each kill gives +1 score and +2 ammo, raises the zombie cap (`3 + score // 8`, max 20), and shortens the spawn interval.
- Ammo starts at 8 and caps at 20. It trickles back faster the lower you are (1 per 6 s below 4, 1 per 12 s below 9).
- Health regenerates 2/sec, and a red damage flash shows on hit.

### Map
Map 0 is an octagonal arena with four square columns that break line of sight and create cover. Maps are defined in `Map.loadMap(n)` with `addWall` and `addColumn` helpers, so new maps are just lists of segments.

---

## Code Structure (MVC)

| Layer | Contents |
|---|---|
| **Model** | `Player`, `Zombie`, `Map`, `Wall`; app state in `onAppStart` / `resetApp` |
| **View** | `drawMap3D`, `drawZombies3D` / `drawZombie`, `drawGun`, `drawHUD`, `drawMap2D`, menu / story / pause / game-over screens |
| **Controller** | `onKeyPress`, `onKeyHold`, `onStep` → `manageZombies`, `managePlayer`, `fireWeapon`, `damageZombies` |
| **Math** | `getRayLineIntersection`, `solveMatrixCramer`, `cross`, `dot`, `distance`, `playerDistanceToWall` |

## Development Notes
- **Started with brute-force ray marching.** The first prototype stepped each ray pixel by pixel across a tile map until it landed in a wall. I replaced that with arbitrary wall segments and analytic ray–segment intersection. That gave exact hits instead of step-size-limited ones, and allowed diagonals and free-form geometry.
- **Researched BSP, chose brute force.** I studied Doom's BSP pipeline in depth. For a single-arena map of ~24 segments, testing every wall per ray is fast enough and much simpler.
- **Performance target was CS Academy,** which forced the 160-ray / 30 fps budget. Pure Python with no C extensions.
- **Angles are radians everywhere**, converted once at setup.

## Future Work
- **CUDA parallelization.** Every ray is independent, since each reads the same wall list and writes one screen column. That maps directly to one GPU thread per ray, and should allow full-resolution ray counts in real time.
- **Fixed-point math.** Replace floats with fixed-point integers, as the original Doom did with 16.16 fixed-point. This would make arithmetic cheaper and deterministic.

## AI Attribution
15-112 allowed AI collaboration with attribution, and the specific spots are marked in source comments. Claude Sonnet 4.6 helped with:
- the logic of the `Zombie` class
- the Cramer's-rule setup and `0 ≤ u ≤ 1` bounds check in `getRayLineIntersection`
- sprite sort order and angle normalization in the zombie renderer
- the zombie body drawing code and pause screen
- generating map 0 and the base title image (which I edited)

The engine architecture, raycaster, collision, combat, and game systems are my own.

---
*Jorge Torres-Steele — Carnegie Mellon University*
