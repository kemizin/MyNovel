# Sistema de Actions: cada função pública aqui NÃO executa nada na hora.
# Ela apenas retorna um objeto de Action, que a Engine executa depois,
# em ordem, ao percorrer a lista `story`.


# Classe base de todas as ações da história. Não faz nada sozinha,
# só serve para a Engine reconhecer "isso é uma ação da história".
#
# Ciclo de vida garantido pela Engine (ver engine.py, Engine.run):
#   1. a Action só guarda dados -- nada é executado ao ser criada
#      (speak/emotion/move/... retornam a Action, não a executam)
#   2. a Engine despacha a Action para o seu execute_*, que atualiza
#      o estado (Character/Canvas)
#   3. o mesmo execute_* deixa a tela já atualizada antes de retornar,
#      chamando self.render() -- exceto Dialogue, que tem loop de
#      desenho próprio (um frame por vez, com input) e não depende de
#      render() para aparecer
#   4. só então a Engine passa para a próxima Action da lista `story`
#
# Ou seja: nenhuma Action depende de um speak() posterior para que sua
# mudança apareça na tela.
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
