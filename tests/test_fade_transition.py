# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_fade_transition.py
#
# Waystone 6: change_scene(canvas, transition="fade", duration=...)
# faz fade out -> troca -> fade in, sem espalhar codigo de fade pela
# Engine (tudo isolado em transitions.py).

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import change_scene

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png")
ken.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
campo.add_character(ken, 3, scale=0.5)

quarto = Canvas("quarto", "assets/fundos/quarto.jpg", 1920, 1080)

FADE_DURATION = 0.4

story = [
    speak(ken, "Vamos para casa.", delay=0.1),
    change_scene(quarto, transition="fade", duration=FADE_DURATION),
]

engine = Engine()

start = time.time()
engine.run(campo, story)
elapsed = time.time() - start

assert engine.canvas is quarto

# fade out (duration/2) + fade in (duration/2) = duration, no minimo
assert elapsed >= FADE_DURATION, (
    f"esperava pelo menos {FADE_DURATION}s de fade, rodou em {elapsed:.2f}s"
)

print(f"OK: change_scene com transition='fade' levou {elapsed:.2f}s e trocou para '{engine.canvas.nome}'")
