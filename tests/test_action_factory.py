# Teste pequeno, sem dependências externas, sem pygame (a Action
# Factory por si só não precisa de pygame -- story.py/dialogue.py
# tambem nao importam).
# Roda com: .venv/Scripts/python.exe tests/test_action_factory.py
#
# Project System Update, Waystone 8: ActionData -> Actions de Runtime.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.character import Character
from src.MyNovellib.dialogue import Dialogue
from src.MyNovellib.story import Emotion, Move, Enter, Exit, Pause
from src.MyNovellib.project.story_data import ActionData, StoryData
from src.MyNovellib.project.action_factory import build_action, build_story

assert "pygame" not in sys.modules

jef = Character("Jef")
ken = Character("Ken")
characters = {"jef": jef, "ken": ken}

# --- speak ---
action = build_action(
    ActionData("speak", character="ken", text="Olá!"),
    characters
)
assert isinstance(action, Dialogue)
assert action.character is ken
assert action.text == "Olá!"
assert action.speed == 0.03  # default
assert action.delay is None
assert action.dub is None

# speak com campos opcionais
action2 = build_action(
    ActionData("speak", character="ken", text="Oi", speed=0.01, delay=1, dub="voz.mp3"),
    characters
)
assert action2.speed == 0.01
assert action2.delay == 1
assert action2.dub == "voz.mp3"

# --- emotion ---
action = build_action(
    ActionData("emotion", character="jef", emotion="bravo"),
    characters
)
assert isinstance(action, Emotion)
assert action.character is jef
assert action.name == "bravo"

# --- move ---
action = build_action(
    ActionData("move", character="jef", position=2),
    characters
)
assert isinstance(action, Move)
assert action.character is jef
assert action.position == 2
assert action.scale is None  # nao informado -- move() so muda o que foi passado

# --- enter ---
action = build_action(
    ActionData("enter", character="ken", position=3, scale=0.6),
    characters
)
assert isinstance(action, Enter)
assert action.character is ken
assert action.position == 3
assert action.scale == 0.6

# --- exit ---
action = build_action(
    ActionData("exit", character="jef"),
    characters
)
assert isinstance(action, Exit)
assert action.character is jef

# --- pause ---
action = build_action(
    ActionData("pause", duration=1.5),
    characters
)
assert isinstance(action, Pause)
assert action.duration == 1.5

# --- personagem nao encontrado ---
try:
    build_action(ActionData("speak", character="fantasma", text="Buu"), characters)
    assert False, "esperava KeyError pra personagem nao resolvido"
except KeyError:
    pass

# --- build_story: StoryData inteiro vira lista de Actions, na ordem ---
story_data = StoryData(name="intro")
story_data.add_action("speak", character="ken", text="Tem alguém aí?")
story_data.add_action("enter", character="jef", position=1)
story_data.add_action("emotion", character="jef", emotion="bravo")
story_data.add_action("speak", character="jef", text="EU ESTOU AQUI!")
story_data.add_action("move", character="jef", position=2)
story_data.add_action("pause", duration=1)
story_data.add_action("exit", character="jef")

story = build_story(story_data, characters)

assert len(story) == 7
assert isinstance(story[0], Dialogue) and story[0].character is ken
assert isinstance(story[1], Enter) and story[1].character is jef
assert isinstance(story[2], Emotion) and story[2].name == "bravo"
assert isinstance(story[3], Dialogue) and story[3].text == "EU ESTOU AQUI!"
assert isinstance(story[4], Move) and story[4].position == 2
assert isinstance(story[5], Pause) and story[5].duration == 1
assert isinstance(story[6], Exit) and story[6].character is jef

print("OK: Action Factory converte ActionData/StoryData em Actions de Runtime (speak/emotion/move/enter/exit/pause)")
