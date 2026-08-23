# Exemplo: speak(character, text, speed=0.03, delay=None, dub=None)
#
# speak() cria uma fala. Ela NÃO executa na hora -- só quando a Engine
# chega nela dentro da lista `story`.
#
# Controles: aperte ESPAÇO ou clique com o botão esquerdo do mouse
# para avançar (ou completar o texto instantaneamente, se ele ainda
# estiver "digitando").
#
# Roda com: .venv/Scripts/python.exe exemples/01_speak.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak

ken = Character("Ken")
ken.add_emotion(
    "normal",
    idle="assets/char/ken/ken.png",
    talking="assets/char/ken/ken_falando.png"
)
ken.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
campo.add_character(ken, position=2, scale=0.6)

story = [

    # delay=None (padrão): espera o jogador apertar espaço/clicar
    # para avançar depois que o texto terminar de aparecer.
    speak(ken, "Aperte espaco ou clique para continuar."),

    # speed controla a velocidade de digitação (segundos por caractere).
    # Quanto menor, mais rápido o texto aparece.
    speak(ken, "Isso aqui aparece rapido!", speed=0.01),
    speak(ken, "E isso aqui aparece bem devagar...", speed=0.08),

    # delay=N: depois que o texto termina, espera N segundos e avança
    # sozinho, sem precisar de input.
    speak(ken, "Essa fala some sozinha depois de 2 segundos.", delay=2),

    # dub: toca um áudio de dublagem junto com a fala. Se delay for
    # informado, a Engine espera o áudio (e depois o delay) antes de
    # avançar sozinha.
    speak(
        ken,
        "E essa fala tem uma dublagem tocando junto.",
        dub="assets/dubs/fala1.mp3",
        delay=1
    ),
]

engine = Engine()
engine.run(campo, story)
