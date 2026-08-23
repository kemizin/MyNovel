# Sistema de Actions: cada função pública aqui NÃO executa nada na hora.
# Ela apenas retorna um objeto de Action, que a Engine executa depois,
# em ordem, ao percorrer a lista `story`.


# Classe base de todas as ações da história. Não faz nada sozinha,
# só serve para a Engine reconhecer "isso é uma ação da história".
class Action:
    pass


# Ação: trocar a emoção atual de um personagem (ex: "normal" -> "bravo").
class Emotion(Action):

    def __init__(self, character, name):
        self.character = character
        self.name = name


def emotion(character, name):
    return Emotion(character, name)


# Ação: mover um personagem já presente na cena para outro slot de
# posição e/ou ajustar escala/offset. Campos não informados (None)
# mantêm o valor atual do personagem na cena.
class Move(Action):

    def __init__(
        self,
        character,
        position=None,
        scale=None,
        offset_x=None,
        offset_y=None
    ):
        self.character = character
        self.position = position
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y


def move(character, position=None, scale=None, offset_x=None, offset_y=None):
    return Move(character, position, scale, offset_x, offset_y)


# Ação: adicionar um personagem à cena durante a execução da história
# (mesma lógica de Canvas.add_character, só que adiada).
class AddCharacter(Action):

    def __init__(self, character, position, scale=0.5, offset_x=0, offset_y=0):
        self.character = character
        self.position = position
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y


def add_character(character, position, scale=0.5, offset_x=0, offset_y=0):
    return AddCharacter(character, position, scale, offset_x, offset_y)


# Ação: remover um personagem da cena durante a execução da história.
class RemoveCharacter(Action):

    def __init__(self, character):
        self.character = character


def remove_character(character):
    return RemoveCharacter(character)


# Ação: trocar a cena (Canvas) atual. Ainda sem transição visual
# (fade/animação) -- troca é instantânea.
class ChangeScene(Action):

    def __init__(self, canvas):
        self.canvas = canvas


def change_scene(canvas):
    return ChangeScene(canvas)
