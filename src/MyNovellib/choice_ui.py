# Camada de UI da Choice, separada da Engine. Responsável por
# desenhar as opções, tratar hover/seleção (teclado e mouse) e
# detectar confirmação -- tudo que é "como a escolha aparece e se
# comporta na tela". A lógica narrativa (o que a escolha SIGNIFICA
# pra história: selected_index, efeitos no GameState, ramificação)
# continua na Engine/Choice, não aqui.

import pygame


class ChoiceUI:

    BOX_WIDTH = 500
    BOX_HEIGHT = 60
    GAP = 20

    def __init__(self, screen, font, options):

        self.screen = screen
        self.font = font
        self.options = options

        self.selected = 0
        self.rects = self._compute_rects()

    # Lista vertical de retângulos, centralizada na tela -- usada
    # tanto pra desenhar quanto pra detectar hover/clique.
    def _compute_rects(self):

        count = len(self.options)
        total_height = count * self.BOX_HEIGHT + (count - 1) * self.GAP

        x = (self.screen.get_width() - self.BOX_WIDTH) // 2
        start_y = (self.screen.get_height() - total_height) // 2

        rects = []

        for i in range(count):

            y = start_y + i * (self.BOX_HEIGHT + self.GAP)
            rects.append(pygame.Rect(x, y, self.BOX_WIDTH, self.BOX_HEIGHT))

        return rects

    # Índice da opção sob `pos`, ou None se não estiver sobre nenhuma.
    def option_at(self, pos):

        for i, rect in enumerate(self.rects):

            if rect.collidepoint(pos):
                return i

        return None

    # Processa um único evento pygame. Atualiza self.selected quando
    # o evento é navegação/hover. Retorna o índice CONFIRMADO (int)
    # quando o evento é uma confirmação (espaço/enter ou clique numa
    # opção), ou None caso contrário -- mover a seleção nunca confirma
    # sozinho.
    def handle_event(self, event):

        if event.type == pygame.KEYDOWN:

            if event.key in (pygame.K_UP, pygame.K_LEFT):

                self.selected = (self.selected - 1) % len(self.options)

            elif event.key in (pygame.K_DOWN, pygame.K_RIGHT):

                self.selected = (self.selected + 1) % len(self.options)

            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):

                return self.selected

        elif event.type == pygame.MOUSEMOTION:

            hovered = self.option_at(event.pos)

            if hovered is not None:
                self.selected = hovered

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                clicked = self.option_at(event.pos)

                if clicked is not None:
                    return clicked

        return None

    def draw(self):

        for i, rect in enumerate(self.rects):

            box = pygame.Surface(rect.size, pygame.SRCALPHA)

            if i == self.selected:
                box.fill((90, 90, 220, 230))
            else:
                box.fill((30, 30, 30, 200))

            self.screen.blit(box, rect.topleft)

            text_surface = self.font.render(
                self.options[i],
                True,
                (255, 255, 255)
            )

            text_rect = text_surface.get_rect(center=rect.center)

            self.screen.blit(text_surface, text_rect)
