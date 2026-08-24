# Project Runtime Loading: a ponte entre um Project (dados) e a
# Engine que já existe. NÃO é uma Engine paralela -- só monta
# Character/Canvas/Actions de Runtime a partir dos dados do projeto e
# entrega pra Engine de verdade (src/MyNovellib/engine.py) rodar.
#
#     Project -> resolver assets -> Characters -> Canvas -> Actions -> Engine
#
# Ao contrário do resto de src/MyNovellib/project/ (que nunca importa
# pygame), este módulo importa Character/Canvas/Engine -- por isso
# fica separado do resto: é a camada de CONVERSÃO, não de dados.

import os

from src.MyNovellib.character import Character
from src.MyNovellib.scene import Canvas
from src.MyNovellib.engine import Engine
from src.MyNovellib.project.action_factory import build_story


# Resolve um caminho de asset guardado no projeto (relativo à pasta
# do projeto) pra um caminho que funcione não importa qual seja o
# diretório de trabalho atual do processo. Caminhos absolutos e None
# passam direto.
def _resolve_path(base_dir, path):

    if path is None or os.path.isabs(path):
        return path

    return os.path.join(base_dir, path)


# CharacterData -> Character (Runtime), resolvendo os caminhos de
# sprite contra `base_dir`.
def _build_character(character_data, base_dir):

    character = Character(character_data.name)

    for emotion_name, sprites in character_data.emotions.items():

        character.add_emotion(
            emotion_name,
            idle=_resolve_path(base_dir, sprites["idle"]),
            talking=_resolve_path(base_dir, sprites.get("talking")),
        )

    return character


# SceneData -> Canvas (Runtime): resolve background/música, aplica os
# personagens presentes desde o início (com a emoção inicial de cada
# um, se informada). `characters` já precisa ter os Character
# (Runtime) correspondentes construídos.
def _build_canvas(scene_data, project_resolution, characters, base_dir):

    width, height = scene_data.resolution or project_resolution

    canvas = Canvas(
        scene_data.name,
        _resolve_path(base_dir, scene_data.background),
        width,
        height,
        music=_resolve_path(base_dir, scene_data.music),
    )

    for placement in scene_data.characters:

        character = characters[placement.character]

        canvas.add_character(
            character,
            placement.position,
            scale=placement.scale,
            offset_x=placement.offset_x,
            offset_y=placement.offset_y,
        )

        if placement.emotion is not None:
            character.emotion(placement.emotion)

    return canvas


def _only_key_or_raise(mapping, kind):

    if len(mapping) == 1:
        return next(iter(mapping))

    raise ValueError(
        f"Não foi possível decidir qual {kind} rodar automaticamente "
        f"({len(mapping)} disponíve(l/is): {', '.join(sorted(mapping)) or 'nenhuma'}) "
        f"-- informe explicitamente em runtime.run(...)."
    )


# Reúne tudo que um Project sabe (characters/scenes/stories) já
# convertido pra objetos de Runtime, e sabe rodar usando a Engine
# existente.
class ProjectRuntime:

    def __init__(self, project, directory):

        self.project = project
        self.directory = directory

        self.characters = {
            name: _build_character(data, directory)
            for name, data in project.characters.items()
        }

        self.scenes = {
            name: _build_canvas(data, project.resolution, self.characters, directory)
            for name, data in project.scenes.items()
        }

        self.stories = {
            name: build_story(data, self.characters)
            for name, data in project.stories.items()
        }

        self.engine = Engine()

    # Roda o projeto pela Engine existente. Sem `scene`/`story`, só
    # funciona automaticamente se o projeto tiver exatamente uma cena
    # e uma história (o caso comum de uma demo pequena) -- projetos
    # com mais de uma precisam dizer qual rodar.
    def run(self, scene=None, story=None):

        scene_name = scene or _only_key_or_raise(self.scenes, "cena")
        story_name = story or _only_key_or_raise(self.stories, "história")

        canvas = self.scenes[scene_name]
        actions = self.stories[story_name]

        self.engine.run(canvas, actions)


def create_runtime(project, directory):
    return ProjectRuntime(project, directory)
