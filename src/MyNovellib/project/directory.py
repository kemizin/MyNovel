# Abstração de diretório de projeto MyNovel:
#
#     MeuJogo/
#         project.mynovel
#         assets/
#         scenes/
#         stories/
#
# Sem pygame, sem janela -- só operações de arquivo/diretório.

import os

from src.MyNovellib.project.model import Project

PROJECT_FILE_NAME = "project.mynovel"

# Só as pastas estruturais de mais alto nível. Subpastas como
# assets/characters/jef/ nascem quando há conteúdo de verdade pra
# colocar nelas (Waystone de Asset Registry / importação de arquivos)
# -- criar tudo agora seria "lixo" num projeto vazio.
PROJECT_SUBDIRS = ("assets", "scenes", "stories")


class ProjectDirectory:

    def __init__(self, path):
        self.path = str(path)
        self.project = None

    @property
    def project_file(self):
        return os.path.join(self.path, PROJECT_FILE_NAME)

    def exists(self):
        return os.path.isdir(self.path) and os.path.isfile(self.project_file)

    def load(self):
        self.project = Project.load(self.project_file)
        return self.project

    def save(self, project=None):

        if project is not None:
            self.project = project

        if self.project is None:
            raise ValueError("Nenhum Project pra salvar nesta ProjectDirectory.")

        os.makedirs(self.path, exist_ok=True)
        self.project.save(self.project_file)

    def __repr__(self):
        return f"ProjectDirectory(path={self.path!r})"


# Cria um projeto MyNovel novo em `path`: o diretório, as pastas
# estruturais mínimas e o project.mynovel. Recusa criar em cima de um
# diretório que já existe e não está vazio (não sobrescreve projeto
# de ninguém por engano).
def create_project(path, name=None, resolution=(1920, 1080)):

    directory = ProjectDirectory(path)

    if os.path.isdir(directory.path) and os.listdir(directory.path):
        raise FileExistsError(
            f"'{directory.path}' já existe e não está vazio."
        )

    if name is None:
        name = os.path.basename(os.path.normpath(directory.path))

    project = Project(name=name, resolution=resolution)

    os.makedirs(directory.path, exist_ok=True)

    for subdir in PROJECT_SUBDIRS:
        os.makedirs(os.path.join(directory.path, subdir), exist_ok=True)

    directory.save(project)

    return directory
