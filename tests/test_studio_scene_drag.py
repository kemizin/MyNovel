# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_scene_drag.py
#
# Studio Update, Waystone 9: arrastar um personagem no Scene Editor
# ajusta offset_x/offset_y em tempo real (SceneData -- nunca o Canvas
# de Runtime), e a posição persiste entre sessões.
#
# Usa tkinter DE VERDADE com root.withdraw() -- nunca aparece nada na
# tela.

import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk

from src.MyNovellib.studio.app import StudioApp
from src.MyNovellib.project.model import Project
from src.MyNovellib.project.character_data import CharacterData
from src.MyNovellib.project.scene_data import SceneData


class FakeEvent:
    def __init__(self, widget, x, y):
        self.widget = widget
        self.x = x
        self.y = y


def build_project():

    project = Project(name="Projeto Drag", resolution=(960, 540))

    mika = CharacterData("Mika")
    mika.add_emotion("normal", idle="assets/backgrounds/praca.png")
    project.characters["mika"] = mika

    cena = SceneData(name="praca", background="assets/backgrounds/praca.png")
    cena.add_character("mika", position=2, scale=0.5)
    project.scenes["praca"] = cena

    return project


root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)
app.project = build_project()
app.project.loaded_from = "exemples/project_demo"
app._on_project_loaded()

app.explorer.selection_set("scene:praca")
app._on_explorer_select()

placement = app.project.scenes["praca"].characters[0]
assert placement.offset_x == 0 and placement.offset_y == 0

x, y, w, h = app._scene_item_bounds[0]
centro_x, centro_y = x + w // 2, y + h // 2

# --- pressionar sobre o personagem seleciona e comeca o arraste ---
app.dirty = False
app._on_scene_canvas_press(FakeEvent(app.scene_canvas, centro_x, centro_y))

assert app.scene_selected_index == 0
assert app._scene_drag is not None
assert app._scene_drag["index"] == 0
assert app.dirty is False  # so selecionar/pressionar ainda nao marca dirty

# --- arrastar move de verdade -- offset_x/offset_y acompanham o
# movimento do mouse, multiplicados pelo fator de reducao do preview
# (2, nesta cena) ---
factor = app.scene_preview_factor
assert factor == 2

app._on_scene_canvas_drag(FakeEvent(app.scene_canvas, centro_x + 10, centro_y + 4))

assert placement.offset_x == 10 * factor
assert placement.offset_y == 4 * factor
assert app.dirty is True

# continuar arrastando atualiza de novo, a partir do offset ORIGINAL
# do inicio do arraste (nao acumula erro a cada evento de movimento)
app._on_scene_canvas_drag(FakeEvent(app.scene_canvas, centro_x - 5, centro_y + 20))

assert placement.offset_x == -5 * factor
assert placement.offset_y == 20 * factor

# --- soltar o botao termina o arraste (nao muda mais nada depois) ---
app._on_scene_canvas_release(FakeEvent(app.scene_canvas, centro_x - 5, centro_y + 20))
assert app._scene_drag is None

offset_final_x = placement.offset_x
offset_final_y = placement.offset_y

# --- clicar em outro lugar (fora do personagem) sem estar arrastando
# so desseleciona, nao mexe no offset ---
app._on_scene_canvas_press(FakeEvent(app.scene_canvas, 2, 2))
assert app.scene_selected_index is None
assert placement.offset_x == offset_final_x
assert placement.offset_y == offset_final_y

app.dirty = False
app.on_close()

# =================================================================
# Persistencia pedida explicitamente: mover -> salvar -> fechar ->
# reabrir -> posicao continua correta.
# =================================================================

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_scenedrag_")
try:
    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)
    app2.project = build_project()
    # loaded_from aponta pra onde os assets (praca.png) existem de
    # verdade -- precisa disso pro preview conseguir desenhar o
    # personagem e calcular _scene_item_bounds (sem isso nao daria
    # pra simular o arraste). O project.mynovel em si vai ser salvo
    # num lugar diferente (tmp_dir) -- ver save_project() abaixo.
    app2.project.loaded_from = "exemples/project_demo"
    app2._on_project_loaded()

    app2.explorer.selection_set("scene:praca")
    app2._on_explorer_select()

    x2, y2, w2, h2 = app2._scene_item_bounds[0]
    centro2 = (x2 + w2 // 2, y2 + h2 // 2)

    app2._on_scene_canvas_press(FakeEvent(app2.scene_canvas, *centro2))
    app2._on_scene_canvas_drag(FakeEvent(app2.scene_canvas, centro2[0] + 30, centro2[1] - 12))
    app2._on_scene_canvas_release(FakeEvent(app2.scene_canvas, centro2[0] + 30, centro2[1] - 12))

    placement2 = app2.project.scenes["praca"].characters[0]
    offset_x_movido = placement2.offset_x
    offset_y_movido = placement2.offset_y

    # agora sim: redireciona pra onde o projeto vai ser salvo de fato
    app2.project_path = os.path.join(tmp_dir, "projeto.mynovel")
    assert offset_x_movido != 0 or offset_y_movido != 0

    app2.save_project()
    app2.on_close()

    # "fecha" e "reabre": nova instancia do zero, carregando do disco
    root3 = tk.Tk()
    root3.withdraw()
    app3 = StudioApp(root=root3)
    app3.load_project(app2.project_path)

    placement3 = app3.project.scenes["praca"].characters[0]
    assert placement3.offset_x == offset_x_movido
    assert placement3.offset_y == offset_y_movido

    app3.on_close()

    # confere tambem direto pelo Project System, sem passar pelo Studio
    reloaded = Project.load(app2.project_path)
    assert reloaded.scenes["praca"].characters[0].offset_x == offset_x_movido
    assert reloaded.scenes["praca"].characters[0].offset_y == offset_y_movido

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print("OK: arrastar personagem na cena ajusta offset_x/offset_y (SceneData), e a posição persiste entre sessões")
