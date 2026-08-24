# Ponto de entrada do MyNovel Studio (editor visual desktop, Tkinter).
#
# Rodar com:
#     .venv/Scripts/python.exe studio.py

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from src.MyNovellib.studio.app import StudioApp


def main():
    app = StudioApp()
    app.run()


if __name__ == "__main__":
    main()
