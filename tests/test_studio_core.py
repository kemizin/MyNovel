# Teste pequeno, sem dependências externas, sem tkinter.
# Roda com: .venv/Scripts/python.exe tests/test_studio_core.py
#
# Hardening, Waystones "studio core project lifecycle" e "studio core
# content editing": StudioCore concentra a lógica de negócio do Studio
# (validar/criar/carregar/salvar projeto, editar personagem/cena) sem
# nenhuma dependência de Tkinter -- prova de que uma interface
# diferente (uma futura versão Web, por exemplo) conseguiria
# reaproveitar essa lógica sem reescrevê-la.

import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.studio.core import StudioCore, StudioError, _slugify, _generate_key
from src.MyNovellib.project.model import Project
from src.MyNovellib.project.character_data import CharacterData
from src.MyNovellib.project.scene_data import SceneData

# --- _slugify/_generate_key: a chave interna de um personagem/cena/
# história novo, derivada do nome (minúsculas, sem acento, sem
# espaço) -- sem isso, nada dá pra criar só clicando. ---
assert _slugify("Mika") == "mika"
assert _slugify("João da Silva") == "joao_da_silva"
assert _slugify("  Espaços   Extras  ") == "espacos_extras"
assert _slugify("!!!") == ""  # só pontuação -- quem chama usa o fallback
assert _slugify("") == ""

assert _generate_key("Mika", existing_keys=set(), fallback="personagem") == "mika"
assert _generate_key("Mika", existing_keys={"mika"}, fallback="personagem") == "mika_2"
assert _generate_key("Mika", existing_keys={"mika", "mika_2"}, fallback="personagem") == "mika_3"
assert _generate_key("!!!", existing_keys=set(), fallback="personagem") == "personagem"

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

    # --- add_emotion/remove_emotion: mexe em CharacterData de
    # verdade, sem UI nenhuma envolvida ---
    mika = CharacterData("Mika")
    mika.add_emotion("normal", idle="assets/characters/mika/normal_idle.png")
    core.project.characters["mika"] = mika
    core.dirty = False

    core.add_emotion("mika", "feliz", idle="assets/backgrounds/praca.png")
    assert "feliz" in mika.emotions
    assert core.dirty is True

    try:
        core.add_emotion("mika", "", idle="x.png")
        assert False, "esperava StudioError (nome vazio)"
    except StudioError:
        pass

    try:
        core.add_emotion("mika", "triste", idle="")
        assert False, "esperava StudioError (idle vazio)"
    except StudioError:
        pass

    core.remove_emotion("mika", "feliz")
    assert "feliz" not in mika.emotions

    # --- create_character: nasce sem emoção nenhuma (mesmo estado que
    # CharacterData(nome) já tem) -- quem quiser a primeira emoção usa
    # add_emotion() logo em seguida ---
    core.dirty = False
    chave = core.create_character("Novo Personagem")

    assert chave == "novo_personagem"
    assert core.project.characters[chave].name == "Novo Personagem"
    assert core.project.characters[chave].emotions == {}
    assert core.dirty is True

    # nome repetido gera uma chave diferente, não sobrescreve
    outra_chave = core.create_character("Novo Personagem")
    assert outra_chave == "novo_personagem_2"
    assert len(core.project.characters) == 3  # mika + os dois novos

    try:
        core.create_character("")
        assert False, "esperava StudioError (nome vazio)"
    except StudioError:
        pass

    # --- apply_scene_field: mexe em SceneCharacter de verdade,
    # incluindo a validação que agora mora lá (position/scale) ---
    praca = SceneData(name="praca", background="assets/backgrounds/praca.png")
    placement = praca.add_character("mika", position=2, scale=0.5)
    core.project.scenes["praca"] = praca
    core.dirty = False

    core.apply_scene_field("praca", 0, "scale", "0.8", float)
    assert placement.scale == 0.8
    assert core.dirty is True

    try:
        core.apply_scene_field("praca", 0, "position", "99", int)
        assert False, "esperava StudioError (position fora de 1/2/3)"
    except StudioError:
        pass

    try:
        core.apply_scene_field("praca", 0, "scale", "abc", float)
        assert False, "esperava StudioError (não é número)"
    except StudioError:
        pass

    assert placement.scale == 0.8  # nenhum dos erros acima mudou o valor

    # index fora do range é no-op silencioso, não erro
    core.apply_scene_field("praca", 99, "scale", "0.1", float)

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print("OK: StudioCore cria/carrega/salva projeto e edita personagem/cena, sem nenhuma dependência de Tkinter")
