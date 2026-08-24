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

    # --- create_scene: background é opcional (SceneData aceita None) ---
    chave_cena = core.create_scene("Quarto", background="assets/backgrounds/quarto.png")
    assert chave_cena == "quarto"
    assert core.project.scenes[chave_cena].background == "assets/backgrounds/quarto.png"
    assert core.project.scenes[chave_cena].characters == []

    chave_cena_sem_fundo = core.create_scene("Vazia")
    assert core.project.scenes[chave_cena_sem_fundo].background is None

    try:
        core.create_scene("")
        assert False, "esperava StudioError (nome vazio)"
    except StudioError:
        pass

    # --- create_story: nasce sem Action nenhuma ---
    chave_historia = core.create_story("Introdução")
    assert chave_historia == "introducao"
    assert core.project.stories[chave_historia].actions == []

    outra_historia = core.create_story("Introdução")
    assert outra_historia == "introducao_2"

    try:
        core.create_story("")
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

    # --- delete_character: bloqueia se estiver em uso, nunca remove
    # em cascata ---
    try:
        core.delete_character("mika")  # colocada na cena "praca" acima
        assert False, "esperava StudioError (mika está na cena praca)"
    except StudioError as error:
        assert "praca" in str(error)

    assert "mika" in core.project.characters  # não removeu nada

    core.project.stories["introducao"].add_action(
        "speak", character="novo_personagem_2", text="Oi!"
    )
    try:
        core.delete_character("novo_personagem_2")
        assert False, "esperava StudioError (citada na história introducao)"
    except StudioError as error:
        assert core.project.stories["introducao"].name in str(error)

    # sem uso nenhum -- remove normalmente
    core.dirty = False
    core.delete_character("novo_personagem")
    assert "novo_personagem" not in core.project.characters
    assert core.dirty is True

    try:
        core.delete_character("nao_existe")
        assert False, "esperava StudioError (personagem não existe)"
    except StudioError:
        pass

    # --- delete_scene/delete_story: nada no modelo referencia cena ou
    # história por chave -- não há o que bloquear ---
    core.delete_scene("quarto")
    assert "quarto" not in core.project.scenes

    try:
        core.delete_scene("nao_existe")
        assert False, "esperava StudioError (cena não existe)"
    except StudioError:
        pass

    core.delete_story("introducao_2")
    assert "introducao_2" not in core.project.stories

    try:
        core.delete_story("nao_existe")
        assert False, "esperava StudioError (história não existe)"
    except StudioError:
        pass

    # --- add_story_action: reaproveita StoryData.add_action()
    # (tipo suportado + campos obrigatórios) ---
    core.create_story("Capítulo Extra")
    core.dirty = False

    core.add_story_action("capitulo_extra", "speak", character="mika", text="Oi!")
    assert len(core.project.stories["capitulo_extra"].actions) == 1
    assert core.project.stories["capitulo_extra"].actions[0].type == "speak"
    assert core.dirty is True

    core.add_story_action("capitulo_extra", "pause", duration=1.5)
    assert len(core.project.stories["capitulo_extra"].actions) == 2

    try:
        core.add_story_action("capitulo_extra", "choice", options=["A"])
        assert False, "esperava StudioError (tipo não suportado)"
    except StudioError:
        pass

    try:
        core.add_story_action("capitulo_extra", "speak", character="mika")  # falta "text"
        assert False, "esperava StudioError (campo obrigatório faltando)"
    except StudioError:
        pass

    assert len(core.project.stories["capitulo_extra"].actions) == 2  # nenhum erro adicionou nada

    # --- update_story_action: troca os campos, tipo continua o mesmo ---
    core.dirty = False
    core.update_story_action("capitulo_extra", 0, character="mika", text="Oi de novo!")

    acao_atualizada = core.project.stories["capitulo_extra"].actions[0]
    assert acao_atualizada.type == "speak"  # tipo não muda
    assert acao_atualizada.fields["text"] == "Oi de novo!"
    assert core.dirty is True

    try:
        core.update_story_action("capitulo_extra", 0, character="mika")  # falta "text"
        assert False, "esperava StudioError (campo obrigatório faltando)"
    except StudioError:
        pass

    try:
        core.update_story_action("capitulo_extra", 99, character="mika", text="x")
        assert False, "esperava StudioError (índice fora do range)"
    except StudioError:
        pass

    # --- remove_story_action ---
    core.dirty = False
    core.remove_story_action("capitulo_extra", 1)  # remove o "pause"
    assert len(core.project.stories["capitulo_extra"].actions) == 1
    assert core.project.stories["capitulo_extra"].actions[0].type == "speak"
    assert core.dirty is True

    try:
        core.remove_story_action("capitulo_extra", 99)
        assert False, "esperava StudioError (índice fora do range)"
    except StudioError:
        pass

    # --- move_story_action: troca de lugar com a vizinha ---
    core.add_story_action("capitulo_extra", "pause", duration=1)
    core.add_story_action("capitulo_extra", "exit", character="mika")
    # agora: [0]=speak, [1]=pause, [2]=exit
    ordem_antes = [a.type for a in core.project.stories["capitulo_extra"].actions]
    assert ordem_antes == ["speak", "pause", "exit"]

    core.dirty = False
    novo_indice = core.move_story_action("capitulo_extra", 1, -1)  # "pause" sobe
    assert novo_indice == 0
    ordem_depois = [a.type for a in core.project.stories["capitulo_extra"].actions]
    assert ordem_depois == ["pause", "speak", "exit"]
    assert core.dirty is True

    # mover pra baixo é o inverso
    novo_indice = core.move_story_action("capitulo_extra", 0, 1)
    assert novo_indice == 1
    assert [a.type for a in core.project.stories["capitulo_extra"].actions] == ["speak", "pause", "exit"]

    # já na ponta: no-op silencioso, devolve o mesmo índice, não marca dirty
    core.dirty = False
    novo_indice = core.move_story_action("capitulo_extra", 0, -1)  # já é o primeiro
    assert novo_indice == 0
    assert core.dirty is False
    assert [a.type for a in core.project.stories["capitulo_extra"].actions] == ["speak", "pause", "exit"]

    novo_indice = core.move_story_action("capitulo_extra", 2, 1)  # já é o último
    assert novo_indice == 2
    assert core.dirty is False

    try:
        core.move_story_action("capitulo_extra", 99, -1)
        assert False, "esperava StudioError (índice fora do range)"
    except StudioError:
        pass

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print("OK: StudioCore cria/carrega/salva projeto e edita personagem/cena, sem nenhuma dependência de Tkinter")
