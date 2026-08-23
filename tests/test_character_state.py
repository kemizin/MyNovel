# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_character_state.py
#
# Waystone 3: move() com campos parciais nao pode resetar
# scale/offset/emotion que ja estavam definidos.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.story import add_character, emotion, move

jef = Character("Jef")
jef.add_emotion("normal", idle="assets/char/jefer/jefer.png")
jef.add_emotion("bravo", idle="assets/char/jefer/jefer_soco.png")
jef.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)

story = [
    add_character(jef, position=1, scale=0.5, offset_x=20),
    emotion(jef, "bravo"),
    move(jef, position=2, scale=0.7),
    move(jef, position=3),
]

engine = Engine()
engine.run(campo, story)

data = campo.characters["Jef"]

# o segundo move() so mudou a posicao -- scale e offset_x tem que
# continuar com o que foi setado antes, nao voltar para o default.
assert data["position"] == 3
assert data["scale"] == 0.7, f"esperava scale=0.7, veio {data['scale']}"
assert data["offset_x"] == 20, f"esperava offset_x=20, veio {data['offset_x']}"
assert data["offset_y"] == 0

# emotion e is_speaking vivem no Character e nao sao tocados por move()
assert jef.current_emotion == "bravo"
assert jef.is_speaking is False

print("OK: move() parcial preserva scale/offset/emotion nao informados")
