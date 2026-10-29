# RAM Tower Rescue — Pygame PoC

A small, runnable 2D educational computer-science game prototype based on the project brief.

## Features
- Top-down single-room RAM Tower District gray-box environment
- WASD / arrow-key movement with room boundaries
- Walk to the glowing terminal and press **E** to open the puzzle
- Memory allocation puzzle with active/inactive programs
- Release memory from inactive programs, allocate it to an active program
- Protected active memory cannot be released; clear failure feedback
- Submit, success, failure, hint, retry, and return-to-room flows
- Challenge title, objective, and hint loaded from `data/game_challenges.csv`
- Automated unit tests for core puzzle rules

## Requirements
Python 3.10+ recommended.

```bash
python -m venv .venv
source .venv/bin/activate       # macOS/Linux
# .venv\Scripts\activate      # Windows
python -m pip install -r requirements.txt
python -m src.main
```

If you are running this from the project directory, `python src/main.py` also works.

## Controls
- Move: **WASD** or **arrow keys**
- Interact with terminal: **E**
- Puzzle: click memory blocks/buttons; **H** for hint; **Enter** to submit; **R** to retry; **Esc** to return to room
- Result screen: **R** to retry; **Esc** to return to room

## Puzzle rules in this first implementation
This is a provisional design to make the prototype playable; tune it after reviewing RAM-001:
- The active `School Project App` needs **3 blocks**.
- The room begins with 4 occupied blocks and 2 free blocks.
- Two occupied blocks belong to inactive programs and can be released.
- Two occupied blocks belong to active programs and are protected.
- The player releases one inactive program's two blocks, then allocates the two newly freed blocks plus one already-free block to the target active app (3 blocks total).
- Submitting fewer than 3 allocated blocks fails the attempt and offers retry.
- Trying to release a protected active block fails the attempt and explains why.
- The rules live in `src/ram_puzzle.py`, not in the CSV.

The brief described these as design choices to validate, so the capacities are deliberately provisional.

## Art assets
The game uses drawn placeholder art until the main character concept art is provided. Put an approved transparent PNG at `assets/characters/main_character_poc.png` to use it automatically. A background image can be placed at `assets/environments/ram_tower_room.png`; the game falls back to a drawn room if either image is absent. Keep untouched originals in `assets/concepts/`.

## Project layout
```text
data/game_challenges.csv
src/main.py
src/game_data.py
src/ram_puzzle.py
tests/test_ram_puzzle.py
assets/
notebooks/
```

## Tests
```bash
python -m unittest discover -s tests -v
```
