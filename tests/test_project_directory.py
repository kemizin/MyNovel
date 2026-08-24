# Teste pequeno, sem dependências externas, sem pygame.
# Roda com: .venv/Scripts/python.exe tests/test_project_directory.py
#
# Project System Update, Waystone 3: create_project() e
# ProjectDirectory -- estrutura de pastas minima, sem lixo.

import os
import sys
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.project.directory import (
    ProjectDirectory,
    create_project,
    PROJECT_FILE_NAME,
    PROJECT_SUBDIRS,
)

assert "pygame" not in sys.modules

tmp_root = tempfile.mkdtemp(prefix="mynovel_test_dir_")

try:
    # --- create_project cria a estrutura minima, sem lixo extra ---
    project_path = os.path.join(tmp_root, "MeuJogo")
    directory = create_project(project_path)

    assert os.path.isdir(project_path)
    assert os.path.isfile(os.path.join(project_path, PROJECT_FILE_NAME))

    conteudo = set(os.listdir(project_path))
    esperado = set(PROJECT_SUBDIRS) | {PROJECT_FILE_NAME}
    assert conteudo == esperado, f"esperava exatamente {esperado}, veio {conteudo}"

    # so as pastas estruturais -- nada de assets/characters/jef/ etc
    # criado sem necessidade
    for subdir in PROJECT_SUBDIRS:
        subdir_path = os.path.join(project_path, subdir)
        assert os.path.isdir(subdir_path)
        assert os.listdir(subdir_path) == [], f"{subdir}/ deveria estar vazia"

    # --- nome default = nome da pasta ---
    assert directory.project.name == "MeuJogo"
    assert directory.project.resolution == (1920, 1080)

    # --- nome/resolucao customizados ---
    outro_path = os.path.join(tmp_root, "outro")
    outro_dir = create_project(outro_path, name="Jogo Customizado", resolution=(1280, 720))
    assert outro_dir.project.name == "Jogo Customizado"
    assert outro_dir.project.resolution == (1280, 720)

    # --- ProjectDirectory.exists() ---
    assert directory.exists() is True
    assert ProjectDirectory(os.path.join(tmp_root, "nao_existe")).exists() is False

    # --- carregar um projeto existente pelo diretorio ---
    reloaded = ProjectDirectory(project_path)
    project = reloaded.load()
    assert project.name == "MeuJogo"
    assert project.resolution == (1920, 1080)

    # --- nao cria em cima de diretorio nao vazio ---
    try:
        create_project(project_path)  # ja existe e tem conteudo
        assert False, "esperava FileExistsError"
    except FileExistsError:
        pass

    # --- mas cria normalmente num diretorio vazio ja existente ---
    pre_criado = os.path.join(tmp_root, "pre_criado")
    os.makedirs(pre_criado)
    pre_dir = create_project(pre_criado)
    assert pre_dir.project.name == "pre_criado"

    # --- ProjectDirectory.save() sem project nenhum falha claramente ---
    vazio = ProjectDirectory(os.path.join(tmp_root, "vazio"))
    try:
        vazio.save()
        assert False, "esperava ValueError (nenhum Project pra salvar)"
    except ValueError:
        pass

    print("OK: create_project()/ProjectDirectory criam e carregam a estrutura minima, sem lixo")

finally:
    shutil.rmtree(tmp_root, ignore_errors=True)
