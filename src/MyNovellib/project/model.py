# Modelo de dados de um projeto MyNovel (project.mynovel). Puro
# Python -- sem pygame, sem janela, sem renderização, sem execução de
# história. Representa só o que um projeto "é", não como ele roda.

import json
import os

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

        # Guardados por nome/id -> dado, pra busca O(1). As classes de
        # dado (SceneData, StoryData, Asset, ...) chegam nos próximos
        # Waystones -- por enquanto estes dicts ficam vazios.
        self.scenes = {}
        self.stories = {}
        self.assets = {}

    def __repr__(self):

        return (
            f"Project(name={self.name!r}, resolution={self.resolution!r}, "
            f"version={self.version!r})"
        )

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

        project.scenes = dict(data.get("scenes", {}))
        project.stories = dict(data.get("stories", {}))
        project.assets = dict(data.get("assets", {}))

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

        return cls.from_dict(data)
