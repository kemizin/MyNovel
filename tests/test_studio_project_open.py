# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_project_open.py
#
# Studio Update, Waystone 2: File -> Open Project carrega um
# project.mynovel de verdade (Project.load() já existente, sem
# duplicar) e atualiza a interface.
#
# Usa tkinter DE VERDADE com root.withdraw() -- nunca aparece nada na
# tela.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import tkinter.messagebox as messagebox

from src.MyNovellib.studio.app import StudioApp, APP_TITLE

root = tk.Tk()
root.withdraw()
app = StudioApp(root=root)

# --- antes de carregar: nenhum projeto, placeholder visivel ---
assert app.project is None
assert app.root.title() == APP_TITLE

# --- carregar o Project Demo real (criado na Project System Update) ---
# load_project() e chamado direto, sem passar pelo file dialog --
# open_project() so ficaria responsavel por perguntar o caminho.
app.load_project("exemples/project_demo/project.mynovel")

assert app.project is not None
assert app.project.name == "Project Demo"

# --- titulo e status bar atualizados ---
assert app.root.title() == f"{APP_TITLE} — Project Demo"
assert "Project Demo" in app.status_bar.cget("text")

# --- area principal mostra nome, resolucao, cenas e quantidade de assets ---
main_area_text = ""
for widget in app.main_area.winfo_children():
    if isinstance(widget, tk.Label):
        main_area_text += widget.cget("text")

assert "Project Demo" in main_area_text
assert "960" in main_area_text and "540" in main_area_text
assert "praca" in main_area_text  # nome da cena
assert "3" in main_area_text      # quantidade de assets (registrados no demo)

# --- caminho invalido: nao derruba a aplicacao, mostra erro (sem
# abrir um dialog de verdade -- messagebox.showerror e substituido por
# um espiao que so registra a chamada) ---
erros_mostrados = []
original_showerror = messagebox.showerror
messagebox.showerror = lambda titulo, msg: erros_mostrados.append((titulo, msg))

try:
    app.load_project("caminho/que/nao/existe.mynovel")
finally:
    messagebox.showerror = original_showerror

assert len(erros_mostrados) == 1
assert erros_mostrados[0][0] == APP_TITLE

# o projeto anterior continua carregado -- um erro ao abrir outro
# projeto nao apaga o que ja estava aberto
assert app.project.name == "Project Demo"

app.on_close()

print("OK: File -> Open Project carrega o Project Demo real e atualiza a interface (Project.load() reaproveitado, sem duplicar)")
