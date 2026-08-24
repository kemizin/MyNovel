# Registro de assets do projeto: só METADADOS (id, tipo, caminho).
# NUNCA carrega o arquivo de verdade (PNG/MP3/...) -- quem sabe abrir
# um arquivo de asset é o Runtime (Engine), não o Project Data.

# Tipos de asset que a MyNovel já entende hoje. `type` aceita
# qualquer string (não é uma trava rígida) -- isto é documentação
# executável, não validação.
ASSET_TYPES = (
    "character_sprite",
    "background",
    "music",
    "voice",
    "sfx",
)


class Asset:

    def __init__(self, id, type, path):

        if not id or not str(id).strip():
            raise ValueError("Asset precisa de um id não vazio.")

        if not path or not str(path).strip():
            raise ValueError(f"Asset {id!r} precisa de um path não vazio.")

        self.id = id
        self.type = type
        self.path = path

    def to_dict(self):
        return {"id": self.id, "type": self.type, "path": self.path}

    @classmethod
    def from_dict(cls, data):
        return cls(id=data["id"], type=data["type"], path=data["path"])

    def __eq__(self, other):

        if not isinstance(other, Asset):
            return NotImplemented

        return (self.id, self.type, self.path) == (other.id, other.type, other.path)

    def __repr__(self):
        return f"Asset(id={self.id!r}, type={self.type!r}, path={self.path!r})"
