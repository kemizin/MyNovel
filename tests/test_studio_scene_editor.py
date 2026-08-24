# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_scene_editor.py
#
# Studio Update, Waystone 8: Scene Editor -- canvas visual (background
# + personagens), seleção por clique, edição numérica de Position/
# Scale/Offset X/Offset Y + Emotion. Edita SceneData/SceneCharacter,
# nunca o Canvas de Runtime.
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
from tkinter import ttk
import tkinter.messagebox as messagebox

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

    project = Project(name="Projeto Cena", resolution=(960, 540))

    mika = CharacterData("Mika")
    mika.add_emotion("normal", idle="assets/backgrounds/praca.png")  # reusa um PNG real qualquer
    mika.add_emotion("feliz", idle="assets/backgrounds/praca.png")
    project.characters["mika"] = mika

    cena = SceneData(name="praca", background="assets/backgrounds/praca.png")
    cena.add_character("mika", position=1, scale=0.5, emotion="normal")
    project.scenes["praca"] = cena

    return project


root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)
app.project = build_project()
app.project.loaded_from = "exemples/project_demo"  # onde praca.png de fato existe
app._on_project_loaded()

# --- selecionar a cena mostra o canvas, do tamanho certo (960/2=480,
# 540/2=270 -- fator de reducao 2 pro preview) ---
app.explorer.selection_set("scene:praca")
app._on_explorer_select()

assert isinstance(app.scene_canvas, tk.Canvas)
assert int(app.scene_canvas["width"]) == 480
assert int(app.scene_canvas["height"]) == 270
assert app.scene_preview_factor == 2

# background foi desenhado (pelo menos 1 item no canvas)
assert len(app.scene_canvas.find_all()) >= 1

# --- antes de selecionar um personagem: painel Properties mostra o
# placeholder ---
assert app.scene_selected_index is None
placeholder = app.scene_properties_frame.winfo_children()[0]
assert "Clique" in placeholder.cget("text")

# --- clicar no personagem seleciona (simulado via coordenadas reais
# calculadas no proprio render, sem precisar de mouse de verdade) ---
x, y, w, h = app._scene_item_bounds[0]
evento = FakeEvent(app.scene_canvas, x + w // 2, y + h // 2)
app._on_scene_canvas_press(evento)

assert app.scene_selected_index == 0

# --- painel Properties mostra os campos certos pro personagem
# selecionado ---
def find_widgets(parent, cls):
    achados = []
    for w in parent.winfo_children():
        if isinstance(w, cls):
            achados.append(w)
        achados.extend(find_widgets(w, cls))
    return achados


labels = [w.cget("text") for w in find_widgets(app.scene_properties_frame, tk.Label)]
assert any("mika" in l for l in labels)

# tk.Entry exato (nao ttk.Combobox, que -- surpreendentemente --
# tambem e um tk.Entry por heranca multipla em ttk.Entry(Widget,
# tkinter.Entry); Combobox e conferido separado, mais abaixo)
entries = [w for w in find_widgets(app.scene_properties_frame, tk.Entry) if type(w) is tk.Entry]
assert [e.get() for e in entries] == ["1", "0.5", "0", "0"]  # Position, Scale, Offset X, Offset Y

placement = app.project.scenes["praca"].characters[0]

# --- clicar fora de qualquer personagem desseleciona ---
app._on_scene_canvas_press(FakeEvent(app.scene_canvas, 5, 5))
assert app.scene_selected_index is None

# reseleciona pra continuar testando os campos
app._on_scene_canvas_press(FakeEvent(app.scene_canvas, x + w // 2, y + h // 2))
assert app.scene_selected_index == 0

# --- editar Position aplica de verdade (via _apply_scene_field,
# direto -- equivalente ao <Return>/<FocusOut> do Entry) ---
app.dirty = False
app._apply_scene_field(0, "position", "3", int)
assert placement.position == 3
assert app.dirty is True

# --- Position invalido (fora de 1/2/3) mostra erro e nao aplica ---
erros = []
original_showerror = messagebox.showerror
messagebox.showerror = lambda titulo, msg: erros.append(msg)

try:
    app._apply_scene_field(0, "position", "5", int)
    app._apply_scene_field(0, "position", "abc", int)
    app._apply_scene_field(0, "scale", "0", float)
    app._apply_scene_field(0, "scale", "-1", float)
finally:
    messagebox.showerror = original_showerror

assert len(erros) == 4
assert placement.position == 3  # nao mudou com os valores invalidos

# --- Offset X/Y aceitam inteiros normalmente ---
app._apply_scene_field(0, "offset_x", "15", int)
app._apply_scene_field(0, "offset_y", "-8", int)
assert placement.offset_x == 15
assert placement.offset_y == -8

# --- Emotion: so lista emocoes cadastradas pro personagem ---
app._render_scene_properties()
combos = find_widgets(app.scene_properties_frame, ttk.Combobox)
assert len(combos) == 1
assert set(combos[0].cget("values")) == {"normal", "feliz"}

combos[0].set("feliz")
combos[0].event_generate("<<ComboboxSelected>>")
assert placement.emotion == "feliz"

# --- Canvas de Runtime nunca importado ---
assert "src.MyNovellib.scene" not in sys.modules

app.dirty = False
app.on_close()

# =================================================================
# Persistencia: Studio edita SceneData -> Save -> Project.load()
# direto confirma.
# =================================================================

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_sceneeditor_")
try:
    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)
    app2.project = build_project()
    app2.project_path = os.path.join(tmp_dir, "projeto.mynovel")
    app2.project.loaded_from = tmp_dir
    app2._on_project_loaded()

    app2.explorer.selection_set("scene:praca")
    app2._on_explorer_select()

    cena2 = app2.project.scenes["praca"]
    app2._apply_scene_field(0, "position", "2", int)
    app2._apply_scene_field(0, "scale", "0.9", float)

    app2.save_project()
    app2.on_close()

    reloaded = Project.load(app2.project_path)
    placement_recarregado = reloaded.scenes["praca"].characters[0]
    assert placement_recarregado.position == 2
    assert placement_recarregado.scale == 0.9

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print("OK: Scene Editor mostra/seleciona/edita personagens na cena (SceneData), persiste via Save")
