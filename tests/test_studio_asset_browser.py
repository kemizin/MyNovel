# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_asset_browser.py
#
# Studio Update, Waystone 6: painel ASSETS -- assets agrupados por
# categoria (Characters/Backgrounds/Music/Voices/SFX), thumbnail sob
# demanda (lazy) pra imagens, áudio mostrado como nome/tipo sem tocar.
#
# Usa tkinter DE VERDADE com root.withdraw() -- nunca aparece nada na
# tela.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk

from src.MyNovellib.studio.app import StudioApp
from src.MyNovellib.project.assets import Asset

root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

# --- a sidebar tem as duas abas pedidas ---
abas = [app.sidebar.tab(t, "text") for t in app.sidebar.tabs()]
assert abas == ["Project", "Assets"]

# --- antes de carregar: arvore de assets vazia ---
assert app.asset_tree.get_children() == ()

app.load_project("exemples/project_demo/project.mynovel")

# --- as 5 categorias pedidas, na ordem, mesmo as vazias ---
categorias = app.asset_tree.get_children()
assert categorias == (
    "assetcat:character_sprite",
    "assetcat:background",
    "assetcat:music",
    "assetcat:voice",
    "assetcat:sfx",
)
rotulos = [app.asset_tree.item(c, "text") for c in categorias]
assert rotulos == ["Characters", "Backgrounds", "Music", "Voices", "SFX"]

# --- cada asset do Project Demo aparece na categoria certa ---
characters = app.asset_tree.get_children("assetcat:character_sprite")
assert set(app.asset_tree.item(i, "text") for i in characters) == {
    "mika.normal.idle", "mika.normal.talking"
}

backgrounds = app.asset_tree.get_children("assetcat:background")
assert [app.asset_tree.item(i, "text") for i in backgrounds] == ["praca.bg"]

# categorias sem nenhum asset ficam vazias (nada fake preenchido)
assert app.asset_tree.get_children("assetcat:music") == ()
assert app.asset_tree.get_children("assetcat:voice") == ()
assert app.asset_tree.get_children("assetcat:sfx") == ()

# --- lazy loading: so populei a arvore, nenhuma imagem foi carregada
# ainda (nada selecionado) ---
assert app.properties_image_label.cget("image") == ""

# --- selecionar uma categoria mostra a contagem ---
app.asset_tree.selection_set("assetcat:character_sprite")
app._on_asset_tree_select()
assert app.properties_label.cget("text") == "Characters: 2"
assert app.properties_image_label.cget("image") == ""  # categoria nao tem thumbnail

# --- selecionar um asset de imagem CARREGA a thumbnail agora (sob
# demanda -- so quando selecionado) ---
app.asset_tree.selection_set("asset:mika.normal.idle")
app._on_asset_tree_select()

texto = app.properties_label.cget("text")
assert "mika.normal.idle" in texto
assert "character_sprite" in texto

thumbnail = app.properties_image_label.image
assert thumbnail is not None
# a imagem original (200x400, gerada no Waystone 11 da Project System
# Update) tem que ter sido reduzida pra caber num thumbnail pequeno
assert thumbnail.width() <= 100 and thumbnail.height() <= 100

# --- asset de audio (music/voice/sfx): nome/tipo, sem thumbnail, sem
# tentar tocar nada -- simulado com um Asset fake (o Project Demo nao
# tem audio registrado) ---
app.project.assets["fake.music"] = Asset(
    id="fake.music", type="music", path="assets/music/nao_precisa_existir.mp3"
)
app._refresh_asset_browser()

app.asset_tree.selection_set("asset:fake.music")
app._on_asset_tree_select()

texto = app.properties_label.cget("text")
assert "fake.music" in texto
assert "music" in texto
assert app.properties_image_label.cget("image") == ""  # sem thumbnail pra audio

# --- tipo de asset desconhecido cai numa categoria "Other", nao
# desaparece silenciosamente ---
app.project.assets["fake.other"] = Asset(
    id="fake.other", type="minigame_data", path="assets/x.bin"
)
app._refresh_asset_browser()

assert "assetcat:other" in app.asset_tree.get_children()
outros = app.asset_tree.get_children("assetcat:other")
assert [app.asset_tree.item(i, "text") for i in outros] == ["fake.other"]

app.on_close()

print("OK: Asset Browser agrupa por categoria, thumbnail sob demanda pra imagens, áudio sem tocar")
