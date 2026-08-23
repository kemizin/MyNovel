# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_choice.py
#
# Waystone 1 (Gameplay Update): choice() pausa a historia e so
# continua depois que o jogador confirma uma opcao.
#
# Roda com SDL_VIDEODRIVER=dummy -- pygame real, sem abrir janela na
# tela (evita ficar reabrindo a aplicacao a cada teste).

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import choice

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png", talking="assets/char/ken/ken_falando.png")
ken.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 800, 600)
campo.add_character(ken, 2, scale=0.5)

# delay curto e speed rapido nas falas (em vez de None) so pra rodar
# sozinho sem input -- a Choice em si continua exigindo confirmacao
# de verdade.
story = [
    speak(ken, "O que vamos fazer?", speed=0.005, delay=0.05),
    choice("Ir para casa", "Ficar aqui"),
    speak(ken, "Escolha recebida.", speed=0.005, delay=0.05),
]

# tempo generoso: a primeira fala (com speed/delay curtos) termina
# bem antes disso, entao o evento so pode chegar durante a Choice.
CONFIRM_AFTER = 1.0


def post_confirm():
    time.sleep(CONFIRM_AFTER)
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))


threading.Timer(0, post_confirm).start()

engine = Engine()

start = time.time()
engine.run(campo, story)
elapsed = time.time() - start

# se a Engine NAO tivesse pausado esperando a escolha, a historia
# inteira (duas falas curtas) teria terminado bem antes de
# CONFIRM_AFTER segundos.
assert elapsed >= CONFIRM_AFTER, (
    f"esperava a Engine pausar ate pelo menos {CONFIRM_AFTER}s, "
    f"mas terminou em {elapsed:.2f}s -- choice() nao bloqueou a historia"
)

print(f"OK: choice() pausou a historia e so avancou apos confirmacao ({elapsed:.2f}s)")
