# Teste pequeno, sem dependências externas (nem pygame -- GameState
# é puro Python).
# Roda com: .venv/Scripts/python.exe tests/test_game_state.py
#
# Waystone 3 (Gameplay Update): set/get/increment, flags booleanas e
# defaults previsíveis/configuráveis.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.state import GameState

# --- default global (0) quando a chave nunca foi definida ---
state = GameState()
assert state.get("amizade") == 0

state.set("amizade", 10)
assert state.get("amizade") == 10

# --- increment ---
state.increment("amizade")
assert state.get("amizade") == 11

state.increment("amizade", 5)
assert state.get("amizade") == 16

# increment numa chave que nunca existiu -- parte do default (0)
state.increment("pontos")
assert state.get("pontos") == 1

# --- flags booleanas ---
state.set("porta_aberta", True)
assert state.get("porta_aberta") is True

state.set("porta_aberta", False)
assert state.get("porta_aberta") is False

# --- default por chamada, sobrepondo o default global ---
assert state.get("nunca_existiu", "vazio") == "vazio"
assert state.get("nunca_existiu") == 0  # sem default explicito, usa o global

# --- default global configuravel na criacao ---
state_custom = GameState(default=None)
assert state_custom.get("qualquer_coisa") is None

print("OK: GameState.set/get/increment e defaults funcionam como esperado")
