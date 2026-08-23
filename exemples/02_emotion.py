# Exemplo: emotion(character, name)
#
# Troca a emoção atual de um personagem. A emoção precisa ter sido
# cadastrada antes com character.add_emotion(nome, idle, talking=None).
#
# A mudança aparece imediatamente na tela, mesmo sem nenhum speak()
# depois dela.
#
# Roda com: .venv/Scripts/python.exe exemples/02_emotion.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import emotion, pause

jef = Character("Jef")

# Cada emoção tem um sprite "idle" (parado) e, opcionalmente, um
# sprite "talking" (falando). Se "talking" não for informado, a
# Engine usa o "idle" mesmo enquanto o personagem fala.
jef.add_emotion(
    "normal",
    idle="assets/char/jefer/jefer.png",
    talking="assets/char/jefer/jefer_falano.png"
)
jef.add_emotion(
    "bravo",
    idle="assets/char/jefer/jefer_soco.png"
    # sem "talking" -- ao falar bravo, usa o mesmo sprite parado.
)
jef.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
campo.add_character(jef, position=2, scale=0.6)

story = [

    speak(jef, "Aqui eu estou com a emocao 'normal'.", delay=1.5),

    # Troca para "bravo". A tela já muda antes da próxima fala.
    emotion(jef, "bravo"),
    pause(0.5),

    speak(jef, "Agora estou com a emocao 'bravo'.", delay=1.5),

    emotion(jef, "normal"),
    pause(0.5),

    speak(jef, "E voltei para 'normal'.", delay=1.5),
]

engine = Engine()
engine.run(campo, story)
