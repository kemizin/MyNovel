# Teste pequeno, sem dependências externas, sem tkinter.
# Roda com: .venv/Scripts/python.exe tests/test_studio_core.py
#
# Hardening, Waystone "studio core project lifecycle": StudioCore
# concentra a lógica de negócio do Studio (validar/criar/carregar/
# salvar projeto) sem nenhuma dependência de Tkinter -- prova de que
# uma interface diferente (uma futura versão Web, por exemplo)
# conseguiria reaproveitar essa lógica sem reescrevê-la.

import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.studio.core import StudioCore, StudioError
from src.MyNovellib.project.model import Project

# --- importar StudioCore não traz tkinter (nem pygame) de brinde ---
assert "tkinter" not in sys.modules
assert "pygame" not in sys.modules

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_studiocore_")
try:
    core = StudioCore()

    assert core.project is None
    assert core.project_path is None
    assert core.dirty is False

    # --- create_new_project: sucesso ---
    core.create_new_project("Projeto Core", tmp_dir, "800", "600")

    assert core.project is not None
    assert core.project.name == "Projeto Core"
    assert core.project.resolution == (800, 600)
    assert core.project_path is not None
    assert core.dirty is False

    # --- create_new_project: cada validação levanta StudioError, não
    # levanta exceção crua nem imprime nada -- quem chama decide como
    # mostrar a mensagem ---
    for args, motivo in (
        (("", tmp_dir, "800", "600"), "nome vazio"),
        (("Outro", "", "800", "600"), "location vazio"),
        (("Outro", tmp_dir, "abc", "600"), "largura inválida"),
        (("Outro", tmp_dir, "800", "0"), "altura inválida"),
    ):
        try:
            core.create_new_project(*args)
            assert False, f"esperava StudioError ({motivo})"
        except StudioError:
            pass

    # criar em cima da mesma pasta (já existe e não está vazia)
    try:
        core.create_new_project("Projeto Core", tmp_dir, "800", "600")
        assert False, "esperava StudioError (pasta já existe)"
    except StudioError:
        pass

    # nenhum desses erros trocou o projeto que já estava carregado
    assert core.project.name == "Projeto Core"

    # --- load_project: sucesso e erro ---
    core2 = StudioCore()
    core2.load_project(core.project_path)
    assert core2.project.name == "Projeto Core"
    assert core2.dirty is False

    try:
        StudioCore().load_project(os.path.join(tmp_dir, "nao_existe.mynovel"))
        assert False, "esperava StudioError (arquivo não existe)"
    except StudioError:
        pass

    arquivo_invalido = os.path.join(tmp_dir, "invalido.mynovel")
    with open(arquivo_invalido, "w", encoding="utf-8") as f:
        f.write("isso não é json válido")

    try:
        StudioCore().load_project(arquivo_invalido)
        assert False, "esperava StudioError (JSON inválido)"
    except StudioError:
        pass

    # --- save_project_to: salva de verdade, limpa dirty, redireciona
    # loaded_from ---
    core.dirty = True
    novo_caminho = os.path.join(tmp_dir, "outro_nome.mynovel")
    core.save_project_to(novo_caminho)

    assert core.project_path == os.path.abspath(novo_caminho)
    assert core.project.loaded_from == os.path.dirname(os.path.abspath(novo_caminho))
    assert core.dirty is False

    reloaded = Project.load(novo_caminho)
    assert reloaded.name == "Projeto Core"

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print("OK: StudioCore cria/carrega/salva projeto sem nenhuma dependência de Tkinter")
