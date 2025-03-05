# Rick and Morty Tactical RTS

A Myth-style real-time tactical strategy game set in the Rick and Morty universe.

## About

This game is inspired by Myth: The Fallen Lords and Myth II: Soulblighter, featuring tactical squad-based combat with a Rick and Morty theme. You command squads of units like Dimensioneers, Portal Archers, Tech Grenadiers, and Meeseeks Berserkers against enemies such as Gromflomite Soldiers and Cronenberg Horrors.

## Key Features

- Squad-based tactical gameplay with no base building or resource gathering
- Physics-driven combat with realistic projectiles, explosions, and persistent debris
- 3D terrain with height advantages and tactical positioning
- Formation-based movement and positioning
- Permanent squad losses and veteran status for surviving units

## Development

This project is under development. See the `implementationplan.md` file for the current development roadmap.

## Requirements

- macOS with Metal support
- Required dependencies listed in `requirements.txt`

## Setup and Running

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python src/main.py`

## Project Structure

- `src/` - Source code
  - `engine/` - Core engine components
  - `game/` - Game-specific logic and mechanics
- `assets/` - Game assets (sprites, terrain, audio)
- `resources/` - Configuration files and shaders
