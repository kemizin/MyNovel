# Demonstração completa do MyNovel: usa TODAS as Actions da biblioteca
# em uma única história, para servir de referência rápida.
#
# Roda com: .venv/Scripts/python.exe exemples/00_demo_completa.py
#
# Funções usadas aqui: speak, add_character, enter, emotion, move,
# pause, exit, change_scene (com transição de fade), remove_character.
#
# Para exemplos focados em UMA função de cada vez, veja os outros
# arquivos desta pasta (01_speak.py, 02_emotion.py, ...).

import os
import sys

# Permite rodar este arquivo diretamente de dentro de exemples/,
# sem precisar ajustar o PYTHONPATH manualmente.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import (
    enter,
    exit as sair,          # "exit" conflita com o builtin do Python;
    emotion,                # aqui importamos com outro nome (sair).
    move,
    pause,
    change_scene,
    remove_character,
)


# --- Personagens -----------------------------------------------------

ken = Character("Ken")
ken.add_emotion(
    "normal",
    idle="assets/char/ken/ken.png",
    talking="assets/char/ken/ken_falando.png"
)
ken.emotion("normal")

jef = Character("Jef")
jef.add_emotion(
    "normal",
    idle="assets/char/jefer/jefer.png",
    talking="assets/char/jefer/jefer_falano.png"
)
jef.add_emotion(
    "bravo",
    idle="assets/char/jefer/jefer_soco.png"
)
jef.emotion("normal")


# --- Cenas -------------------------------------------------------------

campo = Canvas(
    "campo",
    "assets/fundos/campo.jpg",
    1920,
    1080
)

quarto = Canvas(
    "quarto",
    "assets/fundos/quarto.jpg",
    1920,
    1080
)

# add_character(): configuração INICIAL da cena, antes da história
# começar. Ken já está no campo desde o primeiro frame.
campo.add_character(ken, position=3, scale=0.5)


# --- História ------------------------------------------------------

story = [

    speak(ken, "Sera que tem alguem no campo comigo?", delay=1.2),

    # enter(): entrada NARRATIVA de um personagem -- acontece durante
    # a história, diferente de add_character() (que é configuração).
    enter(jef, position=1, scale=0.5),

    speak(jef, "Relaxa, sou so eu.", delay=1.2),

    # emotion(): troca a emoção atual do personagem.
    emotion(jef, "bravo"),

    speak(jef, "MAS SE VOCE ME CHAMAR DE FANTASMA DE NOVO...", delay=1.2),

    # move(): reposiciona/reenquadra um personagem já em cena, sem
    # perder o que não foi informado (aqui a emoção "bravo" continua).
    move(jef, position=2, scale=0.7),

    # pause(): segura a cena parada por N segundos, sem exigir input.
    pause(1),

    speak(ken, "Ta, ta bom, foi mal.", delay=1.2),

    # exit(): saída NARRATIVA de um personagem.
    sair(jef),

    speak(ken, "Ufa. Vou pra casa.", delay=1.2),

    # change_scene(): troca de cena com transição de fade (fade out
    # -> troca -> fade in). Sem `transition`, a troca seria instantânea.
    change_scene(quarto, transition="fade", duration=1.0),

    # cada Canvas tem seus próprios personagens -- ken não "atravessa"
    # a troca de cena sozinho, por isso ele entra de novo aqui.
    enter(ken, position=2, scale=0.6),

    speak(ken, "Bem melhor aqui no quarto.", delay=1.5),

    # remove_character(): remoção TÉCNICA/de configuração (contraste
    # com exit(), que é a saída narrativa usada acima para o Jef).
    remove_character(ken),
]


engine = Engine()

engine.run(campo, story)
