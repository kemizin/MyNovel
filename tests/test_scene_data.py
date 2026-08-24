# Teste pequeno, sem dependências externas, sem pygame.
# Roda com: .venv/Scripts/python.exe tests/test_scene_data.py
#
# Project System Update, Waystone 6: SceneData/SceneCharacter, sem
# pygame, e Project.scenes preservando isso num round trip.

import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.project.scene_data import SceneData, SceneCharacter
from src.MyNovellib.project.model import Project

assert "pygame" not in sys.modules

# --- criacao basica ---
campo = SceneData(
    name="campo",
    background="assets/backgrounds/campo.png",
    music="assets/music/campo.mp3",
)
assert campo.name == "campo"
assert campo.background == "assets/backgrounds/campo.png"
assert campo.music == "assets/music/campo.mp3"
assert campo.resolution is None  # herda do Project por padrao
assert campo.characters == []

# --- resolucao propria (sobrescreve a do Project) ---
cena_especial = SceneData(name="cutscene", resolution=(2560, 1440))
assert cena_especial.resolution == (2560, 1440)

# --- add_character (equivalente de dados a Canvas.add_character) ---
campo.add_character("jef", position=1, scale=0.5, emotion="normal")
campo.add_character("ken", position=3, scale=0.6, offset_y=-10)

assert len(campo.characters) == 2
assert isinstance(campo.characters[0], SceneCharacter)
assert campo.characters[0].character == "jef"
assert campo.characters[0].position == 1
assert campo.characters[0].emotion == "normal"
assert campo.characters[1].character == "ken"
assert campo.characters[1].offset_y == -10
assert campo.characters[1].emotion is None  # nao informado

# --- validacao ---
try:
    SceneData(name="")
    assert False, "esperava ValueError para nome vazio"
except ValueError:
    pass

try:
    SceneCharacter(character="", position=1)
    assert False, "esperava ValueError para character vazio"
except ValueError:
    pass

# --- validação (hardening): position/scale inválidos não passam mais
# batido -- sem isso, um valor ruim só quebrava lá na frente, com um
# KeyError cru dentro de engine.py (x_positions[position]) ---
for posicao_invalida in (0, 4, "2", None):
    try:
        SceneCharacter(character="jef", position=posicao_invalida)
        assert False, f"esperava ValueError para position={posicao_invalida!r}"
    except ValueError:
        pass

for escala_invalida in (0, -0.5, -1):
    try:
        SceneCharacter(character="jef", position=1, scale=escala_invalida)
        assert False, f"esperava ValueError para scale={escala_invalida!r}"
    except ValueError:
        pass

try:
    campo.add_character("jef", position=99)
    assert False, "esperava ValueError -- add_character reaproveita a validação de SceneCharacter"
except ValueError:
    pass

# --- to_dict/from_dict/igualdade ---
data = campo.to_dict()
assert data["name"] == "campo"
assert data["resolution"] is None
assert len(data["characters"]) == 2
assert data["characters"][0]["character"] == "jef"

reconstruida = SceneData.from_dict(data)
assert reconstruida == campo

# --- Project.scenes preserva SceneData num round trip ---
tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_scenedata_")
try:
    project = Project(name="Com Cenas")
    project.scenes["campo"] = campo
    project.scenes["cutscene"] = cena_especial

    project_path = os.path.join(tmp_dir, "projeto.mynovel")
    project.save(project_path)

    loaded = Project.load(project_path)

    assert loaded.scenes["campo"] == campo
    assert loaded.scenes["cutscene"] == cena_especial
    assert isinstance(loaded.scenes["campo"], SceneData)
    assert loaded.scenes["campo"].characters[0].character == "jef"

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

# --- SceneData nao tem NADA de Runtime (sem screen/background
# carregado, sem draw, sem pygame.Surface) ---
assert not hasattr(campo, "screen")
assert not hasattr(campo, "draw")
assert not hasattr(campo, "tamanho")  # esse e o campo do Canvas de Runtime

print("OK: SceneData/SceneCharacter e Project.scenes funcionam, separados do Canvas de Runtime")
