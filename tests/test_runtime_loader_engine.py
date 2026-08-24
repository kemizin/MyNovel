# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_runtime_loader_engine.py
#
# Project System Update, Waystone 9: prova a arquitetura completa,
# com assets reais deste repositorio, rodando pela Engine de verdade:
#
#     Project.save() -> Project.load() -> create_runtime() -> run()
#
# Nenhuma Engine paralela -- runtime.engine e uma Engine de verdade
# (src/MyNovellib/engine.py), so alimentada por dados em vez de
# codigo Python escrito a mao.
#
# Roda headless (SDL_VIDEODRIVER=dummy).

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from src.MyNovellib.project.model import Project
from src.MyNovellib.project.character_data import CharacterData
from src.MyNovellib.project.scene_data import SceneData
from src.MyNovellib.project.story_data import StoryData
from src.MyNovellib.engine import Engine

# --- monta um projeto em memoria, usando os assets REAIS do repo
# (caminhos relativos a REPO_ROOT, os mesmos que main.py/exemples ja
# usam) ---
project = Project(name="Projeto Runtime Loading", resolution=(800, 600))

jef_data = CharacterData("Jef")
jef_data.add_emotion(
    "normal",
    idle="assets/char/jefer/jefer.png",
    talking="assets/char/jefer/jefer_falano.png"
)
jef_data.add_emotion("bravo", idle="assets/char/jefer/jefer_soco.png")
project.characters["jef"] = jef_data

ken_data = CharacterData("Ken")
ken_data.add_emotion(
    "normal",
    idle="assets/char/ken/ken.png",
    talking="assets/char/ken/ken_falando.png"
)
project.characters["ken"] = ken_data

campo_data = SceneData(name="campo", background="assets/fundos/campo.jpg")
campo_data.add_character("ken", position=3, scale=0.5, emotion="normal")
project.scenes["campo"] = campo_data

intro = StoryData(name="intro")
intro.add_action("speak", character="ken", text="Tem alguém aí?", speed=0.005, delay=0.02)
intro.add_action("enter", character="jef", position=1, scale=0.5)
intro.add_action("emotion", character="jef", emotion="bravo")
intro.add_action("speak", character="jef", text="EU ESTOU AQUI!", speed=0.005, delay=0.02)
intro.add_action("move", character="jef", position=2)
intro.add_action("pause", duration=0.1)
intro.add_action("exit", character="jef")
project.stories["intro"] = intro

# --- carregar arquivos: salva e recarrega de verdade ---
tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_runtime_")
try:
    project_path = os.path.join(tmp_dir, "projeto.mynovel")
    project.save(project_path)

    loaded = Project.load(project_path)
    assert loaded.loaded_from == tmp_dir

    # o .mynovel foi salvo numa pasta temporaria (sem os assets --
    # esses continuam no repo). Um projeto de verdade normalmente tem
    # os assets do lado do project.mynovel (ver Waystone 11); aqui
    # apontamos create_runtime() pra raiz do repo, onde os caminhos
    # relativos guardados realmente existem.
    runtime = loaded.create_runtime(directory=REPO_ROOT)

    assert set(runtime.characters) == {"jef", "ken"}
    assert set(runtime.scenes) == {"campo"}
    assert set(runtime.stories) == {"intro"}
    assert isinstance(runtime.engine, Engine)

    # jef ainda nao esta na cena (so entra via Action "enter" na story)
    assert "Jef" not in runtime.scenes["campo"].characters
    assert "Ken" in runtime.scenes["campo"].characters

    # roda pela Engine de verdade -- sem informar scene/story
    # explicitamente, porque so ha uma de cada
    runtime.run()

    jef = runtime.characters["jef"]
    campo = runtime.scenes["campo"]

    assert jef.current_emotion == "bravo"
    assert "Jef" not in campo.characters  # saiu no final (Action "exit")
    assert "Ken" in campo.characters      # nunca saiu

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print("OK: Project.load() -> create_runtime() -> run() executa uma historia completa com assets reais, pela Engine existente")
