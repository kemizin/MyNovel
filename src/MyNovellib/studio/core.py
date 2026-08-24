# Studio Core: a lógica de negócio do MyNovel Studio, sem nenhuma
# dependência de Tkinter -- só o Project System
# (src/MyNovellib/project/). StudioApp (app.py) é quem sabe de menu,
# botão, diálogo, messagebox; StudioCore só sabe manipular um Project
# e devolver sucesso ou um StudioError com mensagem pronta pra
# mostrar.
#
# Motivo de existir: antes desta separação, validar/criar/carregar/
# salvar um projeto e chamar messagebox.showerror(...) eram a mesma
# linha de código dentro de StudioApp -- o que funciona, mas significa
# que nenhuma outra interface (uma futura versão Web do Studio, por
# exemplo) conseguiria reaproveitar essa lógica sem reescrevê-la. Com
# o Core isolado, qualquer interface (Tkinter hoje, outra amanhã) só
# precisa: chamar o método, mostrar a mensagem se vier StudioError,
# atualizar a tela se não vier.

import os
import re
import unicodedata

from src.MyNovellib.project.model import Project
from src.MyNovellib.project.directory import create_project
from src.MyNovellib.project.character_data import CharacterData
from src.MyNovellib.project.scene_data import SceneData
from src.MyNovellib.project.story_data import StoryData, ActionData


# Erro de uma operação do Core -- a mensagem já vem pronta pra
# mostrar ao usuário (messagebox, toast, o que a interface usar).
class StudioError(Exception):
    pass


# Personagem/cena/história nova precisa de uma chave interna (a
# criada à mão em código sempre foi algo tipo "mika") -- gerada a
# partir do nome: minúsculas, sem acento, só [a-z0-9_]. Se colidir com
# uma chave já existente, tenta "_2", "_3", ... até achar uma livre.
def _slugify(text):

    text = unicodedata.normalize("NFKD", text or "")
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)

    return text.strip("_")


def _generate_key(name, existing_keys, fallback):

    base = _slugify(name) or fallback

    if base not in existing_keys:
        return base

    n = 2
    while f"{base}_{n}" in existing_keys:
        n += 1

    return f"{base}_{n}"


class StudioCore:

    def __init__(self):

        self.project = None
        self.project_path = None  # caminho exato do .mynovel aberto/salvo
        self.dirty = False

    # Cria o projeto de verdade: valida os campos, reaproveita
    # create_project() (Project System, sem duplicar nenhuma lógica de
    # criação) e já carrega o projeto recém-criado. Levanta StudioError
    # em qualquer passo inválido -- quem chama decide como mostrar.
    def create_new_project(self, name, location, width, height):

        name = (name or "").strip()
        location = (location or "").strip()

        if not name:
            raise StudioError("Informe um nome para o projeto.")

        if not location:
            raise StudioError("Informe onde o projeto deve ser criado.")

        try:
            width = int(width)
            height = int(height)

            if width <= 0 or height <= 0:
                raise ValueError

        except (TypeError, ValueError):
            raise StudioError(
                "Largura e altura precisam ser números inteiros positivos."
            )

        project_path = os.path.join(location, name)

        try:
            directory = create_project(project_path, name=name, resolution=(width, height))

        except FileExistsError as error:
            raise StudioError(f"Não foi possível criar o projeto:\n\n{error}")

        self.load_project(directory.project_file)

    # Carrega um project.mynovel pelo caminho. Reaproveita
    # Project.load() -- nenhuma lógica de carregamento duplicada aqui.
    def load_project(self, path):

        try:
            project = Project.load(path)

        except (FileNotFoundError, ValueError) as error:
            raise StudioError(f"Não foi possível abrir o projeto:\n\n{error}")

        self.project = project
        self.project_path = os.path.abspath(path)
        self.dirty = False

    # Onde o salvamento de fato acontece. Usa Project.save()
    # diretamente (Project System) -- nenhum sistema de persistência
    # paralelo.
    def save_project_to(self, path):

        self.project.save(path)

        self.project_path = os.path.abspath(path)
        self.project.loaded_from = os.path.dirname(self.project_path)

        self.dirty = False

    # --- Character -------------------------------------------------------

    # Cria um CharacterData vazio (sem emoção nenhuma ainda -- mesmo
    # estado que CharacterData(nome) já tem em Python; a primeira
    # emoção entra depois via add_emotion(), acima). Devolve a chave
    # gerada, pra quem chamou já poder selecionar/abrir o personagem
    # recém-criado.
    def create_character(self, name):

        name = (name or "").strip()

        try:
            character = CharacterData(name)

        except ValueError as error:
            raise StudioError(str(error))

        key = _generate_key(name, self.project.characters, fallback="personagem")
        self.project.characters[key] = character
        self.dirty = True

        return key

    # Remove o personagem -- mas nunca em cascata: se ele estiver
    # colocado em alguma cena (SceneCharacter.character) ou citado em
    # alguma Action de história (fields["character"]), bloqueia com
    # StudioError dizendo onde, em vez de apagar e deixar uma
    # referência pendurada (o mesmo tipo de problema que o hardening
    # de validação, Fase A, fechou pro position/scale).
    def delete_character(self, character_key):

        if character_key not in self.project.characters:
            raise StudioError(f"Personagem {character_key!r} não existe neste projeto.")

        usos = []

        for scene in self.project.scenes.values():
            if any(p.character == character_key for p in scene.characters):
                usos.append(f'cena "{scene.name}"')

        for story in self.project.stories.values():
            if any(a.fields.get("character") == character_key for a in story.actions):
                usos.append(f'história "{story.name}"')

        if usos:
            raise StudioError(
                "Não é possível remover: personagem usado em " + ", ".join(usos) + "."
            )

        del self.project.characters[character_key]
        self.dirty = True

    # Reaproveita CharacterData.add_emotion() (Project System) e toda
    # a validação de lá (idle e name não vazios) -- o Core não valida
    # nada por conta própria, só traduz o ValueError em StudioError.
    def add_emotion(self, character_key, name, idle, talking=""):

        data = self.project.characters[character_key]

        name = (name or "").strip()
        idle = (idle or "").strip()
        talking = (talking or "").strip() or None

        try:
            data.add_emotion(name, idle=idle, talking=talking)

        except ValueError as error:
            raise StudioError(str(error))

        self.dirty = True

    def remove_emotion(self, character_key, emotion_name):

        data = self.project.characters[character_key]

        del data.emotions[emotion_name]
        self.dirty = True

    # --- Scene -------------------------------------------------------

    # Cria um SceneData novo. `background` é opcional (SceneData aceita
    # None -- uma cena sem fundo ainda renderiza, só mostra o canvas
    # vazio) mas normalmente vem preenchido: diferente do personagem,
    # hoje não existe campo no Scene Editor pra trocar o background
    # depois da criação. Devolve a chave gerada.
    def create_scene(self, name, background=""):

        name = (name or "").strip()
        background = (background or "").strip() or None

        try:
            scene = SceneData(name=name, background=background)

        except ValueError as error:
            raise StudioError(str(error))

        key = _generate_key(name, self.project.scenes, fallback="cena")
        self.project.scenes[key] = scene
        self.dirty = True

        return key

    # Remove a cena. Ao contrário de personagem, nada no modelo de
    # dados guarda uma referência a uma cena por chave (uma história
    # não "aponta" pra uma cena -- a escolha de qual cena/história
    # rodar é feita por fora, em runtime.run(scene=..., story=...)) --
    # não há o que bloquear aqui além da cena existir.
    def delete_scene(self, scene_key):

        if scene_key not in self.project.scenes:
            raise StudioError(f"Cena {scene_key!r} não existe neste projeto.")

        del self.project.scenes[scene_key]
        self.dirty = True

    # `parse` só faz a conversão de tipo (str -> int/float, tipicamente
    # vindo de um Entry) -- quem valida o VALOR (position precisa ser
    # 1/2/3, scale precisa ser > 0) é o próprio SceneCharacter
    # (property setter, ver project/scene_data.py). `index` fora do
    # range de personagens da cena é no-op silencioso -- mesmo
    # comportamento de sempre, não é erro de usuário.
    def apply_scene_field(self, scene_key, index, field, raw_value, parse):

        data = self.project.scenes[scene_key]

        if index >= len(data.characters):
            return

        placement = data.characters[index]

        try:
            valor = parse(raw_value)
            setattr(placement, field, valor)

        except (TypeError, ValueError) as error:
            raise StudioError(f"Valor inválido em {field}: {error}")

        self.dirty = True

    # --- Story -------------------------------------------------------

    # Cria uma StoryData vazia (sem Action nenhuma ainda -- não existe
    # Story Editor nesta fase pra preencher o conteúdo). Devolve a
    # chave gerada.
    def create_story(self, name):

        name = (name or "").strip()

        try:
            story = StoryData(name=name)

        except ValueError as error:
            raise StudioError(str(error))

        key = _generate_key(name, self.project.stories, fallback="historia")
        self.project.stories[key] = story
        self.dirty = True

        return key

    # Remove a história. Assim como cena, nada no modelo de dados
    # referencia uma história por chave -- não há o que bloquear além
    # dela existir.
    def delete_story(self, story_key):

        if story_key not in self.project.stories:
            raise StudioError(f"História {story_key!r} não existe neste projeto.")

        del self.project.stories[story_key]
        self.dirty = True

    # Adiciona uma Action ao final da história. Reaproveita
    # StoryData.add_action() (que por sua vez usa ActionData -- tipo
    # suportado e campos obrigatórios já validados lá); o Core só
    # traduz o ValueError em StudioError. Não valida que o
    # personagem citado existe -- quem monta os campos (o diálogo Add
    # Action, no Studio) só deixa escolher personagens que já existem,
    # via combobox.
    def add_story_action(self, story_key, action_type, **fields):

        story = self.project.stories[story_key]

        try:
            story.add_action(action_type, **fields)

        except ValueError as error:
            raise StudioError(str(error))

        self.dirty = True

    # Substitui os campos da Action em `index` -- o tipo não muda
    # (trocar de tipo é remover + adicionar de novo, não editar; os
    # campos válidos são completamente diferentes por tipo). Constrói
    # uma ActionData nova pra reaproveitar a validação de campo
    # obrigatório (ActionData.__init__) em vez de mexer em
    # story.actions[index].fields direto e arriscar um dict
    # inconsistente.
    def update_story_action(self, story_key, index, **fields):

        story = self.project.stories[story_key]

        if index < 0 or index >= len(story.actions):
            raise StudioError("Action não encontrada.")

        action_type = story.actions[index].type

        try:
            story.actions[index] = ActionData(action_type, **fields)

        except ValueError as error:
            raise StudioError(str(error))

        self.dirty = True

    def remove_story_action(self, story_key, index):

        story = self.project.stories[story_key]

        if index < 0 or index >= len(story.actions):
            raise StudioError("Action não encontrada.")

        del story.actions[index]
        self.dirty = True

    # Troca a Action em `index` de lugar com a vizinha (delta=-1 pra
    # cima, +1 pra baixo). Já na ponta (não tem vizinha nessa direção)
    # é no-op silencioso, não erro -- mesmo espírito de índice fora do
    # range em apply_scene_field. Devolve o índice onde a Action
    # terminou (igual a `index` se foi no-op) -- quem chama usa isso
    # pra saber o que re-selecionar na lista.
    def move_story_action(self, story_key, index, delta):

        story = self.project.stories[story_key]

        if index < 0 or index >= len(story.actions):
            raise StudioError("Action não encontrada.")

        novo_index = index + delta

        if novo_index < 0 or novo_index >= len(story.actions):
            return index

        story.actions[index], story.actions[novo_index] = (
            story.actions[novo_index],
            story.actions[index],
        )
        self.dirty = True

        return novo_index
