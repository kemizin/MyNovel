# Representação serializável de um personagem -- o que o Studio edita
# e o que fica salvo no arquivo de projeto. Sem pygame, sem qualquer
# dependência do Runtime.
#
# src/MyNovellib/character.py (Character) continua sendo a classe que
# a Engine usa de verdade em tempo de execução -- CharacterData NÃO
# substitui nem duplica essa lógica, é só o formato de dados. A
# conversão CharacterData -> Character é responsabilidade de uma
# camada separada (Project Runtime Loading), não daqui.


class CharacterData:

    def __init__(self, name, emotions=None):

        if not name or not str(name).strip():
            raise ValueError("CharacterData precisa de um nome não vazio.")

        self.name = name

        # nome_da_emoção -> {"idle": caminho, "talking": caminho ou None}
        # -- mesmo formato que Character.add_emotion() já usa.
        self.emotions = {}

        for emotion_name, sprites in (emotions or {}).items():
            self.add_emotion(
                emotion_name,
                sprites["idle"],
                sprites.get("talking")
            )

    def add_emotion(self, name, idle, talking=None):

        if not idle or not str(idle).strip():
            raise ValueError(
                f"A emoção {name!r} de {self.name!r} precisa de um sprite 'idle'."
            )

        self.emotions[name] = {"idle": idle, "talking": talking}

    def to_dict(self):

        return {
            "name": self.name,
            "emotions": {
                emotion_name: dict(sprites)
                for emotion_name, sprites in self.emotions.items()
            },
        }

    @classmethod
    def from_dict(cls, data):

        return cls(name=data["name"], emotions=data.get("emotions", {}))

    def __eq__(self, other):

        if not isinstance(other, CharacterData):
            return NotImplemented

        return self.name == other.name and self.emotions == other.emotions

    def __repr__(self):

        return (
            f"CharacterData(name={self.name!r}, "
            f"emotions={list(self.emotions)!r})"
        )
