class Canvas:

    def __init__(
        self,
        nome,
        imagem,
        tamanho_x,
        tamanho_y,
        music=None
    ):
        self.nome = nome
        self.imagem = imagem
        self.tamanho = (tamanho_x, tamanho_y)
        self.music = music

        self.characters = {}

    def add_character(
        self,
        character,
        position,
        scale=0.5,
        offset_x=0,
        offset_y=0
    ):

        self.characters[character.nome] = {
            "character": character,
            "position": position,
            "scale": scale,
            "offset_x": offset_x,
            "offset_y": offset_y
        }

    # Remove um personagem da cena (usado pela Action RemoveCharacter).
    def remove_character(self, character):

        if character.nome not in self.characters:
            raise ValueError(
                f"O personagem '{character.nome}' não está na cena '{self.nome}'."
            )

        del self.characters[character.nome]

    # Atualiza posição/escala/offset de um personagem já presente na
    # cena (usado pela Action Move). Campos None mantêm o valor atual.
    def move_character(
        self,
        character,
        position=None,
        scale=None,
        offset_x=None,
        offset_y=None
    ):

        if character.nome not in self.characters:
            raise ValueError(
                f"O personagem '{character.nome}' não está na cena '{self.nome}'."
            )

        data = self.characters[character.nome]

        if position is not None:
            data["position"] = position

        if scale is not None:
            data["scale"] = scale

        if offset_x is not None:
            data["offset_x"] = offset_x

        if offset_y is not None:
            data["offset_y"] = offset_y