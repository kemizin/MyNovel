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

from src.MyNovellib.project.model import Project
from src.MyNovellib.project.directory import create_project


# Erro de uma operação do Core -- a mensagem já vem pronta pra
# mostrar ao usuário (messagebox, toast, o que a interface usar).
class StudioError(Exception):
    pass


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
