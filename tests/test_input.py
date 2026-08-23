# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_input.py
#
# Waystone 9 (Gameplay Update): Input.poll() organiza QUIT e o gesto
# de "avançar" (espaço/clique esquerdo) num só lugar, sem cada Action
# checar pygame.KEYDOWN/MOUSEBUTTONDOWN por conta própria.
#
# Roda headless (SDL_VIDEODRIVER=dummy).

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

from src.MyNovellib.input import Input

pygame.init()
pygame.display.set_mode((200, 200))

# --- sem eventos: nada acontece ---
pygame.event.clear()
result = Input.poll()
assert result.quit is False
assert result.advance is False
assert result.events == []

# --- espaco -> advance ---
pygame.event.clear()
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
result = Input.poll()
assert result.advance is True
assert result.quit is False

# --- clique esquerdo -> advance ---
pygame.event.clear()
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(10, 10)))
result = Input.poll()
assert result.advance is True

# --- clique direito NAO conta como advance ---
pygame.event.clear()
pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(10, 10)))
result = Input.poll()
assert result.advance is False

# --- outra tecla qualquer NAO conta como advance ---
pygame.event.clear()
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a))
result = Input.poll()
assert result.advance is False

# --- QUIT ---
pygame.event.clear()
pygame.event.post(pygame.event.Event(pygame.QUIT))
result = Input.poll()
assert result.quit is True

# --- eventos crus continuam disponiveis (pra quem precisa, tipo ChoiceUI) ---
pygame.event.clear()
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
result = Input.poll()
assert len(result.events) == 1
assert result.events[0].key == pygame.K_DOWN

pygame.quit()

print("OK: Input.poll() organiza QUIT/advance/eventos crus corretamente")
