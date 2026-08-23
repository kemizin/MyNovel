# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_choice_result.py
#
# Waystone 2 (Gameplay Update): o resultado da Choice (qual opção foi
# escolhida) precisa estar disponível pra Engine/historia depois da
# confirmação, sem estar acoplado a UI -- fica em
# `choice_action.selected_index`, um inteiro simples.
#
# Cobre as 4 combinações pedidas: primeira opção / segunda opção,
# por teclado / por mouse. Roda headless (SDL_VIDEODRIVER=dummy).

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
from src.MyNovellib.story import Choice, choice

SCREEN_W, SCREEN_H = 800, 600

# mesma formula de src/MyNovellib/engine.py:_choice_rects(), so pra
# calcular em que pixel clicar em cada opcao no teste.
BOX_W, BOX_H, GAP = 500, 60, 20
START_Y = (SCREEN_H - (2 * BOX_H + GAP)) // 2
CENTER_X = SCREEN_W // 2
OPTION_0_POS = (CENTER_X, START_Y + BOX_H // 2)
OPTION_1_POS = (CENTER_X, START_Y + BOX_H + GAP + BOX_H // 2)


def schedule(post_fn, delay=0.3):
    def worker():
        time.sleep(delay)
        post_fn()
    threading.Thread(target=worker, daemon=True).start()


def run_choice(post_fn):
    ken = Character("Ken")
    ken.add_emotion("normal", idle="assets/char/ken/ken.png")
    ken.emotion("normal")

    campo = Canvas("campo", "assets/fundos/campo.jpg", SCREEN_W, SCREEN_H)
    campo.add_character(ken, 2, scale=0.5)

    action = choice("Ir para casa", "Ficar aqui")
    assert isinstance(action, Choice)
    assert action.selected_index is None  # nao decidido antes de rodar

    schedule(post_fn)

    engine = Engine()
    engine.run(campo, [action])

    return action.selected_index


# --- teclado, primeira opcao (Enter direto -- selecao comeca em 0) ---
result = run_choice(
    lambda: pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
)
assert result == 0, f"teclado/primeira: esperava 0, veio {result}"

# --- teclado, segunda opcao (seta pra baixo, depois confirma) ---
def keyboard_second():
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))

result = run_choice(keyboard_second)
assert result == 1, f"teclado/segunda: esperava 1, veio {result}"

# --- mouse, primeira opcao (clique direto na primeira caixa) ---
result = run_choice(
    lambda: pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=OPTION_0_POS))
)
assert result == 0, f"mouse/primeira: esperava 0, veio {result}"

# --- mouse, segunda opcao (clique direto na segunda caixa) ---
result = run_choice(
    lambda: pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=OPTION_1_POS))
)
assert result == 1, f"mouse/segunda: esperava 1, veio {result}"

print("OK: selected_index correto nas 4 combinacoes (teclado/mouse x primeira/segunda opcao)")
