import pygame

from src.MyNovellib.dialogue import Dialogue
from src.MyNovellib.story import (
    Emotion,
    Move,
    AddCharacter,
    RemoveCharacter,
    ChangeScene,
    Enter,
    Exit
)


class Engine:

    def __init__(self):

        pygame.init()
        pygame.mixer.init()
        self.clock = pygame.time.Clock()
        self.canvas = None
        self.screen = None
        self.background = None

        self.running = False

        self.font = pygame.font.Font(None, 42)

        pygame.mixer.music.set_volume(0.5)

    def run(self, canvas, story):

        self._load_canvas(canvas)

        self.running = True

        for action in story:

            if not self.running:
                break

            # Despacha cada Action da história para o executor certo.
            # Ações fora dessa lista são ignoradas (sem quebrar a história).

            if isinstance(action, Dialogue):

                self.execute_dialogue(action)

            elif isinstance(action, Emotion):

                self.execute_emotion(action)

            elif isinstance(action, Move):

                self.execute_move(action)

            elif isinstance(action, AddCharacter):

                self.execute_add_character(action)

            elif isinstance(action, RemoveCharacter):

                self.execute_remove_character(action)

            elif isinstance(action, ChangeScene):

                self.execute_change_scene(action)

            elif isinstance(action, Enter):

                self.execute_enter(action)

            elif isinstance(action, Exit):

                self.execute_exit(action)

        self.running = False

        pygame.quit()

    # Carrega uma cena (background, título da janela e música).
    # Usado tanto no início do run() quanto ao trocar de cena (ChangeScene).
    def _load_canvas(self, canvas):

        self.canvas = canvas

        self.screen = pygame.display.set_mode(
            canvas.tamanho
        )

        pygame.display.set_caption(
            canvas.nome
        )

        self.background = pygame.image.load(
            canvas.imagem
        ).convert()

        self.background = pygame.transform.scale(
            self.background,
            canvas.tamanho
        )

        if canvas.music:

            pygame.mixer.music.load(
                canvas.music
            )

            pygame.mixer.music.play(-1)

        else:

            pygame.mixer.music.stop()

    def execute_dialogue(self, dialogue):

        character = dialogue.character

        character.is_speaking = True

        visible_text = ""

        text_finished = False
        delay_started = False
        delay_start = None

        text_start = pygame.time.get_ticks()

        if dialogue.dub:

            pygame.mixer.music.load(dialogue.dub)
            pygame.mixer.music.play()

        while self.running:

            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():

                if event.type == pygame.QUIT:

                    self.running = False
                    return

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_SPACE:

                        if not text_finished:

                            visible_text = dialogue.text
                            text_finished = True

                        elif dialogue.delay is None:

                            self.finish_dialogue(character)
                            return

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1:

                        if not text_finished:

                            visible_text = dialogue.text
                            text_finished = True

                        elif dialogue.delay is None:

                            self.finish_dialogue(character)
                            return

            # --------------------------------
            # TEXTO SENDO ESCRITO
            # --------------------------------

            if not text_finished:

                elapsed = current_time - text_start

                if dialogue.speed <= 0:

                    characters_to_show = len(dialogue.text)

                else:

                    characters_to_show = int(
                        elapsed / (dialogue.speed * 1000)
                    )

                visible_text = dialogue.text[
                    :characters_to_show
                ]

                if len(visible_text) >= len(dialogue.text):

                    visible_text = dialogue.text
                    text_finished = True

            # --------------------------------
            # TEXTO TERMINOU
            # --------------------------------

            if text_finished:

                # Se existe dublagem,
                # espera ela terminar primeiro.

                if dialogue.dub:

                    if pygame.mixer.music.get_busy():

                        delay_started = False

                    else:

                        if dialogue.delay is not None:

                            if not delay_started:

                                delay_started = True
                                delay_start = current_time

                        else:

                            delay_started = False

                else:

                    if dialogue.delay is not None:

                        if not delay_started:

                            delay_started = True
                            delay_start = current_time

            # --------------------------------
            # DELAY AUTOMÁTICO
            # --------------------------------

            if (
                text_finished
                and dialogue.delay is not None
                and delay_started
            ):

                elapsed_delay = (
                    current_time - delay_start
                )

                if elapsed_delay >= dialogue.delay * 1000:

                    self.finish_dialogue(character)
                    return

            # --------------------------------
            # DESENHAR
            # --------------------------------

            self.draw_scene()

            self.draw_dialogue(
                character,
                visible_text
            )

            pygame.display.flip()

            self.clock.tick(60)

        self.finish_dialogue(character)
    def finish_dialogue(self, character):

        character.is_speaking = False

    # Troca a emoção atual do personagem (reaproveita Character.emotion,
    # que já valida se a emoção foi cadastrada).
    def execute_emotion(self, action):

        action.character.emotion(action.name)

        self.render()

    # Atualiza posição/escala/offset de um personagem já presente na cena.
    def execute_move(self, action):

        self.canvas.move_character(
            action.character,
            position=action.position,
            scale=action.scale,
            offset_x=action.offset_x,
            offset_y=action.offset_y
        )

        self.render()

    # Adiciona um personagem à cena durante a execução da história
    # (reaproveita Canvas.add_character).
    def execute_add_character(self, action):

        self.canvas.add_character(
            action.character,
            action.position,
            scale=action.scale,
            offset_x=action.offset_x,
            offset_y=action.offset_y
        )

        self.render()

    # Remove um personagem da cena durante a execução da história.
    def execute_remove_character(self, action):

        self.canvas.remove_character(action.character)

        self.render()

    # Troca a cena atual (sem transição visual ainda).
    def execute_change_scene(self, action):

        self._load_canvas(action.canvas)

        self.render()

    # Entrada narrativa de um personagem (reaproveita Canvas.add_character).
    def execute_enter(self, action):

        self.canvas.add_character(
            action.character,
            action.position,
            scale=action.scale,
            offset_x=action.offset_x,
            offset_y=action.offset_y
        )

        self.render()

    # Saída narrativa de um personagem (reaproveita Canvas.remove_character).
    def execute_exit(self, action):

        self.canvas.remove_character(action.character)

        self.render()

    # Desenha e mostra a tela imediatamente. Usado por ações que mudam
    # a cena mas não têm loop próprio de desenho (diferente de Dialogue,
    # que já se redesenha sozinho a cada frame).
    def render(self):

        self.draw_scene()
        pygame.display.flip()

    def draw_scene(self):

        self.screen.blit(
            self.background,
            (0, 0)
        )

        self.draw_characters()

    def draw_characters(self):

        for data in self.canvas.characters.values():

            character = data["character"]
            position = data["position"]

            if character.current_emotion is None:
                continue

            emotion = character.emotions[
                character.current_emotion
            ]

            if character.is_speaking:

                image_path = emotion["talking"]

                if image_path is None:
                    image_path = emotion["idle"]

            else:

                image_path = emotion["idle"]

            sprite = pygame.image.load(
                image_path
            ).convert_alpha()

            scale = data["scale"]

            original_width, original_height = (
                sprite.get_size()
            )

            width = int(
                original_width * scale
            )

            height = int(
                original_height * scale
            )

            sprite = pygame.transform.scale(
                sprite,
                (width, height)
            )

            x_positions = {
                1: 0.25,
                2: 0.50,
                3: 0.75
            }

            center_x = int(
                self.screen.get_width()
                * x_positions[position]
            )

            x = center_x - sprite.get_width() // 2

            y = (
                self.screen.get_height()
                - sprite.get_height()
            )

            x += data["offset_x"]
            y += data["offset_y"]

            self.screen.blit(
                sprite,
                (x, y)
            )

    def draw_dialogue(self, character, text):

        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        box_width = screen_width - 160
        box_height = 180

        box_x = 80
        box_y = screen_height - box_height - 50

        box = pygame.Surface(
            (box_width, box_height),
            pygame.SRCALPHA
        )

        box.fill(
            (0, 0, 0, 200)
        )

        self.screen.blit(
            box,
            (box_x, box_y)
        )

        name_surface = self.font.render(
            character.nome,
            True,
            (255, 255, 255)
        )

        text_surface = self.font.render(
            text,
            True,
            (255, 255, 255)
        )

        self.screen.blit(
            name_surface,
            (
                box_x + 30,
                box_y + 20
            )
        )

        self.screen.blit(
            text_surface,
            (
                box_x + 30,
                box_y + 70
            )
        )