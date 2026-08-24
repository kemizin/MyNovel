# Teste pequeno, sem dependências externas, sem pygame.
# Roda com: .venv/Scripts/python.exe tests/test_project_serialization.py
#
# Project System Update, Waystone 2: save/load em JSON, round trip,
# deteccao de arquivo invalido, campo de versao.

import os
import sys
import json
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.project import model
from src.MyNovellib.project.model import Project, CURRENT_FORMAT_VERSION

assert "pygame" not in sys.modules

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_")


def path(name):
    return os.path.join(tmp_dir, name)


try:
    # --- round trip basico: campos simples ---
    original = Project(name="Minha VN", resolution=(1280, 720))
    original.save(path("basico.mynovel"))

    loaded = Project.load(path("basico.mynovel"))

    assert loaded.name == original.name
    assert loaded.resolution == original.resolution
    assert loaded.version == original.version
    assert loaded.scenes == {}
    assert loaded.stories == {}
    assert loaded.assets == {}

    # --- o arquivo salvo e JSON legivel, no formato esperado ---
    with open(path("basico.mynovel"), encoding="utf-8") as f:
        raw = json.load(f)

    assert raw["format"] == "mynovel"
    assert raw["version"] == CURRENT_FORMAT_VERSION
    assert raw["name"] == "Minha VN"
    assert raw["resolution"] == [1280, 720]

    # --- round trip com scenes/stories/assets preenchidos ---
    populated = Project(name="Com Dados")
    populated.scenes["campo"] = {"name": "campo", "background": "campo.jpg"}
    populated.stories["intro"] = {"name": "intro", "actions": []}
    populated.assets["jef.idle"] = {"id": "jef.idle", "path": "jef.png"}

    populated.save(path("populado.mynovel"))
    loaded_populated = Project.load(path("populado.mynovel"))

    assert loaded_populated.scenes == populated.scenes
    assert loaded_populated.stories == populated.stories
    assert loaded_populated.assets == populated.assets

    # --- round trip preservando objetos com to_dict() (sem precisar
    # existir SceneData/CharacterData de verdade ainda) ---
    class FakeSceneData:
        def __init__(self, name):
            self.name = name
        def to_dict(self):
            return {"name": self.name, "fake": True}

    with_object = Project(name="Com Objeto")
    with_object.scenes["quarto"] = FakeSceneData("quarto")
    with_object.save(path("objeto.mynovel"))

    loaded_object = Project.load(path("objeto.mynovel"))
    assert loaded_object.scenes["quarto"] == {"name": "quarto", "fake": True}

    # --- carregar arquivo inexistente ---
    try:
        Project.load(path("nao_existe.mynovel"))
        assert False, "esperava FileNotFoundError"
    except FileNotFoundError:
        pass

    # --- JSON malformado ---
    with open(path("malformado.mynovel"), "w", encoding="utf-8") as f:
        f.write("{ isso nao e json valido")

    try:
        Project.load(path("malformado.mynovel"))
        assert False, "esperava ValueError para JSON malformado"
    except ValueError:
        pass

    # --- format errado (nao e um projeto mynovel) ---
    with open(path("formato_errado.mynovel"), "w", encoding="utf-8") as f:
        json.dump({"format": "outra_coisa", "version": 1, "name": "X"}, f)

    try:
        Project.load(path("formato_errado.mynovel"))
        assert False, "esperava ValueError para format incorreto"
    except ValueError:
        pass

    # --- sem campo version ---
    with open(path("sem_versao.mynovel"), "w", encoding="utf-8") as f:
        json.dump({"format": "mynovel", "name": "X"}, f)

    try:
        Project.load(path("sem_versao.mynovel"))
        assert False, "esperava ValueError para falta de version"
    except ValueError:
        pass

    # --- versao mais nova do que esta biblioteca suporta ---
    with open(path("versao_futura.mynovel"), "w", encoding="utf-8") as f:
        json.dump({
            "format": "mynovel",
            "version": CURRENT_FORMAT_VERSION + 1,
            "name": "Projeto do Futuro",
            "resolution": [1920, 1080],
        }, f)

    try:
        Project.load(path("versao_futura.mynovel"))
        assert False, "esperava ValueError para versao futura"
    except ValueError:
        pass

    # --- nao corromper projeto existente se a escrita falhar no meio ---
    safe = Project(name="Projeto Seguro")
    safe.save(path("seguro.mynovel"))

    with open(path("seguro.mynovel"), encoding="utf-8") as f:
        conteudo_antes = f.read()

    original_dump = model.json.dump

    def dump_que_falha(*args, **kwargs):
        raise RuntimeError("falha simulada no meio da escrita")

    model.json.dump = dump_que_falha
    try:
        try:
            safe.name = "Nome que nao deveria ser salvo"
            safe.save(path("seguro.mynovel"))
            assert False, "esperava a excecao simulada propagar"
        except RuntimeError:
            pass
    finally:
        model.json.dump = original_dump

    with open(path("seguro.mynovel"), encoding="utf-8") as f:
        conteudo_depois = f.read()

    assert conteudo_depois == conteudo_antes, (
        "o arquivo original foi corrompido por uma escrita que falhou no meio"
    )

    print("OK: Project save/load, round trip, versao e deteccao de arquivo invalido")

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)
