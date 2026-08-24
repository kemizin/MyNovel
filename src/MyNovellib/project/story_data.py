# Representação serializável de uma história -- prova de que Actions
# (speak, emotion, move, enter, exit, pause, ...) podem existir como
# DADOS, sem depender de código Python. Sem pygame.
#
# Subconjunto pequeno de propósito (ver Waystone 7 do Project System
# Update): serializar as demais Actions da biblioteca de story.py
# (Move mais os campos de scale/offset, Choice, GameState, etc.) fica
# pra quando for necessário -- o objetivo aqui é provar o conceito,
# não cobrir 100% da API de uma vez.
#
# A conversão ActionData -> Action de Runtime (speak(), emotion(),
# ...) é responsabilidade de uma camada separada (Action Factory,
# próximo Waystone), não daqui.

SUPPORTED_ACTION_TYPES = (
    "speak",
    "emotion",
    "move",
    "enter",
    "exit",
    "pause",
)

# Campos obrigatórios por tipo -- documentação executável (falha cedo
# se faltar algo), não uma linguagem de schema.
_REQUIRED_FIELDS = {
    "speak": ("character", "text"),
    "emotion": ("character", "emotion"),
    "move": ("character",),
    "enter": ("character", "position"),
    "exit": ("character",),
    "pause": ("duration",),
}

_DESCRIBE_TEXT_MAX = 40


def _describe_speak(fields):

    texto = fields.get("text", "")

    if len(texto) > _DESCRIBE_TEXT_MAX:
        texto = texto[: _DESCRIBE_TEXT_MAX - 1] + "…"

    return f'speak {fields.get("character")}: "{texto}"'


def _describe_move(fields):

    partes = [
        f"{chave}={fields[chave]}"
        for chave in ("position", "scale", "offset_x", "offset_y")
        if fields.get(chave) is not None
    ]

    return f'move {fields.get("character")}: ' + (", ".join(partes) if partes else "(sem mudanças)")


# Um describer pequeno por tipo -- mesma ideia do _BUILDERS em
# action_factory.py, só que pra texto em vez de Action de Runtime.
_ACTION_DESCRIBERS = {
    "speak": _describe_speak,
    "emotion": lambda fields: f'emotion {fields.get("character")}: {fields.get("emotion")}',
    "move": _describe_move,
    "enter": lambda fields: f'enter {fields.get("character")} (position {fields.get("position")})',
    "exit": lambda fields: f'exit {fields.get("character")}',
    "pause": lambda fields: f'pause {fields.get("duration")}s',
}

assert set(_ACTION_DESCRIBERS) == set(SUPPORTED_ACTION_TYPES), (
    "_ACTION_DESCRIBERS desalinhado de SUPPORTED_ACTION_TYPES -- todo "
    "tipo suportado por ActionData precisa de um describer aqui."
)


# Uma única Action representada como dado: {"type": ..., <campos>}.
#
#     ActionData("speak", character="ken", text="Olá!")
#     ActionData("emotion", character="jef", emotion="bravo")
#     ActionData("move", character="jef", position=2)
class ActionData:

    def __init__(self, type, **fields):

        if type not in SUPPORTED_ACTION_TYPES:
            raise ValueError(
                f"Tipo de Action não suportado como dado: {type!r}. "
                f"Suportados: {', '.join(SUPPORTED_ACTION_TYPES)}."
            )

        missing = [
            field for field in _REQUIRED_FIELDS[type]
            if field not in fields
        ]

        if missing:
            raise ValueError(
                f"Action {type!r} sem campo(s) obrigatório(s): "
                f"{', '.join(missing)}."
            )

        self.type = type
        self.fields = fields

    def to_dict(self):
        return {"type": self.type, **self.fields}

    # Resumo legível de uma linha só, tipo "speak jef: \"Olá!\"" -- pro
    # Story Editor do Studio mostrar a lista de Actions sem repetir
    # essa formatação lá (e pra qualquer outra interface que precise
    # descrever uma Action sem reescrever isso). Não é o mesmo que
    # __repr__ (que mostra o dado cru, pra debug).
    def describe(self):
        return _ACTION_DESCRIBERS[self.type](self.fields)

    @classmethod
    def from_dict(cls, data):

        data = dict(data)
        action_type = data.pop("type")

        return cls(action_type, **data)

    def __eq__(self, other):

        if not isinstance(other, ActionData):
            return NotImplemented

        return self.to_dict() == other.to_dict()

    def __repr__(self):
        return f"ActionData({self.to_dict()!r})"


# Uma história: nome + lista ordenada de ActionData.
class StoryData:

    def __init__(self, name, actions=None):

        if not name or not str(name).strip():
            raise ValueError("StoryData precisa de um nome não vazio.")

        self.name = name
        self.actions = list(actions) if actions else []

    def add_action(self, type, **fields):

        action = ActionData(type, **fields)
        self.actions.append(action)

        return action

    def to_dict(self):

        return {
            "name": self.name,
            "actions": [action.to_dict() for action in self.actions],
        }

    @classmethod
    def from_dict(cls, data):

        story = cls(name=data["name"])

        story.actions = [
            ActionData.from_dict(entry)
            for entry in data.get("actions", [])
        ]

        return story

    def __eq__(self, other):

        if not isinstance(other, StoryData):
            return NotImplemented

        return self.to_dict() == other.to_dict()

    def __repr__(self):
        return f"StoryData(name={self.name!r}, actions={len(self.actions)})"
