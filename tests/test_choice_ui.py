# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_choice_ui.py
#
# Waystone 8 (Gameplay Update): ChoiceUI isolada da Engine -- testa a
# mecânica de hover/seleção/confirmação (teclado e mouse) direto,
# sem precisar rodar uma Story completa.
#
# Roda headless (SDL_VIDEODRIVER=dummy).

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from src.MyNovellib.choice_ui import ChoiceUI

pygame.init()
screen = pygame.display.set_mode((800, 600))
font = pygame.font.Font(None, 42)

ui = ChoiceUI(screen, font, ["A", "B", "C"])

# --- estado inicial ---
assert ui.selected == 0
assert len(ui.rects) == 3

# --- navegacao por teclado, com wrap-around ---
def key(k):
    return pygame.event.Event(pygame.KEYDOWN, key=k)

assert ui.handle_event(key(pygame.K_DOWN)) is None
assert ui.selected == 1

assert ui.handle_event(key(pygame.K_DOWN)) is None
assert ui.selected == 2

assert ui.handle_event(key(pygame.K_DOWN)) is None  # wrap: 2 -> 0
assert ui.selected == 0

assert ui.handle_event(key(pygame.K_UP)) is None  # wrap: 0 -> 2
assert ui.selected == 2

# --- tecla nao relacionada nao muda nada e nao confirma ---
assert ui.handle_event(key(pygame.K_a)) is None
assert ui.selected == 2

# --- confirmar por teclado retorna o indice atual ---
assert ui.handle_event(key(pygame.K_RETURN)) == 2

# --- hover por mouse muda a selecao, mas NAO confirma ---
ui.selected = 0
option_1_center = ui.rects[1].center
motion = pygame.event.Event(pygame.MOUSEMOTION, pos=option_1_center)
assert ui.handle_event(motion) is None
assert ui.selected == 1

# --- clique dentro de uma opcao confirma aquele indice ---
click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=option_1_center)
assert ui.handle_event(click) == 1

# --- clique fora de qualquer opcao nao confirma nada ---
outside_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(5, 5))
assert ui.handle_event(outside_click) is None

# --- clique com outro botao do mouse (nao o esquerdo) nao confirma ---
right_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=option_1_center)
assert ui.handle_event(right_click) is None

# --- desenhar nao levanta excecao ---
ui.draw()

pygame.quit()

print("OK: ChoiceUI (hover/selecao/confirmacao por teclado e mouse) funciona isolada da Engine")
