# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_sample_project.py
#
# Project System Update, Waystone 11: exemples/project_demo/ é um
# projeto MyNovel real (não um script Python) -- este teste confirma
# que qualquer pessoa que clone o repositório consegue carregá-lo e
# rodá-lo pelo Runtime, do jeito que está no disco.
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

from src.MyNovellib.project.directory import ProjectDirectory

PROJECT_PATH = "exemples/project_demo"

directory = ProjectDirectory(PROJECT_PATH)
assert directory.exists(), f"{PROJECT_PATH} não parece um projeto MyNovel válido"

project = directory.load()

assert project.name == "Project Demo"
assert set(project.characters) == {"mika"}
assert set(project.scenes) == {"praca"}
assert set(project.stories) == {"intro"}
assert len(project.assets) == 3

# create_runtime() sem `directory` -- usa project.loaded_from
# (setado pelo load()), exatamente como um usuário real faria.
runtime = project.create_runtime()

mika = runtime.characters["mika"]
praca = runtime.scenes["praca"]

assert "Mika" not in praca.characters  # so entra durante a historia (Action "enter")

# a story do demo usa speak() sem delay (interativo de verdade, pra
# quem for jogar de verdade) -- pygame.init() ja rodou (create_runtime
# construiu a Engine), entao agora simulamos alguem apertando espaco
# repetidamente, so pra validar headless que o projeto roda ate o fim
# sem excecao.
def auto_press_space():
    while True:
        time.sleep(0.15)
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))


threading.Thread(target=auto_press_space, daemon=True).start()

runtime.run()  # uma cena, uma historia -- roda sem precisar escolher

assert "Mika" not in praca.characters  # saiu no final (Action "exit")
assert mika.current_emotion == "normal"

print("OK: exemples/project_demo carrega e roda pelo Runtime, do jeito que esta no disco")
