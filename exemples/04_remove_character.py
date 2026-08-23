# Exemplo: remove_character(character)
#
# Remove um personagem da cena durante a execução da história. É o
# equivalente "técnico" de exit() -- faz a mesma coisa na prática,
# mas sem a conotação de "saída narrativa" (veja 06_exit.py para a
# diferença de uso).
#
# Roda com: .venv/Scripts/python.exe exemples/04_remove_character.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import remove_character

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png", talking="assets/char/ken/ken_falando.png")
ken.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
campo.add_character(ken, position=2, scale=0.6)

story = [
    speak(ken, "Estou aqui na cena.", delay=1.5),
    speak(ken, "Vou sumir tecnicamente, sem 'sair andando'.", delay=1.5),

    # remove_character() some com o personagem imediatamente -- a
    # tela já reflete a remoção antes da próxima fala.
    remove_character(ken),

    # a fala ainda aparece (o texto/nome não dependem do personagem
    # estar visível), mas o sprite do Ken já não está mais na tela.
    speak(ken, "Fui removido, mas minha fala ainda pode aparecer aqui.", delay=1.5),
]

engine = Engine()
engine.run(campo, story)
