# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_demo.py
#
# Studio Update, Waystone 12: prova, de ponta a ponta, que o fluxo
# inteiro do Studio funciona sobre um projeto real e comitado
# (exemples/studio_demo/) -- não um projeto inventado só pro teste:
#
#     Open Project -> Project Explorer -> Character Editor ->
#     Scene Editor -> Save -> Play
#
# O projeto em si (exemples/studio_demo/) é pequeno de propósito --
# 1 personagem, 1 cena, 2 falas -- o objetivo é demonstrar o FLUXO
# completo do Studio, não uma história longa.
#
# Este teste trabalha numa CÓPIA temporária do projeto (nunca escreve
# em exemples/studio_demo/) -- assim o projeto comitado continua
# sempre no estado "recém aberto", pronto pra quem quiser abrir de
# verdade no Studio (python studio.py) e seguir o mesmo fluxo na mão.
#
# Usa tkinter DE VERDADE com root.withdraw() e SDL_VIDEODRIVER=dummy
# -- nunca aparece nada na tela.

import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import sys
import shutil
import tempfile
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.studio.app import StudioApp, APP_TITLE
from src.MyNovellib.project.model import Project

DEMO_SOURCE = os.path.join("exemples", "studio_demo")

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_studiodemo_")
try:
    demo_copy = os.path.join(tmp_dir, "studio_demo")
    shutil.copytree(DEMO_SOURCE, demo_copy)
    project_path = os.path.join(demo_copy, "project.mynovel")

    root = tk.Tk()
    root.withdraw()
    app = StudioApp(root=root)

    # --- 1) Open Project: carrega o projeto real do exemplo comitado ---
    app.load_project(project_path)

    assert app.project.name == "Studio Demo"
    assert app.root.title() == f"{APP_TITLE} — Studio Demo"
    assert app.dirty is False

    # --- 2) Project Explorer: personagem, cena e história aparecem ---
    filhos_raiz = app.explorer.get_children("")
    assert len(filhos_raiz) == 1  # um único nó "project"
    categorias = {
        app.explorer.item(c, "text"): c
        for c in app.explorer.get_children(filhos_raiz[0])
    }
    assert set(categorias) == {"Characters", "Scenes", "Stories", "Assets"}

    personagens = app.explorer.get_children(categorias["Characters"])
    cenas = app.explorer.get_children(categorias["Scenes"])
    assert personagens == ("character:mika",)
    assert cenas == ("scene:praca",)

    # --- 3) Character Editor: edição real (adicionar emoção) chega
    # no dirty/título, exatamente como um artista faria na mão ---
    app.explorer.selection_set("character:mika")
    app._on_explorer_select()

    assert app.dirty is False  # só abrir o editor ainda não é edição

    app.add_emotion(
        "mika", "feliz", idle="assets/backgrounds/praca.png"
    )  # reaproveita um asset já existente só pra ter um segundo sprite

    assert "feliz" in app.project.characters["mika"].emotions
    assert app.dirty is True
    assert app.root.title() == f"{APP_TITLE} — Studio Demo *"

    # --- 4) Scene Editor: edição real (ajustar a posição de mika na
    # cena "praca") também chega no dirty/título ---
    app.explorer.selection_set("scene:praca")
    app._on_explorer_select()

    placement = app.project.scenes["praca"].characters[0]
    escala_original = placement.scale

    app._apply_scene_field(0, "scale", "0.7", float)

    assert placement.scale == 0.7
    assert placement.scale != escala_original
    assert app.dirty is True

    # --- 5) Save: persiste as duas edições no arquivo ---
    app.save_project()

    assert app.dirty is False
    assert app.root.title() == f"{APP_TITLE} — Studio Demo"

    app.on_close()

    # Reabre do zero (nova instância, carregando do disco) -- confirma
    # que as edições feitas pelos editores realmente persistiram.
    root2 = tk.Tk()
    root2.withdraw()
    app2 = StudioApp(root=root2)
    app2.load_project(project_path)

    assert "feliz" in app2.project.characters["mika"].emotions
    assert app2.project.scenes["praca"].characters[0].scale == 0.7

    # confere também direto pelo Project System, sem passar pelo Studio
    reloaded = Project.load(project_path)
    assert "feliz" in reloaded.characters["mika"].emotions
    assert reloaded.scenes["praca"].characters[0].scale == 0.7

    # --- 6) Play: roda o projeto (já editado) pela Engine existente ---
    # As falas do demo esperam um input real do jogador pra avançar
    # (assim é uma VN de verdade quando alguém abre o Studio na mão).
    # Só pra este teste conseguir terminar sozinho, sem simular
    # eventos de teclado/mouse, ajusta delay/speed das falas -- mesma
    # técnica do test_studio_play.py. Isso muda só a cópia em memória
    # deste teste, nunca o projeto comitado.
    for acao in app2.project.stories["intro"].actions:
        if acao.type == "speak":
            acao.fields["speed"] = 0.005
            acao.fields["delay"] = 0.02

    app2.play_project()

    assert app2.root.winfo_exists()  # Studio continua aberto depois
    assert "de volta ao Studio" in app2.status_bar.cget("text")

    app2.on_close()

    print(
        "OK: fluxo completo do Studio Demo -- Open Project -> Explorer -> "
        "Character Editor -> Scene Editor -> Save -> Play -- sobre o "
        "projeto real em exemples/studio_demo/"
    )

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)
