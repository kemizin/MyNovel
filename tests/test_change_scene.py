# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_change_scene.py
#
# Waystone 5: change_scene() como Action solida -- troca background,
# dimensoes, musica e os personagens passam a ser os da nova cena.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import change_scene

# registra os tamanhos de janela pedidos durante a execucao, ja que
# engine.screen deixa de existir depois que run() chama pygame.quit()
requested_sizes = []
_original_set_mode = pygame.display.set_mode


def _tracking_set_mode(size):
    requested_sizes.append(tuple(size))
    return _original_set_mode(size)


pygame.display.set_mode = _tracking_set_mode

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png")
ken.emotion("normal")

jef = Character("Jef")
jef.add_emotion("normal", idle="assets/char/jefer/jefer.png")
jef.emotion("normal")

# duas cenas com tamanhos diferentes, musicas diferentes e personagens
# diferentes -- para garantir que TUDO troca junto.
campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080, music="assets/music/campo.wav")
campo.add_character(ken, 3, scale=0.5)

quarto = Canvas("quarto", "assets/fundos/quarto.jpg", 1280, 720, music="assets/music/quarto.wav")
quarto.add_character(jef, 2, scale=0.5)

story = [
    speak(ken, "Vamos para casa.", delay=0.1),
    change_scene(quarto),
    speak(ken, "Chegamos.", delay=0.1),
]

engine = Engine()
engine.run(campo, story)

# apos o change_scene, a engine tem que estar na cena nova
assert engine.canvas is quarto

# a janela tem que ter sido redimensionada de verdade durante a
# execucao: primeiro para o campo (1920x1080), depois para o quarto
assert requested_sizes == [(1920, 1080), (1280, 720)], requested_sizes

assert engine.canvas.tamanho == (1280, 720)

# os personagens visiveis agora sao os do quarto, nao os do campo
assert "Jef" in quarto.characters
assert "Ken" in campo.characters  # continua la, so nao e mais a cena ativa

print("OK: change_scene troca background/dimensoes/musica/personagens")
