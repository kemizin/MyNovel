# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_runtime_loader.py
#
# Project System Update, Waystone 9: resolução de caminhos e
# construção de Character/Canvas (Runtime) a partir de dados de
# projeto. A parte de resolução de path não precisa de pygame; a
# construção de Canvas/Character também não (só quando a Engine
# de fato roda é que pygame entra -- ver test_runtime_loader_engine.py).

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.project.character_data import CharacterData
from src.MyNovellib.project.scene_data import SceneData
from src.MyNovellib.project.model import Project
from src.MyNovellib.project.runtime_loader import (
    _resolve_path, _build_character, _build_canvas, _only_key_or_raise,
    ProjectRuntime,
)

# --- _resolve_path: relativo junta com base_dir; absoluto/None passam direto ---
assert _resolve_path("/projeto", "assets/jef.png") == os.path.join("/projeto", "assets/jef.png")
assert _resolve_path("/projeto", None) is None

abs_path = os.path.abspath("C:/em/outro/lugar/jef.png" if os.name == "nt" else "/em/outro/lugar/jef.png")
assert _resolve_path("/projeto", abs_path) == abs_path

# --- _build_character: CharacterData -> Character (Runtime), paths resolvidos ---
jef_data = CharacterData("Jef")
jef_data.add_emotion("normal", idle="assets/jef_idle.png", talking="assets/jef_talk.png")
jef_data.add_emotion("bravo", idle="assets/jef_soco.png")

jef = _build_character(jef_data, base_dir="/meu_projeto")

assert jef.nome == "Jef"
assert jef.emotions["normal"]["idle"] == os.path.join("/meu_projeto", "assets/jef_idle.png")
assert jef.emotions["normal"]["talking"] == os.path.join("/meu_projeto", "assets/jef_talk.png")
assert jef.emotions["bravo"]["talking"] is None

# --- _build_canvas: SceneData -> Canvas (Runtime), personagens aplicados ---
scene_data = SceneData(name="campo", background="fundos/campo.jpg", music="musica/campo.mp3")
scene_data.add_character("jef", position=1, scale=0.5, emotion="bravo")

canvas = _build_canvas(scene_data, project_resolution=(1920, 1080), characters={"jef": jef}, base_dir="/meu_projeto")

assert canvas.nome == "campo"
assert canvas.imagem == os.path.join("/meu_projeto", "fundos/campo.jpg")
assert canvas.music == os.path.join("/meu_projeto", "musica/campo.mp3")
assert canvas.tamanho == (1920, 1080)  # herdou do project (scene_data.resolution era None)
assert "Jef" in canvas.characters
assert jef.current_emotion == "bravo"  # emotion inicial ja aplicada

# --- resolution propria da cena sobrescreve a do project ---
scene_hd = SceneData(name="cutscene", resolution=(2560, 1440))
canvas_hd = _build_canvas(scene_hd, project_resolution=(1920, 1080), characters={}, base_dir="/x")
assert canvas_hd.tamanho == (2560, 1440)

# --- _only_key_or_raise ---
assert _only_key_or_raise({"unica": 1}, "cena") == "unica"

try:
    _only_key_or_raise({}, "cena")
    assert False, "esperava ValueError pra dict vazio"
except ValueError:
    pass

try:
    _only_key_or_raise({"a": 1, "b": 2}, "cena")
    assert False, "esperava ValueError pra mais de uma opcao sem escolha explicita"
except ValueError:
    pass

# --- ProjectRuntime monta characters/scenes/stories a partir do Project ---
project = Project(name="Projeto de Teste")
project.characters["jef"] = jef_data
project.scenes["campo"] = scene_data

runtime = ProjectRuntime(project, directory="/meu_projeto")

assert set(runtime.characters) == {"jef"}
assert set(runtime.scenes) == {"campo"}
assert runtime.stories == {}  # nenhuma story registrada neste projeto
assert runtime.characters["jef"].nome == "Jef"
assert runtime.scenes["campo"].imagem == os.path.join("/meu_projeto", "fundos/campo.jpg")

# a Engine existente e reaproveitada, nao uma nova
from src.MyNovellib.engine import Engine
assert isinstance(runtime.engine, Engine)

print("OK: resolucao de paths e construcao de Character/Canvas a partir de dados de projeto")
