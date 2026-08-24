# Modelo de dados de um projeto MyNovel (project.mynovel). Puro
# Python -- sem pygame, sem janela, sem renderização, sem execução de
# história. Representa só o que um projeto "é", não como ele roda.

import json
import os

from src.MyNovellib.project.assets import Asset
from src.MyNovellib.project.character_data import CharacterData
from src.MyNovellib.project.scene_data import SceneData
from src.MyNovellib.project.story_data import StoryData

# Formato/versão do arquivo de projeto. `version` viaja com o projeto
# desde já pra permitir migração no futuro -- nenhuma migração é
# feita ainda (ver Waystone de serialização), só o campo existe e é
# checado.
PROJECT_FORMAT = "mynovel"
CURRENT_FORMAT_VERSION = 1


# Converte um valor guardado em scenes/stories/assets pra algo que o
# json consiga escrever: usa to_dict() se existir (SceneData,
# CharacterData, Asset dos próximos Waystones já vão ter), senão
# assume que já é um dict simples.
def _to_serializable(value):

    if hasattr(value, "to_dict"):
        return value.to_dict()

    return value


class Project:

    def __init__(
        self,
        name,
        resolution=(1920, 1080),
        version=CURRENT_FORMAT_VERSION
    ):

        if not name or not str(name).strip():
            raise ValueError("Project precisa de um nome não vazio.")

        if len(resolution) != 2 or any(v <= 0 for v in resolution):
            raise ValueError(
                f"resolution inválida: {resolution!r} "
                f"(esperado um par de números positivos, ex: (1920, 1080))."
            )

        self.name = name
        self.resolution = (int(resolution[0]), int(resolution[1]))
        self.version = version

        # Guardados por nome/id -> dado, pra busca O(1).
        self.scenes = {}
        self.stories = {}
        self.assets = {}
        self.characters = {}

        # pasta de onde o projeto foi carregado (setado por load()) --
        # usado por create_runtime() pra resolver caminhos relativos
        # de asset. None pra um Project montado em memória.
        self.loaded_from = None

    def __repr__(self):

        return (
            f"Project(name={self.name!r}, resolution={self.resolution!r}, "
            f"version={self.version!r})"
        )

    # --- Assets ---------------------------------------------------------
    #
    # Só REGISTRO (metadados: id/type/path) -- o Project nunca carrega o
    # arquivo de asset de verdade (isso é trabalho do Runtime).

    def add_asset(self, asset):

        self.assets[asset.id] = asset
        return asset

    def remove_asset(self, asset_id):

        if asset_id not in self.assets:
            raise KeyError(
                f"Asset {asset_id!r} não está registrado neste projeto."
            )

        del self.assets[asset_id]

    def get_asset(self, asset_id):

        if asset_id not in self.assets:
            raise KeyError(
                f"Asset {asset_id!r} não está registrado neste projeto."
            )

        return self.assets[asset_id]

    # --- Serialização -------------------------------------------------

    def to_dict(self):

        return {
            "format": PROJECT_FORMAT,
            "version": self.version,
            "name": self.name,
            "resolution": list(self.resolution),
            "scenes": {
                key: _to_serializable(value)
                for key, value in self.scenes.items()
            },
            "stories": {
                key: _to_serializable(value)
                for key, value in self.stories.items()
            },
            "assets": {
                key: _to_serializable(value)
                for key, value in self.assets.items()
            },
            "characters": {
                key: _to_serializable(value)
                for key, value in self.characters.items()
            },
        }

    @classmethod
    def from_dict(cls, data):

        if data.get("format") != PROJECT_FORMAT:
            raise ValueError(
                f"Arquivo não é um projeto MyNovel válido "
                f"(esperado format={PROJECT_FORMAT!r}, veio {data.get('format')!r})."
            )

        if "version" not in data:
            raise ValueError("Arquivo de projeto sem campo 'version'.")

        if data["version"] > CURRENT_FORMAT_VERSION:
            raise ValueError(
                f"Este projeto foi salvo com a versão de formato "
                f"{data['version']}, mais nova que a suportada por esta "
                f"biblioteca ({CURRENT_FORMAT_VERSION}). Atualize a MyNovel "
                f"pra abrir este projeto."
            )

        if "name" not in data:
            raise ValueError("Arquivo de projeto sem campo 'name'.")

        project = cls(
            name=data["name"],
            resolution=tuple(data.get("resolution", (1920, 1080))),
            version=data["version"]
        )

        # scenes/stories/assets/characters já têm classes de dado de
        # verdade -- reconstrói objetos, não deixa como dict cru.
        project.stories = {
            key: StoryData.from_dict(value)
            for key, value in data.get("stories", {}).items()
        }

        project.scenes = {
            key: SceneData.from_dict(value)
            for key, value in data.get("scenes", {}).items()
        }

        project.assets = {
            key: Asset.from_dict(value)
            for key, value in data.get("assets", {}).items()
        }

        project.characters = {
            key: CharacterData.from_dict(value)
            for key, value in data.get("characters", {}).items()
        }

        return project

    # Escreve o projeto em `path` como JSON. Grava num arquivo
    # temporário e só troca no final (os.replace é atômico), pra não
    # deixar um project.mynovel existente corrompido se algo falhar
    # no meio da escrita.
    def save(self, path):

        path = str(path)
        tmp_path = path + ".tmp"

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

        os.replace(tmp_path, path)

    @classmethod
    def load(cls, path):

        path = str(path)

        if not os.path.isfile(path):
            raise FileNotFoundError(f"Arquivo de projeto não encontrado: {path}")

        with open(path, "r", encoding="utf-8") as f:

            try:
                data = json.load(f)

            except json.JSONDecodeError as error:
                raise ValueError(
                    f"Arquivo de projeto inválido (JSON malformado): {path}"
                ) from error

        project = cls.from_dict(data)
        project.loaded_from = os.path.dirname(os.path.abspath(path))

        return project

    # --- Runtime ---------------------------------------------------------
    #
    # Import de src.MyNovellib.project.runtime_loader fica de propósito
    # DENTRO do método (não no topo do arquivo): model.py continua sem
    # importar pygame só de existir a classe Project -- só quando
    # create_runtime() é de fato CHAMADO é que a camada de Runtime
    # (Character/Canvas/Engine) entra em cena.
    def create_runtime(self, directory=None):

        from src.MyNovellib.project.runtime_loader import create_runtime

        directory = directory or self.loaded_from or os.getcwd()

        return create_runtime(self, directory)
