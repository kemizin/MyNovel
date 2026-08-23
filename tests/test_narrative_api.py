# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_narrative_api.py
#
# Waystone 7: reproduz literalmente o exemplo de historia do prompt,
# usando so a API publica (speak/enter/emotion/move/pause/exit/
# change_scene), sem nenhuma API interna da Engine.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import (
    enter,
    emotion,
    move,
    pause,
    exit as story_exit,
    change_scene,
)

jef = Character("Jef")
jef.add_emotion("normal", idle="assets/char/jefer/jefer.png", talking="assets/char/jefer/jefer_falano.png")
jef.add_emotion("bravo", idle="assets/char/jefer/jefer_soco.png")
jef.emotion("normal")

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png", talking="assets/char/ken/ken_falando.png")
ken.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
campo.add_character(ken, 3, scale=0.5)

quarto = Canvas("quarto", "assets/fundos/quarto.jpg", 1920, 1080)

# Exemplo do Waystone 7, igual ao do prompt, so com delay curto pra
# rodar sozinho (sem exigir input) e duracoes pequenas pra ser rapido.
story = [
    speak(ken, "Tem alguém aí?", delay=0.05),
    enter(jef, position=1),
    emotion(jef, "bravo"),
    speak(jef, "EU ESTOU AQUI!", delay=0.05),
    move(jef, position=2, scale=0.7),
    pause(0.1),
    speak(ken, "Você é assustador.", delay=0.05),
    story_exit(jef),
    change_scene(quarto),
]

engine = Engine()
engine.run(campo, story)

assert engine.canvas is quarto
assert "Jef" not in campo.characters
assert "Ken" in campo.characters

print("OK: exemplo narrativo completo do Waystone 7 rodou usando so a API publica")
