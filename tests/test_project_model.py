# Teste pequeno, sem dependências externas -- e SEM pygame de
# propósito: Project Data não pode depender da Engine.
# Roda com: .venv/Scripts/python.exe tests/test_project_model.py
#
# Project System Update, Waystone 1: criação e manipulação em memória
# de Project, e a garantia arquitetural mais importante desta fase --
# importar o modelo de projeto NÃO importa pygame.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# import isolado, antes de qualquer outra coisa: se Project (ou algo
# que ele importa) puxar pygame escondido, isso aparece aqui.
from src.MyNovellib.project.model import Project, PROJECT_FORMAT, CURRENT_FORMAT_VERSION

assert "pygame" not in sys.modules, (
    "importar Project puxou pygame junto -- Project Data não pode "
    "depender da Engine/Runtime."
)

# --- criação básica ---
project = Project(name="Minha VN")
assert project.name == "Minha VN"
assert project.resolution == (1920, 1080)  # default
assert project.version == CURRENT_FORMAT_VERSION
assert project.scenes == {}
assert project.stories == {}
assert project.assets == {}

# --- resolução customizada ---
project2 = Project(name="Outro Jogo", resolution=(1280, 720))
assert project2.resolution == (1280, 720)

# --- manipulação em memória ---
project.name = "Nome Renomeado"
assert project.name == "Nome Renomeado"

project.resolution = (800, 600)
assert project.resolution == (800, 600)

# containers sao dicts comuns -- da pra manipular direto (as classes
# de dado especificas chegam nos proximos waystones)
project.scenes["campo"] = {"nome": "campo"}
assert "campo" in project.scenes
assert len(project.scenes) == 1

# --- validacao: nome vazio ---
try:
    Project(name="")
    assert False, "esperava ValueError para nome vazio"
except ValueError:
    pass

try:
    Project(name="   ")
    assert False, "esperava ValueError para nome só com espaços"
except ValueError:
    pass

# --- validacao: resolucao invalida ---
try:
    Project(name="X", resolution=(1920,))
    assert False, "esperava ValueError para resolution incompleta"
except ValueError:
    pass

try:
    Project(name="X", resolution=(0, 1080))
    assert False, "esperava ValueError para resolution com valor <= 0"
except ValueError:
    pass

# --- repr util pra debug ---
assert "Minha VN" not in repr(project)  # foi renomeado
assert "Nome Renomeado" in repr(project)

print(f"OK: Project criado/manipulado em memoria sem pygame (formato={PROJECT_FORMAT!r})")
