# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_choice_state.py
#
# Waystone 4 (Gameplay Update): CHOICE -> RESULTADO -> GAME STATE.
# Cada opção pode carregar um dict de efeitos {chave: quantidade},
# aplicado via GameState.increment() na opção confirmada.
#
# Roda headless (SDL_VIDEODRIVER=dummy).

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
from src.MyNovellib.state import GameState
from src.MyNovellib.story import choice


def schedule(post_fn, delay=0.3):
    def worker():
        time.sleep(delay)
        post_fn()
    threading.Thread(target=worker, daemon=True).start()


def make_scene():
    ken = Character("Ken")
    ken.add_emotion("normal", idle="assets/char/ken/ken.png")
    ken.emotion("normal")
    campo = Canvas("campo", "assets/fundos/campo.jpg", 800, 600)
    campo.add_character(ken, 2, scale=0.5)
    return campo


def confirm(key=pygame.K_RETURN):
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=key))


def confirm_second():
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))


# --- opcao "Ajudar" (indice 0): amizade += 1 ---
action = choice(
    ("Ajudar Jef", {"amizade": 1}),
    ("Ignorar Jef", {"amizade": 0}),
)
schedule(confirm)
engine = Engine()
engine.run(make_scene(), [action])
assert action.selected_index == 0
assert engine.state.get("amizade") == 1, engine.state.get("amizade")

# --- opcao "Ignorar" (indice 1): amizade += 0 ---
action = choice(
    ("Ajudar Jef", {"amizade": 1}),
    ("Ignorar Jef", {"amizade": 0}),
)
schedule(confirm_second)
engine = Engine()
engine.run(make_scene(), [action])
assert action.selected_index == 1
assert engine.state.get("amizade") == 0, engine.state.get("amizade")

# --- opcao sem efeito (string simples), misturada com uma com efeito ---
action = choice(
    "Nada acontece",
    ("Ganha amizade", {"amizade": 5}),
)
schedule(confirm)  # confirma a primeira (string simples, sem efeito)
engine = Engine()
engine.run(make_scene(), [action])
assert action.selected_index == 0
assert engine.state.get("amizade") == 0  # nao mudou

# --- GameState explicito passado pra Engine e o MESMO objeto e mutado ---
shared_state = GameState()
shared_state.set("amizade", 10)

action = choice(
    ("Ajudar Jef", {"amizade": 1}),
    ("Ignorar Jef", {"amizade": 0}),
)
schedule(confirm)
engine = Engine(state=shared_state)
engine.run(make_scene(), [action])
assert engine.state is shared_state
assert shared_state.get("amizade") == 11

print("OK: escolha -> resultado -> GameState aplicado corretamente em todos os casos")
