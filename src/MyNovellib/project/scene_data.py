# Representação serializável de uma cena -- o que o Studio edita e o
# que fica salvo no arquivo de projeto. Sem pygame: SceneData nunca
# carrega a imagem de fundo nem toca música, só guarda os caminhos.
#
# Equivalente de dados a Canvas (src/MyNovellib/scene.py), que
# continua sendo a classe que a Engine usa de verdade em tempo de
# execução. A conversão SceneData -> Canvas é responsabilidade de uma
# camada separada (Project Runtime Loading), não daqui.


# Um personagem presente na cena desde o início -- equivalente de
# dados a Canvas.add_character(), com um campo a mais: `emotion`
# (a emoção inicial dele nessa cena, já que o Runtime só sabe disso
# depois de criar o Character de verdade).
class SceneCharacter:

    def __init__(
        self,
        character,
        position,
        scale=0.5,
        offset_x=0,
        offset_y=0,
        emotion=None
    ):

        if not character or not str(character).strip():
            raise ValueError(
                "SceneCharacter precisa de um 'character' (id/nome) não vazio."
            )

        self.character = character
        self.position = position  # passa pela property -- valida 1/2/3
        self.scale = scale        # passa pela property -- valida > 0
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.emotion = emotion

    # `position`/`scale` são property (não atributo simples) de propósito:
    # a validação precisa valer tanto na criação quanto em qualquer edição
    # posterior (ex.: Scene Editor mudando um valor existente via
    # `setattr(placement, "position", valor)`) -- um atributo comum só
    # protegeria a criação, e o Scene Editor edita muito mais do que cria.
    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):

        if value not in (1, 2, 3):
            raise ValueError(
                f"Position precisa ser 1, 2 ou 3 (veio {value!r})."
            )

        self._position = value

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):

        if value <= 0:
            raise ValueError(
                f"Scale precisa ser maior que zero (veio {value!r})."
            )

        self._scale = value

    def to_dict(self):

        return {
            "character": self.character,
            "position": self.position,
            "scale": self.scale,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "emotion": self.emotion,
        }

    @classmethod
    def from_dict(cls, data):

        return cls(
            character=data["character"],
            position=data["position"],
            scale=data.get("scale", 0.5),
            offset_x=data.get("offset_x", 0),
            offset_y=data.get("offset_y", 0),
            emotion=data.get("emotion"),
        )

    def __eq__(self, other):

        if not isinstance(other, SceneCharacter):
            return NotImplemented

        return self.to_dict() == other.to_dict()

    def __repr__(self):

        return (
            f"SceneCharacter(character={self.character!r}, "
            f"position={self.position!r})"
        )


class SceneData:

    def __init__(
        self,
        name,
        background=None,
        resolution=None,
        music=None,
        characters=None
    ):

        if not name or not str(name).strip():
            raise ValueError("SceneData precisa de um nome não vazio.")

        self.name = name
        self.background = background

        # None = herda a resolution do Project -- a maioria das cenas
        # usa a mesma resolução do projeto inteiro; só sobrescreve
        # quando precisar de algo diferente.
        self.resolution = tuple(resolution) if resolution else None

        self.music = music
        self.characters = list(characters) if characters else []

    def add_character(
        self,
        character,
        position,
        scale=0.5,
        offset_x=0,
        offset_y=0,
        emotion=None
    ):

        placement = SceneCharacter(
            character, position, scale, offset_x, offset_y, emotion
        )

        self.characters.append(placement)

        return placement

    def to_dict(self):

        return {
            "name": self.name,
            "background": self.background,
            "resolution": list(self.resolution) if self.resolution else None,
            "music": self.music,
            "characters": [c.to_dict() for c in self.characters],
        }

    @classmethod
    def from_dict(cls, data):

        scene = cls(
            name=data["name"],
            background=data.get("background"),
            resolution=data.get("resolution"),
            music=data.get("music"),
        )

        scene.characters = [
            SceneCharacter.from_dict(entry)
            for entry in data.get("characters", [])
        ]

        return scene

    def __eq__(self, other):

        if not isinstance(other, SceneData):
            return NotImplemented

        return self.to_dict() == other.to_dict()

    def __repr__(self):

        return f"SceneData(name={self.name!r}, background={self.background!r})"
