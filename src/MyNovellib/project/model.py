# Modelo de dados de um projeto MyNovel (project.mynovel). Puro
# Python -- sem pygame, sem janela, sem renderização, sem execução de
# história. Representa só o que um projeto "é", não como ele roda.

# Formato/versão do arquivo de projeto. `version` viaja com o projeto
# desde já pra permitir migração no futuro (ver Waystone de
# serialização) -- nenhuma migração é feita ainda, só o campo existe.
PROJECT_FORMAT = "mynovel"
CURRENT_FORMAT_VERSION = 1


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
