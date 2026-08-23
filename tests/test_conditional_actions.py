# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_conditional_actions.py
#
# Waystone 5 (Gameplay Update): if_state(key, operador, value, actions)
# só executa as Actions internas se a condição sobre o GameState for
# verdadeira. Cobre os 6 operadores, valores booleanos, operador
# inválido e aninhamento.
#
# Roda headless (SDL_VIDEODRIVER=dummy).

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.state import GameState
from src.MyNovellib.story import if_state, emotion


def run_story(state, story):
    jef = Character("Jef")
    jef.add_emotion("normal", idle="assets/char/jefer/jefer.png")
    jef.add_emotion("bravo", idle="assets/char/jefer/jefer_soco.png")
    jef.emotion("normal")

    campo = Canvas("campo", "assets/fundos/campo.jpg", 800, 600)
    campo.add_character(jef, 1, scale=0.5)

    engine = Engine(state=state)
    engine.run(campo, story(jef))

    return jef


# --- condicao verdadeira: a Action interna executa ---
state = GameState()
state.set("amizade", 10)
jef = run_story(state, lambda jef: [
    if_state("amizade", ">=", 10, [emotion(jef, "bravo")])
])
assert jef.current_emotion == "bravo"

# --- condicao falsa: a Action interna NAO executa ---
state = GameState()
state.set("amizade", 3)
jef = run_story(state, lambda jef: [
    if_state("amizade", ">=", 10, [emotion(jef, "bravo")])
])
assert jef.current_emotion == "normal"

# --- todos os operadores ---
casos = [
    ("==", 5, 5, True),
    ("==", 5, 6, False),
    ("!=", 5, 6, True),
    ("!=", 5, 5, False),
    (">", 5, 3, True),
    (">", 5, 5, False),
    ("<", 3, 5, True),
    ("<", 5, 5, False),
    (">=", 5, 5, True),
    (">=", 4, 5, False),
    ("<=", 5, 5, True),
    ("<=", 6, 5, False),
]

for operador, valor_no_estado, valor_comparado, esperado in casos:

    state = GameState()
    state.set("valor", valor_no_estado)

    jef = run_story(state, lambda jef: [
        if_state("valor", operador, valor_comparado, [emotion(jef, "bravo")])
    ])

    resultado = jef.current_emotion == "bravo"

    assert resultado == esperado, (
        f"{valor_no_estado} {operador} {valor_comparado}: "
        f"esperava {esperado}, veio {resultado}"
    )

# --- valores booleanos ---
state = GameState()
state.set("porta_aberta", True)
jef = run_story(state, lambda jef: [
    if_state("porta_aberta", "==", True, [emotion(jef, "bravo")])
])
assert jef.current_emotion == "bravo"

state = GameState()
state.set("porta_aberta", False)
jef = run_story(state, lambda jef: [
    if_state("porta_aberta", "==", True, [emotion(jef, "bravo")])
])
assert jef.current_emotion == "normal"

# --- operador invalido levanta erro na criacao (falha cedo) ---
try:
    if_state("x", "**", 1, [])
    assert False, "esperava ValueError para operador invalido"
except ValueError:
    pass

# --- aninhamento: IfState dentro de IfState ---
state = GameState()
state.set("a", 10)
state.set("b", 10)
jef = run_story(state, lambda jef: [
    if_state("a", ">=", 10, [
        if_state("b", ">=", 10, [emotion(jef, "bravo")])
    ])
])
assert jef.current_emotion == "bravo"

# aninhado, mas a condicao de dentro e falsa
state = GameState()
state.set("a", 10)
state.set("b", 1)
jef = run_story(state, lambda jef: [
    if_state("a", ">=", 10, [
        if_state("b", ">=", 10, [emotion(jef, "bravo")])
    ])
])
assert jef.current_emotion == "normal"

print("OK: if_state cobre os 6 operadores, booleanos, erro de operador e aninhamento")
