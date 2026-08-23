from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak


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


campo = Canvas(
    "campo",
    "assets/fundos/campo.jpg",
    1920,
    1080,
    music="assets/music/ambiente_2.mp3"
)

campo.add_character(
    jef,
    1,
    scale=0.5
)

campo.add_character(
    ken,
    3,
    scale=0.5
)


story = [

    speak(
        ken,
        "mano, preciso de ajuda",
        delay=1
    ),

    speak(
        jef,
        "o que você fez?",
        delay=1
    ),

    speak(
        ken,
        "tecnicamente... nada",
        delay=2
    ),

    speak(
        jef,
        "isso é exatamente o que me preocupa",
        delay=2
    ),

    speak(
        ken,
        "eu só fui mexer no código de produção",
        delay=2
    ),

    speak(
        jef,
        "POR QUÊ?",
        delay=1
    ),

    speak(
        ken,
        "porque tava funcionando",
        delay=2
    ),

    speak(
        jef,
        "e você pensou que isso era suspeito?",
        delay=2
    ),

    speak(
        ken,
        "pensei",
        delay=1
    ),

    speak(
        ken,
        "aí eu corrigi",
        delay=1
    ),

    speak(
        jef,
        "o que você corrigiu?",
        delay=2
    ),

    speak(
        ken,
        "a parte que tava funcionando",
        delay=2
    ),

    speak(
        jef,
        "KEN...",
        delay=2
    ),

    speak(
        ken,
        "agora não funciona mais",
        delay=1
    ),

    speak(
        jef,
        "pelo menos você sabe o que quebrou?",
        delay=2
    ),

    speak(
        ken,
        "sei",
        delay=1
    ),

    speak(
        jef,
        "o quê?",
        delay=1
    ),

    speak(
        ken,
        "a produção",
        delay=3
    ),

    speak(
        jef,
        "...",
        delay=2
    ),

    speak(
        ken,
        "quer que eu faça um commit?",
        delay=1
    ),

    speak(
        jef,
        "NÃO",
        delay=1
    ),

    speak(
        ken,
        "um push então?",
        delay=1
    ),

    speak(
        jef,
        "LARGA O TECLADO",
        delay=2
    ),

    speak(
        ken,
        "tá bom, tá bom",
        delay=1
    ),

    speak(
        jef,
        "faz quanto tempo que isso aconteceu?",
        delay=2
    ),

    speak(
        ken,
        "uns vinte minutos",
        delay=1
    ),

    speak(
        jef,
        "E VOCÊ SÓ ME CHAMOU AGORA?",
        delay=2
    ),

    speak(
        ken,
        "nos primeiros cinco minutos eu achei que era problema do servidor",
        delay=2
    ),

    speak(
        jef,
        "e nos outros quinze?",
        delay=2
    ),

    speak(
        ken,
        "eu reiniciei o servidor",
        delay=2
    ),

    speak(
        jef,
        "você reiniciou o servidor de produção?!",
        delay=2
    ),

    speak(
        ken,
        "duas vezes",
        delay=1
    ),

    speak(
        jef,
        "KEN, VOCÊ TRANSFORMOU UM BUG EM EVENTO HISTÓRICO",
        delay=2
    ),

    speak(
        ken,
        "pelo menos agora ninguém sabe exatamente o que aconteceu",
        delay=2
    ),

    speak(
        jef,
        "eu sei",
        delay=1
    ),

    speak(
        ken,
        "ah",
        delay=1
    ),

    speak(
        jef,
        "e eu vou contar",
        delay=2
    ),

    speak(
        ken,
        "pra quem?",
        delay=1
    ),

    speak(
        jef,
        "pro meu chefe",
        delay=2
    ),

    speak(
        ken,
        "posso ir junto?",
        delay=1
    ),

    speak(
        jef,
        "por quê?",
        delay=1
    ),

    speak(
        ken,
        "quero ver a cara dele",
        delay=2
    ),

    speak(
        jef,
        "você não tem medo?",
        delay=2
    ),

    speak(
        ken,
        "tenho",
        delay=1
    ),

    speak(
        ken,
        "mas quero aproveitar o espetáculo",
        delay=3
    )
]


engine = Engine()

engine.run(
    campo,
    story
)