# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_branching.py
#
# Waystone 6 (Gameplay Update): Choice + State + Conditions juntos --
# uma opção pode disparar Actions diretamente (ramificação real),
# além de alterar o GameState. set_state() faz atribuição direta.
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
from src.MyNovellib.story import choice, emotion, set_state, if_state


def schedule(post_fn, delay=0.3):
    def worker():
        time.sleep(delay)
        post_fn()
    threading.Thread(target=worker, daemon=True).start()


def confirm_first():
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))


def confirm_second():
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))


def make_jef():
    jef = Character("Jef")
    jef.add_emotion("normal", idle="assets/char/jefer/jefer.png")
    jef.add_emotion("bravo", idle="assets/char/jefer/jefer_soco.png")
    jef.emotion("normal")
    return jef


def make_canvas(jef):
    campo = Canvas("campo", "assets/fundos/campo.jpg", 800, 600)
    campo.add_character(jef, 1, scale=0.5)
    return campo


# --- caminho "Sim": emotion muda pra bravo, ajudou=1, marcador de rota ---
jef = make_jef()
state = GameState()

action = choice(
    ("Sim", {"ajudou": 1}, [
        emotion(jef, "bravo"),
        set_state("rota", "sim"),
    ]),
    ("Não", {"ajudou": 0}, [
        set_state("rota", "nao"),
    ]),
)

schedule(confirm_first)
engine = Engine(state=state)
engine.run(make_canvas(jef), [action])

assert action.selected_index == 0
assert state.get("ajudou") == 1
assert state.get("rota") == "sim"
assert jef.current_emotion == "bravo"

# --- caminho "Não": ramificação DIFERENTE executa, a do "Sim" nao ---
jef = make_jef()
state = GameState()

action = choice(
    ("Sim", {"ajudou": 1}, [
        emotion(jef, "bravo"),
        set_state("rota", "sim"),
    ]),
    ("Não", {"ajudou": 0}, [
        set_state("rota", "nao"),
    ]),
)

schedule(confirm_second)
engine = Engine(state=state)
engine.run(make_canvas(jef), [action])

assert action.selected_index == 1
assert state.get("ajudou") == 0
assert state.get("rota") == "nao"
assert jef.current_emotion == "normal"  # a ramificacao do "Sim" NAO rodou

# --- set_state faz atribuicao direta (sobrescreve, nao soma) ---
state = GameState()
state.set("pontos", 100)
jef = make_jef()
engine = Engine(state=state)
engine.run(make_canvas(jef), [set_state("pontos", 1)])
assert state.get("pontos") == 1  # sobrescreveu, nao somou (100+1)

# --- Choice + State + Conditions compostos: dois caminhos completos ---
def historia_completa(confirm_fn):
    jef = make_jef()
    state = GameState()

    story = [
        choice(
            ("Ajudar", {"amizade": 5}),
            ("Ignorar", {"amizade": 0}),
        ),
        if_state("amizade", ">=", 5, [
            emotion(jef, "bravo"),
            set_state("final", "bom"),
        ]),
        if_state("amizade", "<", 5, [
            set_state("final", "ruim"),
        ]),
    ]

    schedule(confirm_fn)
    engine = Engine(state=state)
    engine.run(make_canvas(jef), story)

    return jef, state


jef, state = historia_completa(confirm_first)
assert state.get("final") == "bom"
assert jef.current_emotion == "bravo"

jef, state = historia_completa(confirm_second)
assert state.get("final") == "ruim"
assert jef.current_emotion == "normal"

print("OK: choice com ramificacao, set_state e composicao Choice+State+Conditions funcionam")
