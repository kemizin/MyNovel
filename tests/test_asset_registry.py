# Teste pequeno, sem dependências externas, sem pygame.
# Roda com: .venv/Scripts/python.exe tests/test_asset_registry.py
#
# Project System Update, Waystone 4: Asset (so metadados) e
# Project.add_asset()/remove_asset()/get_asset().

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.project.model import Project
from src.MyNovellib.project.assets import Asset, ASSET_TYPES

assert "pygame" not in sys.modules

# --- Asset e so metadados ---
asset = Asset(
    id="jef.normal.idle",
    type="character_sprite",
    path="assets/characters/jef/normal_idle.png"
)
assert asset.id == "jef.normal.idle"
assert asset.type == "character_sprite"
assert asset.path == "assets/characters/jef/normal_idle.png"
assert asset.type in ASSET_TYPES

# --- validacao basica ---
try:
    Asset(id="", type="background", path="x.png")
    assert False, "esperava ValueError para id vazio"
except ValueError:
    pass

try:
    Asset(id="x", type="background", path="")
    assert False, "esperava ValueError para path vazio"
except ValueError:
    pass

# --- to_dict/from_dict/igualdade ---
data = asset.to_dict()
assert data == {
    "id": "jef.normal.idle",
    "type": "character_sprite",
    "path": "assets/characters/jef/normal_idle.png",
}
assert Asset.from_dict(data) == asset

# --- Project.add_asset/get_asset/remove_asset ---
project = Project(name="Meu Jogo")

bg = Asset(id="campo.bg", type="background", path="assets/backgrounds/campo.jpg")
music = Asset(id="campo.music", type="music", path="assets/music/campo.mp3")

project.add_asset(bg)
project.add_asset(music)

assert project.get_asset("campo.bg") is bg
assert project.get_asset("campo.music") is music
assert len(project.assets) == 2

# add_asset com o mesmo id sobrescreve (mesma semantica de um dict)
novo_bg = Asset(id="campo.bg", type="background", path="assets/backgrounds/campo_v2.jpg")
project.add_asset(novo_bg)
assert project.get_asset("campo.bg") is novo_bg
assert len(project.assets) == 2  # nao duplicou

project.remove_asset("campo.music")
assert len(project.assets) == 1
assert "campo.music" not in project.assets

# --- get/remove de asset inexistente falha claro ---
try:
    project.get_asset("nao_existe")
    assert False, "esperava KeyError"
except KeyError:
    pass

try:
    project.remove_asset("nao_existe")
    assert False, "esperava KeyError"
except KeyError:
    pass

# --- Project NAO carrega o arquivo de verdade -- so guarda o path ---
# (nao existe metodo nenhum de "load"/"open" em Asset -- so o registro)
assert not hasattr(asset, "load")
assert not hasattr(asset, "surface")

print("OK: Asset e Project.add_asset/remove_asset/get_asset funcionam (so metadados)")
