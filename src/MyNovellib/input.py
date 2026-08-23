# Abstração simples de input: lê a fila de eventos do pygame UMA vez
# por frame e organiza o que a Engine/Actions precisam saber, pra
# nenhum lugar do código ter que espalhar
# `pygame.KEYDOWN`/`pygame.MOUSEBUTTONDOWN` por conta própria.
#
# NÃO é um sistema de controles configuráveis -- só organiza o input
# que já existia (QUIT, e o gesto de "avançar" usado pelo diálogo:
# espaço ou clique esquerdo). Quem precisar dos eventos crus (como
# ChoiceUI, que precisa saber setas/posição do clique) continua tendo
# acesso via `events`.
import pygame


class Input:

    def __init__(self):

        self.quit = False
        self.advance = False
        self.events = []

    # Drena a fila de eventos do pygame (uma vez) e devolve um Input
    # já preenchido pra este frame.
    @classmethod
    def poll(cls):

        result = cls()

        for event in pygame.event.get():

            result.events.append(event)

            if event.type == pygame.QUIT:

                result.quit = True

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:

                result.advance = True

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                result.advance = True

        return result
