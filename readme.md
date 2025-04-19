# Murder Mystery Adventure Game in Pygame & Python

This game is a tile-based 2D adventure game with murder mystery elements created with Pygame. The original game was based on the tutorial [Load Different Areas - Adventure Game in Pygame 7](https://youtu.be/jnokXcEo-8g).

## Quickstart

1. Open a terminal at the project location. In VSCode, go to the top where it says **Terminal**, and click **New Terminal**. If you don't see terminal, you may see three dots near the top left, click those and see if **Terminal** is under those.
2. Create a virtual environment. Run `python3 -m venv venv`. If you get an error, try `python -m venv venv`. If this still does not work, ensure [Python is installed on your system](https://www.python.org/downloads/). 
3. Activate the virtual environment. **On MacOS, Linux and Unix**, run `source venv/bin/activate`. **On Windows**, run `venv/Scripts/activate`.
4. Install Pygame by typing `pip install pygame`.
5. Run `python generate_assets.py` to create the necessary images for the murder mystery elements.
6. Run the game by typing `python src/main.py`.

## Navigation

|         Item         |  Description  |
|----------------------|---------------|
| [content](./content) | Asset files (images, map data, etc.) is here |
| [src](./src)         | Python code for the game is here. |

## Murder Mystery Features

This game has been extended with murder mystery elements:

- **Clues**: Scattered throughout the map, these objects can be interacted with by pressing the E key when nearby. They provide evidence for your investigation.
- **Suspects**: Characters you can talk to by pressing E when close to them. Each has an alibi and testimony to share.
- **Investigation System**: Tracks which clues you've found and which suspects you've interrogated.
- **Investigation Journal**: Access a detailed journal by pressing J that shows all discovered clues and suspect interviews.
- **Accusation System**: Once you've found all clues and interviewed all suspects, you can accuse someone of being the murderer by walking up to them and pressing the spacebar.
- **Game Outcome**: If you accuse the correct suspect, you win! But if you accuse an innocent person, you lose and the real murderer escapes.

## Controls

- **Arrow Keys**: Move the player character
- **E**: Interact with clues and suspects
- **J**: Open/close your investigation journal
- **Spacebar**: Accuse a suspect (only works when you've found all clues and interviewed all suspects)

## How to Solve the Case

1. Explore the map to find all clues (highlighted items you can interact with)
2. Talk to all suspects to gather their alibis and testimonies
3. Review your investigation journal (press J) to analyze the evidence
4. Based on the evidence, determine who you think is the murderer
5. Walk up to the suspect you believe is guilty and press spacebar to make your accusation
6. If you're right, you win! If you're wrong, you lose and the real murderer escapes

## How to Expand

You can expand this game by:
1. Adding more areas with new clues and suspects
2. Creating more complex testimony and alibi systems
3. Adding a dialog UI instead of console output
4. Implementing time pressure or other game mechanics
