# Action Factory: converte ActionData (dado) em Actions de Runtime
# (as mesmas que speak()/emotion()/move()/... retornam em story.py e
# dialogue.py).
#
#     JSON -> StoryData -> Action Factory -> Actions de Runtime -> Engine
#
# Ponto importante: a Engine (engine.py) nunca importa nada deste
# arquivo nem sabe que ActionData existe -- ela só recebe uma lista
# de Actions, exatamente como já recebia quando alguém escrevia
# `speak(ken, "Olá")` direto em Python. Escrever a história em Python
# ou carregar de um project.mynovel produz o mesmo resultado pra
# Engine.

from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import emotion, move, enter, exit as sair, pause
from src.MyNovellib.project.story_data import SUPPORTED_ACTION_TYPES


def _resolve_character(character_id, characters):

    if character_id not in characters:
        disponiveis = ", ".join(sorted(characters)) or "nenhum"
        raise KeyError(
            f"Personagem {character_id!r} não encontrado ao montar a "
            f"história (personagens disponíveis: {disponiveis})."
        )

    return characters[character_id]


# Um construtor pequeno por tipo -- cada um sabe ler os campos de um
# ActionData.fields e chamar a Action de Runtime correspondente.
_BUILDERS = {

    "speak": lambda fields, characters: speak(
        _resolve_character(fields["character"], characters),
        fields["text"],
        speed=fields.get("speed", 0.03),
        delay=fields.get("delay"),
        dub=fields.get("dub"),
    ),

    "emotion": lambda fields, characters: emotion(
        _resolve_character(fields["character"], characters),
        fields["emotion"],
    ),

    "move": lambda fields, characters: move(
        _resolve_character(fields["character"], characters),
        position=fields.get("position"),
        scale=fields.get("scale"),
        offset_x=fields.get("offset_x"),
        offset_y=fields.get("offset_y"),
    ),

    "enter": lambda fields, characters: enter(
        _resolve_character(fields["character"], characters),
        fields["position"],
        scale=fields.get("scale", 0.5),
        offset_x=fields.get("offset_x", 0),
        offset_y=fields.get("offset_y", 0),
    ),

    "exit": lambda fields, characters: sair(
        _resolve_character(fields["character"], characters),
    ),

    "pause": lambda fields, characters: pause(fields["duration"]),
}

# Garantia de que a fábrica cobre exatamente os tipos que ActionData
# aceita -- se story_data.py ganhar um tipo novo sem a fábrica ganhar
# o builder correspondente, isso é um erro de programação, não algo
# pra descobrir em tempo de execução.
assert set(_BUILDERS) == set(SUPPORTED_ACTION_TYPES), (
    "Action Factory desalinhada de SUPPORTED_ACTION_TYPES -- "
    "todo tipo suportado por ActionData precisa de um builder aqui."
)


# Converte um único ActionData numa Action de Runtime. `characters` é
# um dict {nome/id: Character} (Runtime) usado pra resolver os ids
# guardados em action_data.fields["character"].
def build_action(action_data, characters):

    builder = _BUILDERS.get(action_data.type)

    if builder is None:
        raise ValueError(
            f"Action Factory não sabe converter o tipo {action_data.type!r}."
        )

    return builder(action_data.fields, characters)


# Converte um StoryData inteiro numa lista de Actions de Runtime, na
# mesma ordem -- pronta pra Engine.run(canvas, story).
def build_story(story_data, characters):

    return [
        build_action(action_data, characters)
        for action_data in story_data.actions
    ]
