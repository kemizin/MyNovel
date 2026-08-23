import os
import sys

# Permite rodar este arquivo diretamente de dentro de exemples/,
# sem precisar ajustar o PYTHONPATH manualmente.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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

quarto = Canvas(
    "quarto",
    "assets/fundos/quarto.jpg",
    1920,
    1080,
    music="assets/music/ambiente_2.mp3"
)

sala = Canvas(
    "sala",
    "assets/fundos/sala.jpg",
    1920,
    1080,
    music="assets/music/ambiente_2.mp3"
)



# Jef já está no campo esperando. Ken ainda não existe na cena -- ele
# chega correndo como parte da história (enter()), não como
# configuração inicial.
campo.add_character(
    jef,
    1,
    scale=0.5
)


story = [

    # =========================
    # CAMPO
    # =========================

    # Ken ainda não estava na cena (só o Jef, via add_character antes
    # da história) -- sem isso ele falava sem aparecer na tela.
    enter(ken, position=3, scale=0.5),

    speak(
        ken,
        "Jef, você acha que dá pra ver a casa daqui?",
        delay=1.2
    ),

    speak(
        jef,
        "Acho que sim.",
        delay=1.2
    ),

    speak(
        ken,
        "Então olha ali.",
        delay=1.2
    ),

    speak(
        jef,
        "Onde?",
        delay=1.2
    ),

    speak(
        ken,
        "Ali.",
        delay=1
    ),

    speak(
        jef,
        "Ken, você tá apontando pro chão.",
        delay=1.5
    ),

    speak(
        ken,
        "Eu sei.",
        delay=1
    ),

    speak(
        jef,
        "Então por que você mandou eu olhar?",
        delay=1.5
    ),

    speak(
        ken,
        "Porque eu achei uma coisa.",
        delay=1.2
    ),

    speak(
        jef,
        "O quê?",
        delay=1
    ),

    speak(
        ken,
        "Uma pedra.",
        delay=1.2
    ),

    speak(
        jef,
        "Você me chamou pra mostrar uma pedra?",
        delay=1.5
    ),

    speak(
        ken,
        "Não é uma pedra qualquer.",
        delay=1.2
    ),

    speak(
        jef,
        "É o quê então?",
        delay=1.2
    ),

    speak(
        ken,
        "Uma pedra bonita.",
        delay=1.5
    ),

    speak(
        jef,
        "Ah.",
        delay=1
    ),

    speak(
        ken,
        "Você não entende arte.",
        delay=1.2
    ),

    move(jef, position=2, scale=0.8),

    speak(
        jef,
        "Você ficou quinze minutos olhando pra uma pedra.",
        delay=1.5
    ),

    speak(
        ken,
        "Eu tava refletindo.",
        delay=1.2
    ),

    speak(
        jef,
        "Sobre o quê?",
        delay=1.2
    ),

    speak(
        ken,
        "Sobre como seria bom estar em casa agora.",
        delay=1.5
    ),

    pause(1),

    speak(
        jef,
        "Então vamos pra casa.",
        delay=1.2
    ),

    speak(
        ken,
        "Boa ideia.",
        delay=1
    ),

    speak(
        ken,
        "Mas você leva a pedra.",
        delay=1.2
    ),

    speak(
        jef,
        "Não.",
        delay=1
    ),

    speak(
        ken,
        "Por favor.",
        delay=1
    ),

    speak(
        jef,
        "Não.",
        delay=1
    ),

    speak(
        ken,
        "Ela tem valor sentimental.",
        delay=1.2
    ),

    speak(
        jef,
        "Você conheceu ela hoje.",
        delay=1.2
    ),

    speak(
        ken,
        "E já temos uma história juntos.",
        delay=1.5
    ),

    sair(jef),

    speak(
        ken,
        "Covarde.",
        delay=1.2
    ),

    # =========================
    # SALA
    # =========================

    change_scene(sala, transition="fade", duration=1.0),

    enter(ken, position=2, scale=0.6),

    enter(jef, position=1, scale=0.5),

    speak(
        jef,
        "Pronto. Chegamos.",
        delay=1.2
    ),

    speak(
        ken,
        "Finalmente.",
        delay=1
    ),

    speak(
        jef,
        "Você que quis ir embora.",
        delay=1.2
    ),

    speak(
        ken,
        "Eu tava cansado.",
        delay=1
    ),

    speak(
        jef,
        "Você ficou sentado no campo o tempo todo.",
        delay=1.5
    ),

    speak(
        ken,
        "Exatamente.",
        delay=1
    ),

    speak(
        jef,
        "Como isso te cansou?",
        delay=1.5
    ),

    speak(
        ken,
        "Mentalmente.",
        delay=1
    ),

    speak(
        jef,
        "Você não fez nada.",
        delay=1.2
    ),

    speak(
        ken,
        "Esse é o problema.",
        delay=1.5
    ),

    pause(1),

    speak(
        jef,
        "Quer fazer alguma coisa?",
        delay=1.2
    ),

    speak(
        ken,
        "Quero.",
        delay=1
    ),

    speak(
        jef,
        "O quê?",
        delay=1
    ),

    speak(
        ken,
        "Comer.",
        delay=1.2
    ),

    speak(
        jef,
        "Você acabou de chegar.",
        delay=1.2
    ),

    speak(
        ken,
        "Exatamente.",
        delay=1
    ),

    speak(
        jef,
        "Tá com fome?",
        delay=1
    ),

    speak(
        ken,
        "Não.",
        delay=1
    ),

    speak(
        jef,
        "Então por que quer comer?",
        delay=1.5
    ),

    speak(
        ken,
        "Porque comida existe.",
        delay=1.5
    ),

    speak(
        jef,
        "Isso não é argumento.",
        delay=1.2
    ),

    speak(
        ken,
        "Pra mim é.",
        delay=1
    ),

    move(jef, position=2, scale=0.7),

    speak(
        jef,
        "Vou fazer alguma coisa pra gente comer.",
        delay=1.5
    ),

    speak(
        ken,
        "Faz alguma coisa boa.",
        delay=1.2
    ),

    speak(
        jef,
        "Tipo?",
        delay=1
    ),

    speak(
        ken,
        "Pizza.",
        delay=1
    ),

    speak(
        jef,
        "Eu não sei fazer pizza.",
        delay=1.2
    ),

    speak(
        ken,
        "Então faz um sanduíche.",
        delay=1
    ),

    speak(
        jef,
        "Isso eu sei fazer.",
        delay=1.2
    ),

    speak(
        ken,
        "Ótimo.",
        delay=1
    ),

    pause(1),

    speak(
        jef,
        "Você quer ajudar?",
        delay=1.2
    ),

    speak(
        ken,
        "Não.",
        delay=1
    ),

    speak(
        jef,
        "Nem um pouco?",
        delay=1
    ),

    speak(
        ken,
        "Eu posso supervisionar.",
        delay=1.5
    ),

    speak(
        jef,
        "Você vai ficar sentado?",
        delay=1.2
    ),

    speak(
        ken,
        "Com muita atenção.",
        delay=1.5
    ),

    speak(
        jef,
        "Incrível.",
        delay=1
    ),

    sair(jef),

    speak(
        ken,
        "Acho que ele ficou bravo.",
        delay=1.2
    ),

    pause(2),

    speak(
        ken,
        "Vou esperar ele esquecer.",
        delay=1.2
    ),

    # =========================
    # QUARTO
    # =========================

    change_scene(quarto, transition="fade", duration=1.0),

    enter(ken, position=2, scale=0.6),

    speak(
        ken,
        "Enquanto ele cozinha, vou tirar um cochilo.",
        delay=1.5
    ),

    speak(
        ken,
        "Só cinco minutinhos.",
        delay=1.2
    ),

    pause(1.5),

    speak(
        ken,
        "Talvez dez.",
        delay=1.2
    ),

    pause(1),

    speak(
        ken,
        "Tá, quinze.",
        delay=1.2
    ),

    pause(1),

    speak(
        ken,
        "Eu mereço.",
        delay=1.2
    ),

    enter(jef, position=1, scale=0.5),

    speak(
        jef,
        "Ken.",
        delay=1.2
    ),

    speak(
        ken,
        "Hmm?",
        delay=1
    ),

    speak(
        jef,
        "O sanduíche tá pronto.",
        delay=1.5
    ),

    speak(
        ken,
        "Já?",
        delay=1
    ),

    speak(
        jef,
        "Faz uns vinte minutos.",
        delay=1.5
    ),

    speak(
        ken,
        "Caramba.",
        delay=1
    ),

    speak(
        jef,
        "Você dormiu?",
        delay=1.2
    ),

    speak(
        ken,
        "Não.",
        delay=1
    ),

    speak(
        jef,
        "Você tá deitado de olho fechado.",
        delay=1.5
    ),

    speak(
        ken,
        "Eu tava pensando.",
        delay=1
    ),

    speak(
        jef,
        "Claro.",
        delay=1
    ),

    speak(
        ken,
        "Pensando profundamente.",
        delay=1.2
    ),

    speak(
        jef,
        "No quê?",
        delay=1
    ),

    speak(
        ken,
        "No sanduíche.",
        delay=1.5
    ),

    pause(1),

    speak(
        jef,
        "Levanta.",
        delay=1
    ),

    speak(
        ken,
        "Não quero.",
        delay=1
    ),

    speak(
        jef,
        "Eu fiz comida.",
        delay=1.2
    ),

    speak(
        ken,
        "Isso muda tudo.",
        delay=1.2
    ),

    move(ken, position=2, scale=0.8),

    speak(
        ken,
        "Vamos.",
        delay=1
    ),

    speak(
        jef,
        "Finalmente.",
        delay=1.2
    ),

    speak(
        ken,
        "Mas depois eu volto pra cama.",
        delay=1.2
    ),

    speak(
        jef,
        "Eu sabia.",
        delay=1
    ),

    sair(jef),

    speak(
        ken,
        "A vida é boa.",
        delay=1.5
    ),

    remove_character(ken),
]


engine = Engine()

engine.run(
    campo,
    story
)
