# Exemplo: change_scene(canvas, transition=None, duration=0.5)
#
# Troca a cena (Canvas) atual: background, música, dimensões da
# janela e os personagens visíveis (cada Canvas tem seu próprio
# conjunto de personagens -- eles não "atravessam" a troca sozinhos).
#
# Sem `transition`, a troca é instantânea. Com transition="fade", a
# Engine faz fade out da cena atual, troca com a tela preta, e faz
# fade in da cena nova -- tudo em `duration` segundos ao todo.
#
# Roda com: .venv/Scripts/python.exe exemples/09_change_scene.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import change_scene, enter

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png", talking="assets/char/ken/ken_falando.png")
ken.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
quarto = Canvas("quarto", "assets/fundos/quarto.jpg", 1920, 1080)
sala = Canvas("sala", "assets/fundos/sala.jpg", 1920, 1080)

campo.add_character(ken, position=2, scale=0.6)

story = [
    speak(ken, "Estou no campo.", delay=1.5),

    # troca instantânea (sem transition)
    change_scene(quarto),
    enter(ken, position=2, scale=0.6),
    speak(ken, "Troquei pro quarto na hora, sem transicao.", delay=1.5),

    # troca com fade de 1 segundo
    change_scene(sala, transition="fade", duration=1.0),
    enter(ken, position=2, scale=0.6),
    speak(ken, "E agora troquei pra sala com fade.", delay=1.5),
]

engine = Engine()
engine.run(campo, story)
