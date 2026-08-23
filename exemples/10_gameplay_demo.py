# Demonstração da Gameplay Update: usa TODOS os elementos novos numa
# história curta e jogável do início ao fim.
#
# Roda com: .venv/Scripts/python.exe exemples/10_gameplay_demo.py
#
# Controles: ESPAÇO ou clique esquerdo avançam as falas. Na escolha,
# use as SETAS + ESPAÇO/ENTER, ou clique direto numa opção.
#
# Elementos usados: 2 personagens (Jef, Ken), 2 cenas (campo, quarto),
# enter, exit, emotion, move, speak, pause, choice, GameState,
# if_state (condição), 2 caminhos narrativos diferentes, change_scene
# com fade.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import (
    enter,
    exit as sair,
    emotion,
    move,
    pause,
    choice,
    if_state,
    change_scene,
)


# --- Personagens -----------------------------------------------------

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

ken = Character("Ken")
ken.add_emotion(
    "normal",
    idle="assets/char/ken/ken.png",
    talking="assets/char/ken/ken_falando.png"
)
ken.emotion("normal")


# --- Cenas -------------------------------------------------------------

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
quarto = Canvas("quarto", "assets/fundos/quarto.jpg", 1920, 1080)

# Jef já está no campo desde o início (configuração da cena).
campo.add_character(jef, position=1, scale=0.5)


# --- História ------------------------------------------------------

story = [

    # =========================
    # CAMPO
    # =========================

    speak(jef, "Que tarde tranquila."),

    enter(ken, position=3, scale=0.5),

    speak(ken, "Jef! Preciso da sua ajuda."),
    speak(jef, "O que aconteceu?"),
    speak(ken, "Ouvi um barulho estranho vindo do meu quarto."),

    emotion(jef, "bravo"),
    speak(jef, "Um barulho? Isso pode ser sério."),

    move(jef, position=2, scale=0.7),
    pause(1),

    speak(ken, "Você vem comigo checar?"),

    # A escolha decide o resto da história -- duas ramificações reais,
    # cada uma alterando o GameState (efeito "coragem") de um jeito.
    choice(
        ("Ajudar Ken", {"coragem": 5}, [
            speak(jef, "Claro, vamos juntos."),
        ]),
        ("Deixar Ken ir sozinho", {"coragem": 0}, [
            speak(jef, "Acho melhor você ir sozinho dessa vez."),
            emotion(jef, "normal"),
        ]),
    ),

    sair(ken),

    speak(jef, "Vamos ver o que está acontecendo."),

    # =========================
    # QUARTO
    # =========================

    change_scene(quarto, transition="fade", duration=1.0),

    enter(jef, position=2, scale=0.5),

    # Condição sobre o GameState: o que aconteceu no quarto depende
    # da escolha lá no campo -- dois finais diferentes de verdade.
    if_state("coragem", ">=", 5, [
        enter(ken, position=1, scale=0.5),
        speak(ken, "Era só o vento entrando pela janela."),
        speak(jef, "Que susto à toa. Ainda bem que viemos juntos."),
    ]),

    if_state("coragem", "<", 5, [
        speak(jef, "Ken já deve ter descoberto o que era."),
        pause(1),
        speak(jef, "Espero que esteja tudo bem com ele."),
    ]),

]


engine = Engine()

engine.run(campo, story)
