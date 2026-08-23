# Teste pequeno, sem dependências externas (sem pytest instalado no projeto).
# Roda com: .venv/Scripts/python.exe tests/test_actions_render.py
#
# Verifica a correção pedida: uma história feita só de Actions "silenciosas"
# (add_character, emotion, move -- sem nenhum speak() entre elas) precisa
# aplicar e RENDERIZAR cada mudança imediatamente, uma por uma.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.story import add_character, emotion, move


# Conta quantas vezes a tela foi atualizada (pygame.display.flip).
flip_count = 0
_original_flip = pygame.display.flip


def _counting_flip():
    global flip_count
    flip_count += 1
    _original_flip()


pygame.display.flip = _counting_flip


jef = Character("Jef")
jef.add_emotion(
    "normal",
    idle="assets/char/jefer/jefer.png",
    talking="assets/char/jefer/jefer_falano.png"
)
jef.add_emotion(
    "bravo",
    idle="assets/char/jefer/jefer_soco.png"
)
jef.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)

# História SEM nenhum speak() -- só Actions "silenciosas".
story = [
    add_character(jef, position=1, scale=0.5),
    emotion(jef, "bravo"),
    move(jef, position=2),
]

engine = Engine()
engine.run(campo, story)

# Cada uma das 3 Actions acima precisa ter disparado seu próprio redraw.
assert flip_count >= 3, (
    f"esperava pelo menos 3 atualizações de tela (1 por Action), "
    f"mas houve {flip_count}"
)

# E o estado final também precisa refletir as 3 Actions aplicadas.
assert "Jef" in campo.characters
assert jef.current_emotion == "bravo"
assert campo.characters["Jef"]["position"] == 2

print(f"OK: {flip_count} redraws, estado final aplicado corretamente")
