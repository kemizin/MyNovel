# Transições visuais para troca de cena (ChangeScene).
#
# Toda a lógica de fade fica isolada aqui, de propósito: a Engine só
# delega para transition.run(engine, novo_canvas) quando a Action
# ChangeScene pede uma transição. run(), execute_dialogue(),
# execute_move() etc. continuam sem saber que fade existe.

import pygame


# Fade clássico: cena A escurece até preto, troca de cena acontece com
# a tela preta, depois a cena B clareia a partir do preto.
class FadeTransition:

    def __init__(self, duration=0.5):
        self.duration = duration

    def run(self, engine, new_canvas):

        half_duration = self.duration / 2

        # cena atual (A) escurecendo até preto
        self._fade(engine, fade_in=False, duration=half_duration)

        if not engine.running:
            return

        # troca background/personagens/música com a tela já preta
        engine._load_canvas(new_canvas)

        # cena nova (B) clareando a partir do preto
        self._fade(engine, fade_in=True, duration=half_duration)

    # fade_in=False: desenha a cena atual escurecendo (alpha 0 -> 255).
    # fade_in=True: desenha a cena atual clareando (alpha 255 -> 0).
    def _fade(self, engine, fade_in, duration):

        duration_ms = max(
            int(duration * 1000),
            1
        )

        overlay = pygame.Surface(engine.screen.get_size())
        overlay.fill((0, 0, 0))

        start = pygame.time.get_ticks()

        while engine.running:

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    engine.running = False
                    return

            elapsed = pygame.time.get_ticks() - start
            progress = min(elapsed / duration_ms, 1.0)

            alpha = (
                int(255 * (1 - progress)) if fade_in
                else int(255 * progress)
            )

            engine.draw_scene()

            overlay.set_alpha(alpha)
            engine.screen.blit(overlay, (0, 0))

            pygame.display.flip()
            engine.clock.tick(60)

            if progress >= 1.0:
                return
