# Teste pequeno, sem dependências externas, sem pygame.
# Roda com: .venv/Scripts/python.exe tests/test_story_data.py
#
# Project System Update, Waystone 7: ActionData/StoryData -- prova
# que um subconjunto de Actions (speak, emotion, move, enter, exit,
# pause) pode ser representado como dado, sem pygame, e
# Project.stories preservando isso num round trip.

import os
import sys
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.project.story_data import (
    ActionData, StoryData, SUPPORTED_ACTION_TYPES
)
from src.MyNovellib.project.model import Project

assert "pygame" not in sys.modules

# --- os 6 tipos do subconjunto pedido ---
assert set(SUPPORTED_ACTION_TYPES) == {
    "speak", "emotion", "move", "enter", "exit", "pause"
}

speak = ActionData("speak", character="ken", text="Olá!")
assert speak.type == "speak"
assert speak.fields == {"character": "ken", "text": "Olá!"}

emotion = ActionData("emotion", character="jef", emotion="bravo")
move = ActionData("move", character="jef", position=2)
enter = ActionData("enter", character="ken", position=3)
exit_ = ActionData("exit", character="ken")
pause = ActionData("pause", duration=1)

# --- to_dict() no formato exato do exemplo do prompt ---
assert speak.to_dict() == {"type": "speak", "character": "ken", "text": "Olá!"}
assert emotion.to_dict() == {"type": "emotion", "character": "jef", "emotion": "bravo"}
assert move.to_dict() == {"type": "move", "character": "jef", "position": 2}

# --- tipo nao suportado ---
try:
    ActionData("choice", options=["A", "B"])
    assert False, "esperava ValueError pra tipo fora do subconjunto"
except ValueError:
    pass

# --- campo obrigatorio faltando ---
try:
    ActionData("speak", character="ken")  # falta "text"
    assert False, "esperava ValueError por falta de 'text'"
except ValueError:
    pass

try:
    ActionData("pause")  # falta "duration"
    assert False, "esperava ValueError por falta de 'duration'"
except ValueError:
    pass

# --- from_dict/igualdade ---
data = {"type": "move", "character": "jef", "position": 2}
assert ActionData.from_dict(data) == move

# --- describe(): resumo de uma linha, pro Story Editor do Studio (e
# qualquer outra interface) mostrar sem reimplementar a formatação ---
assert speak.describe() == 'speak ken: "Olá!"'
assert emotion.describe() == "emotion jef: bravo"
assert move.describe() == "move jef: position=2"
assert ActionData("move", character="jef").describe() == "move jef: (sem mudanças)"
assert enter.describe() == "enter ken (position 3)"
assert exit_.describe() == "exit ken"
assert pause.describe() == "pause 1s"

texto_longo = ActionData("speak", character="jef", text="x" * 100)
resumo = texto_longo.describe()
assert len(resumo) < 100  # truncado, não devolve o texto inteiro
assert resumo.endswith("…\"")

# --- StoryData: nome + lista ordenada de ActionData ---
intro = StoryData(name="intro")
intro.add_action("speak", character="ken", text="Tem alguém aí?")
intro.add_action("enter", character="jef", position=1)
intro.add_action("emotion", character="jef", emotion="bravo")
intro.add_action("speak", character="jef", text="EU ESTOU AQUI!")
intro.add_action("move", character="jef", position=2)
intro.add_action("pause", duration=1)
intro.add_action("exit", character="jef")

assert len(intro.actions) == 7
assert intro.actions[0].type == "speak"
assert intro.actions[-1].type == "exit"

# ordem importa -- e a ordem de execucao da historia
tipos_em_ordem = [a.type for a in intro.actions]
assert tipos_em_ordem == ["speak", "enter", "emotion", "speak", "move", "pause", "exit"]

# --- validacao de StoryData ---
try:
    StoryData(name="")
    assert False, "esperava ValueError para nome vazio"
except ValueError:
    pass

# --- to_dict/from_dict/igualdade de StoryData ---
data = intro.to_dict()
assert data["name"] == "intro"
assert len(data["actions"]) == 7
assert data["actions"][0] == {"type": "speak", "character": "ken", "text": "Tem alguém aí?"}

reconstruida = StoryData.from_dict(data)
assert reconstruida == intro

# --- Project.stories preserva StoryData (com ordem das Actions) num round trip ---
tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_storydata_")
try:
    project = Project(name="Com Historia")
    project.stories["intro"] = intro

    project_path = os.path.join(tmp_dir, "projeto.mynovel")
    project.save(project_path)

    loaded = Project.load(project_path)

    assert loaded.stories["intro"] == intro
    assert isinstance(loaded.stories["intro"], StoryData)
    assert [a.type for a in loaded.stories["intro"].actions] == tipos_em_ordem

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

print("OK: ActionData/StoryData representam Actions como dados (subconjunto de 6 tipos), sem pygame")
