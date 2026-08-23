# Sistema de Actions: cada função pública aqui NÃO executa nada na hora.
# Ela apenas retorna um objeto de Action, que a Engine executa depois,
# em ordem, ao percorrer a lista `story`.

import operator as _operator


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


# Ação: trocar a cena (Canvas) atual. Por padrão a troca é instantânea;
# passando transition="fade" a Engine faz fade out -> troca -> fade in
# (ver src/MyNovellib/transitions.py) usando `duration` segundos ao todo.
class ChangeScene(Action):

    def __init__(self, canvas, transition=None, duration=0.5):
        self.canvas = canvas
        self.transition = transition
        self.duration = duration


def change_scene(canvas, transition=None, duration=0.5):
    return ChangeScene(canvas, transition, duration)


# Ação: entrada narrativa de um personagem na cena. Tecnicamente faz o
# mesmo que AddCharacter (adiciona o personagem ao Canvas), mas existe
# como Action própria porque semanticamente é um acontecimento da
# história ("o personagem entrou"), não uma configuração inicial de
# cena. add_character() continua existindo para montar a cena antes
# da história começar.
class Enter(Action):

    def __init__(self, character, position, scale=0.5, offset_x=0, offset_y=0):
        self.character = character
        self.position = position
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y


def enter(character, position, scale=0.5, offset_x=0, offset_y=0):
    return Enter(character, position, scale, offset_x, offset_y)


# Ação: saída narrativa de um personagem da cena (equivalente
# semântico de RemoveCharacter, usado dentro da história).
class Exit(Action):

    def __init__(self, character):
        self.character = character


def exit(character):
    return Exit(character)


# Ação: mantém a cena parada na tela por `duration` segundos, sem
# exigir input do jogador. Primeira Action com duração própria --
# base para futuras ações visuais (fade, shake, flash, ...).
class Pause(Action):

    def __init__(self, duration):
        self.duration = duration


def pause(duration):
    return Pause(duration)


# Ação: pausa a história e mostra opções pro jogador escolher uma.
# A Engine bloqueia (não avança pra próxima Action) até o jogador
# confirmar uma opção -- por teclado (setas + espaço/enter) ou mouse
# (clique). selected_index começa None e só é preenchido pela Engine
# depois que o jogador confirma (ver Waystone "choice result").
#
# Cada opção pode ser só o texto:
#
#     choice("Ir para casa", "Ficar aqui")
#
# ou um par (texto, efeitos) pra alterar o GameState quando aquela
# opção for escolhida -- efeitos é um dict {chave: quantidade},
# aplicado via GameState.increment():
#
#     choice(
#         ("Ajudar Jef", {"amizade": 1}),
#         ("Ignorar Jef", {"amizade": 0}),
#     )
class Choice(Action):

    def __init__(self, *options):

        if len(options) < 2:
            raise ValueError(
                "choice() precisa de pelo menos 2 opções."
            )

        self.options = []
        self.effects = []

        for option in options:

            if isinstance(option, tuple):
                text, effects = option
            else:
                text, effects = option, {}

            self.options.append(text)
            self.effects.append(effects)

        self.selected_index = None


def choice(*options):
    return Choice(*options)


_OPERATORS = {
    "==": _operator.eq,
    "!=": _operator.ne,
    ">": _operator.gt,
    "<": _operator.lt,
    ">=": _operator.ge,
    "<=": _operator.le,
}


# Ação: executa uma lista de Actions só se uma condição sobre o
# GameState for verdadeira. Não cria uma linguagem de scripting -- só
# um teste simples (GameState.get(key) OPERADOR value).
#
#     if_state(
#         "amizade", ">=", 10,
#         [speak(jef, "Eu confio em você.")]
#     )
#
# Operadores aceitos: == != > < >= <=. `value` pode ser número,
# string ou bool (bool funciona bem com == e !=).
class IfState(Action):

    def __init__(self, key, operator, value, actions):

        if operator not in _OPERATORS:
            raise ValueError(
                f"Operador inválido: {operator!r}. "
                f"Use um de: {', '.join(sorted(_OPERATORS))}."
            )

        self.key = key
        self.operator = operator
        self.value = value
        self.actions = actions

    def evaluate(self, current_value):
        return _OPERATORS[self.operator](current_value, self.value)


def if_state(key, operator, value, actions):
    return IfState(key, operator, value, actions)
