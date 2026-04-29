[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/Etw90P0Z)
# DIPPID and Pyglet
## Setup
Clone the repo, then `cd assignment-01-Alphazerfall`.

Set up a virtual environment using`python -m venv .venv`.

Activate the virtual environment using `venv\Scripts\activate` on Windows and `source venv/bin/activate` on Linux/Mac.

Install the requirmenets via `pip install -r requirements.txt`

## DIPPID Sender
To start the simulated sender, run `python dippid_sender/DIPPID_sender.py`.


## Space Invaders with DIPPID
A Space Invaders clone built with [pyglet](https://pyglet.org/), controlled via a [DIPPID](https://github.com/PDA-UR/DIPPID-py) device. Tilt to move, press any button to shoot. To quit the game, press `Q` on the keyboard or close the window.

Make sure your DIPPID device is sending data to UDP port `5700`.

Run via `python 2d_game/main.py`.

### Assets 
This project is inspired by https://github.com/brunotnasc/space-invaders/tree/master. Assets include:
- [sprite sheet](https://www.deviantart.com/gooperblooper22/art/Space-Invaders-Sprite-Sheet-135338373)
- [CRT border sprite](https://github.com/clear-code-projects/Space-invaders/blob/main/graphics/tv.png)
- [sound effects](https://www.classicgaming.cc/classics/space-invaders/sounds)
