# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_project_round_trip.py
#
# Project System Update, Waystone 10: round trip completo.
#
#     criar projeto em memória -> salvar -> carregar -> criar runtime -> executar
#
# Cobre explicitamente cada categoria pedida: personagem, emoção,
# cena, background, story, actions, assets -- e usa assets REAIS
# deste repositório na execução final.
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
from src.MyNovellib.project.assets import Asset

# =====================================================================
# 1. Criar o projeto em memória -- um pouco de cada categoria.
# =====================================================================

project = Project(name="Round Trip Demo", resolution=(800, 600))

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

campo = SceneData(
    name="campo",
    background="assets/fundos/campo.jpg",
    music="assets/music/ambiente_2.mp3"
)
campo.add_character("ken", position=3, scale=0.5, emotion="normal")
project.scenes["campo"] = campo

project.add_asset(Asset(id="campo.bg", type="background", path="assets/fundos/campo.jpg"))
project.add_asset(Asset(id="ambiente", type="music", path="assets/music/ambiente_2.mp3"))

intro = StoryData(name="intro")
intro.add_action("speak", character="ken", text="Tem alguém aí?", speed=0.005, delay=0.02)
intro.add_action("enter", character="jef", position=1, scale=0.5)
intro.add_action("emotion", character="jef", emotion="bravo")
intro.add_action("speak", character="jef", text="EU ESTOU AQUI!", speed=0.005, delay=0.02)
intro.add_action("move", character="jef", position=2)
intro.add_action("pause", duration=0.1)
intro.add_action("exit", character="jef")
project.stories["intro"] = intro

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_roundtrip_")

try:
    # =================================================================
    # 2. Salvar / 3. Carregar.
    # =================================================================

    project_path = os.path.join(tmp_dir, "projeto.mynovel")
    project.save(project_path)
    loaded = Project.load(project_path)

    assert loaded.name == "Round Trip Demo"
    assert loaded.resolution == (800, 600)

    # =================================================================
    # 4. O projeto sobreviveu ao round trip -- cada categoria pedida.
    # =================================================================

    # --- personagem ---
    assert set(loaded.characters) == {"jef", "ken"}
    assert loaded.characters["jef"] == jef_data
    assert loaded.characters["jef"].name == "Jef"

    # --- emoção ---
    assert set(loaded.characters["jef"].emotions) == {"normal", "bravo"}
    assert loaded.characters["jef"].emotions["normal"] == {
        "idle": "assets/char/jefer/jefer.png",
        "talking": "assets/char/jefer/jefer_falano.png",
    }
    assert loaded.characters["jef"].emotions["bravo"]["talking"] is None

    # --- cena ---
    assert set(loaded.scenes) == {"campo"}
    assert loaded.scenes["campo"] == campo
    assert loaded.scenes["campo"].characters[0].character == "ken"
    assert loaded.scenes["campo"].characters[0].emotion == "normal"

    # --- background ---
    assert loaded.scenes["campo"].background == "assets/fundos/campo.jpg"

    # --- story ---
    assert set(loaded.stories) == {"intro"}
    assert loaded.stories["intro"] == intro
    assert loaded.stories["intro"].name == "intro"

    # --- actions (tipo e ORDEM preservados -- é a ordem de execução) ---
    tipos = [action.type for action in loaded.stories["intro"].actions]
    assert tipos == ["speak", "enter", "emotion", "speak", "move", "pause", "exit"]
    assert loaded.stories["intro"].actions[2].fields["emotion"] == "bravo"
    assert loaded.stories["intro"].actions[4].fields["position"] == 2

    # --- assets ---
    assert set(loaded.assets) == {"campo.bg", "ambiente"}
    assert loaded.get_asset("campo.bg").type == "background"
    assert loaded.get_asset("campo.bg").path == "assets/fundos/campo.jpg"
    assert loaded.get_asset("ambiente").type == "music"

    # =================================================================
    # 5. Criar runtime e EXECUTAR a história, com assets reais deste
    # repositório (o .mynovel foi salvo numa pasta temporária sem os
    # assets -- por isso apontamos create_runtime() pra raiz do repo,
    # onde os caminhos relativos guardados realmente existem).
    # =================================================================

    runtime = loaded.create_runtime(directory=REPO_ROOT)

    assert set(runtime.characters) == {"jef", "ken"}
    assert set(runtime.scenes) == {"campo"}
    assert set(runtime.stories) == {"intro"}

    jef = runtime.characters["jef"]
    campo_runtime = runtime.scenes["campo"]

    assert "Jef" not in campo_runtime.characters  # so entra durante a historia
    assert "Ken" in campo_runtime.characters

    runtime.run()  # so uma cena e uma historia -- roda sem precisar escolher

    assert jef.current_emotion == "bravo"
    assert "Jef" not in campo_runtime.characters  # saiu no final
    assert "Ken" in campo_runtime.characters       # nunca saiu

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print(
    "OK: round trip completo -- personagem/emoção/cena/background/story/"
    "actions/assets sobrevivem, e a história executa de ponta a ponta com assets reais"
)
