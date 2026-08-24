# Teste pequeno, sem dependências externas.
# Roda com: .venv/Scripts/python.exe tests/test_studio_shell.py
#
# Studio Update, Waystone 1: o shell (janela, menu, toolbar, área
# principal, status bar) abre e fecha sem exceção, com a estrutura de
# menu pedida.
#
# Usa tkinter DE VERDADE (não é mock) mas com root.withdraw() logo
# após criar a janela -- nunca aparece nada na tela, mesmo espírito do
# SDL_VIDEODRIVER=dummy usado nos testes de pygame.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk

from src.MyNovellib.studio.app import StudioApp, APP_TITLE

_TclError = tk.TclError


def menu_entries(menu):
    """Lista (label, state) de cada item de um tk.Menu, pulando separadores."""

    entries = []

    last = menu.index("end")
    if last is None:
        return entries

    for i in range(last + 1):
        if menu.type(i) == "separator":
            continue
        entries.append((menu.entrycget(i, "label"), str(menu.entrycget(i, "state"))))

    return entries


root = tk.Tk()
root.withdraw()  # nunca fica visível

# --- abrir: construir o shell nao levanta excecao ---
app = StudioApp(root=root)

assert app.root.title() == APP_TITLE

# --- estrutura basica presente: menu, toolbar, area principal, status bar ---
assert isinstance(app.menubar, tk.Menu)
assert isinstance(app.toolbar, tk.Frame)
assert isinstance(app.main_area, tk.Frame)
assert isinstance(app.status_bar, tk.Label)
assert app.status_bar.cget("text") == "Pronto."

# --- os 5 menus pedidos, na ordem certa ---
assert list(app.menus) == ["File", "Edit", "Scene", "Build", "Help"]

# --- File: os itens pedidos, na ordem, com os ainda-nao-implementados
# desabilitados e Exit habilitado ---
file_entries = menu_entries(app.menus["File"])
labels = [label for label, _ in file_entries]
assert labels == ["New Project...", "Open Project...", "Save", "Save As...", "Exit"]

estados = dict(file_entries)
for rotulo_desabilitado in ("Save", "Save As..."):
    assert estados[rotulo_desabilitado] == "disabled", rotulo_desabilitado

# New Project, Open Project e Exit ja sao reais (Waystones 4, 2 e 1)
assert estados["New Project..."] == "normal"
assert estados["Open Project..."] == "normal"
assert estados["Exit"] == "normal"

# --- Edit tem "New Character..." (Hardening), desabilitado ate abrir
# um projeto -- Scene continua sem itens (nada fake) ---
assert menu_entries(app.menus["Edit"]) == [("New Character...", "disabled")]
assert menu_entries(app.menus["Scene"]) == []

# --- Build tem "Play" (Waystone 10), desabilitado ate abrir um projeto ---
assert menu_entries(app.menus["Build"]) == [("Play", "disabled")]

# --- Help tem "About", habilitado ---
help_entries = menu_entries(app.menus["Help"])
assert help_entries == [("About MyNovel Studio", "normal")]

# --- toolbar: Save/Play ainda desabilitados, New/Open ja funcionam ---
assert set(app.toolbar_buttons) == {"New", "Open", "Save", "Play"}
assert str(app.toolbar_buttons["Save"].cget("state")) == "disabled"
assert str(app.toolbar_buttons["Play"].cget("state")) == "disabled"
assert str(app.toolbar_buttons["New"].cget("state")) == "normal"
assert str(app.toolbar_buttons["Open"].cget("state")) == "normal"

# --- fechar: on_close() destroi a janela sem excecao ---
assert app.root.winfo_exists()
app.on_close()

# depois de destroy(), o interpretador Tcl inteiro se vai -- qualquer
# comando (inclusive winfo_exists) levanta TclError. E o jeito mais
# definitivo de confirmar que a janela realmente fechou.
try:
    app.root.winfo_exists()
    assert False, "esperava TclError apos destroy() -- janela nao fechou de verdade"
except _TclError:
    pass

print("OK: shell do Studio abre (menu/toolbar/area principal/status bar) e fecha sem exceção")
