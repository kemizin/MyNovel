# Teste pequeno, sem dependências externas, sem pygame.
# Roda com: .venv/Scripts/python.exe tests/test_character_data.py
#
# Project System Update, Waystone 5: CharacterData (representação
# serializável de personagem), separada do Character de Runtime, e
# Project.characters preservando isso num round trip.

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.MyNovellib.project.character_data import CharacterData
from src.MyNovellib.project.model import Project

assert "pygame" not in sys.modules

# --- criacao vazia + add_emotion (mesmo formato de Character) ---
jef = CharacterData("Jef")
jef.add_emotion("normal", idle="jef_idle.png", talking="jef_talk.png")
jef.add_emotion("bravo", idle="jef_soco.png")  # sem talking, igual Character

assert jef.name == "Jef"
assert jef.emotions["normal"] == {"idle": "jef_idle.png", "talking": "jef_talk.png"}
assert jef.emotions["bravo"] == {"idle": "jef_soco.png", "talking": None}

# --- criacao ja com emotions (formato do JSON) ---
ken = CharacterData("Ken", emotions={
    "normal": {"idle": "ken.png", "talking": "ken_falando.png"},
})
assert ken.emotions["normal"]["idle"] == "ken.png"

# --- validacao ---
try:
    CharacterData("")
    assert False, "esperava ValueError para nome vazio"
except ValueError:
    pass

try:
    jef.add_emotion("triste", idle="")
    assert False, "esperava ValueError para idle vazio"
except ValueError:
    pass

# --- validação (hardening): nome de emoção vazio também não passa
# mais batido -- antes só o Studio checava isso na interface ---
for nome_invalido in ("", "   ", None):
    try:
        jef.add_emotion(nome_invalido, idle="jef_idle.png")
        assert False, f"esperava ValueError para nome={nome_invalido!r}"
    except ValueError:
        pass

# --- to_dict/from_dict/igualdade ---
data = jef.to_dict()
assert data == {
    "name": "Jef",
    "emotions": {
        "normal": {"idle": "jef_idle.png", "talking": "jef_talk.png"},
        "bravo": {"idle": "jef_soco.png", "talking": None},
    },
}
assert CharacterData.from_dict(data) == jef

# --- Project.characters preserva CharacterData num round trip ---
import tempfile, shutil

tmp_dir = tempfile.mkdtemp(prefix="mynovel_test_chardata_")
try:
    project = Project(name="Com Personagens")
    project.characters["jef"] = jef
    project.characters["ken"] = ken

    project_path = os.path.join(tmp_dir, "projeto.mynovel")
    project.save(project_path)

    loaded = Project.load(project_path)

    assert loaded.characters["jef"] == jef
    assert loaded.characters["ken"] == ken
    assert isinstance(loaded.characters["jef"], CharacterData)

finally:
    shutil.rmtree(tmp_dir, ignore_errors=True)

# --- CharacterData nao tem NADA de Runtime (sem emotion() ativa,
# sem is_speaking, sem current_emotion -- isso e do Character) ---
assert not hasattr(jef, "is_speaking")
assert not hasattr(jef, "current_emotion")
assert not hasattr(jef, "emotion")  # o metodo que TROCA a emocao ativa

print("OK: CharacterData e Project.characters funcionam, separados do Character de Runtime")
