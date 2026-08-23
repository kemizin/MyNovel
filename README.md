# MyNovel

Biblioteca Python para criação de Visual Novels usando [Pygame](https://www.pygame.org/).

O objetivo é deixar quem escreve a história pensando em **personagens, cenas, falas,
emoções e acontecimentos** — sem precisar conhecer Pygame, event loops, surfaces ou
qualquer detalhe interno de renderização.

```python
speak(ken, "Cara, você tá comendo terra?")
```

## Requisitos

- Python 3.11.9
- Pygame 2.6.1

## Instalação rápida

```bash
python -m venv .venv
.venv/Scripts/pip install pygame==2.6.1
```

## Rodando

```bash
.venv/Scripts/python.exe main.py
```

Durante uma fala: aperte **espaço** ou dê **clique esquerdo** para avançar (ou para
completar o texto instantaneamente, se ele ainda estiver aparecendo aos poucos).

Para ver todas as funções da biblioteca em ação, rode a demonstração completa:

```bash
.venv/Scripts/python.exe exemples/00_demo_completa.py
```

E a pasta [`exemples/`](exemples/) tem um arquivo focado em cada função individual
(veja a seção [Exemplos](#exemplos) abaixo).

## Conceitos principais

| Conceito | O que é |
|---|---|
| `Character` | Um personagem: nome, emoções cadastradas e qual está ativa. |
| `Canvas` | Uma cena: nome, imagem de fundo, tamanho da janela, música e os personagens visíveis nela. |
| `Engine` | Executa a história: abre a janela, desenha cada frame, processa input. |
| `story` | Uma lista de **Actions** (falas e acontecimentos), executadas em ordem. |

### Character

```python
from src.MyNovellib.character import Character

jef = Character("Jef")

jef.add_emotion(
    "normal",
    idle="assets/char/jefer/jefer.png",
    talking="assets/char/jefer/jefer_falano.png"
)

jef.add_emotion(
    "bravo",
    idle="assets/char/jefer/jefer_soco.png"
    # sem "talking": ao falar bravo, usa o mesmo sprite parado
)

jef.emotion("normal")  # emoção inicial
```

Cada emoção tem um sprite `idle` (parado) e, opcionalmente, um sprite `talking`
(falando). Se `talking` não for informado, a Engine usa o `idle` mesmo enquanto o
personagem fala — assim você não precisa desenhar um frame de fala para toda emoção.

### Canvas

```python
from src.MyNovellib.scene import Canvas

campo = Canvas(
    "campo",                     # nome (também vira o título da janela)
    "assets/fundos/campo.jpg",   # imagem de fundo
    1920, 1080,                  # tamanho da janela
    music="assets/music/campo.wav"  # opcional
)

campo.add_character(jef, position=1, scale=0.5)
campo.add_character(ken, position=3, scale=0.5)
```

`add_character()` é para **configurar a cena antes da história começar** — os
personagens já aparecem desde o primeiro frame. Para personagens que entram *durante*
a história, use a Action `enter()` (veja abaixo).

`position` vai de **1 a 3**:

| position | posição horizontal |
|---|---|
| 1 | 25% da largura da tela |
| 2 | 50% da largura da tela |
| 3 | 75% da largura da tela |

A posição é o **centro** do sprite; os pés ficam sempre alinhados na parte de baixo da
tela. `scale` é aplicado sobre o tamanho original do PNG. `offset_x`/`offset_y` fazem
ajustes finos, em pixels.

### Engine

```python
from src.MyNovellib.engine import Engine

engine = Engine()
engine.run(campo, story)
```

`run(canvas, story)` abre a janela na cena inicial e executa a lista `story` em ordem,
uma Action de cada vez.

## Actions (a história)

`story` é uma lista de Actions. Cada função abaixo **retorna** uma Action — nada é
executado no momento em que a função é chamada, só quando a Engine chega nela dentro
da lista:

```python
story = [
    speak(ken, "Tem alguém aí?"),
    enter(jef, position=1),
    speak(jef, "Eu estou aqui."),
]
```

Toda Action visual (tudo exceto `speak`) atualiza a tela **imediatamente**, sem
depender de um `speak()` depois para aparecer.

### `speak(character, text, speed=0.03, delay=None, dub=None)`
*(`from src.MyNovellib.dialogue import speak`)*

Mostra uma fala, com efeito de texto aparecendo aos poucos.

- `speed`: segundos por caractere (menor = mais rápido).
- `delay`: depois que o texto termina de aparecer —
  - `None` (padrão): espera espaço/clique do jogador para avançar.
  - um número: espera esse tanto de segundos e avança sozinho.
- `dub`: caminho de um áudio de dublagem, tocado junto com a fala.

Enquanto o personagem fala, a Engine usa o sprite `talking` da emoção atual (ou o
`idle`, se não houver `talking`).

### `emotion(character, name)`

Troca a emoção atual do personagem (precisa já ter sido cadastrada com
`add_emotion`).

### `move(character, position=None, scale=None, offset_x=None, offset_y=None)`

Reposiciona/reenquadra um personagem que **já está na cena**. Qualquer parâmetro
deixado como `None` mantém o valor atual — `move()` nunca reseta o que você não
informou:

```python
move(jef, position=2, scale=0.7)
move(jef, position=3)              # scale continua 0.7
```

### `add_character(character, position, scale=0.5, offset_x=0, offset_y=0)`

Versão em Action de `Canvas.add_character()` — útil quando você quer adicionar um
personagem como parte da própria lista `story`, em vez de configurar antes.

### `remove_character(character)`

Remove um personagem da cena. Equivalente técnico de `exit()` (veja abaixo).

### `enter(character, position, scale=0.5, offset_x=0, offset_y=0)`

Entrada **narrativa** de um personagem — semanticamente é um acontecimento da
história ("o personagem entrou"), e não uma configuração de cena. Faz o mesmo que
`add_character()` por baixo dos panos.

### `exit(character)`

Saída **narrativa** de um personagem, equivalente a `remove_character()`.

> `exit` é o nome de uma função do Python (usada para fechar o interpretador). Ao
> importar, é comum dar um apelido:
> `from src.MyNovellib.story import exit as sair`

### `pause(duration)`

Mantém a cena parada na tela por `duration` segundos, sem exigir input — útil para dar
um respiro dramático ou tempo de uma mudança (`emotion`/`move`) ser percebida.

### `change_scene(canvas, transition=None, duration=0.5)`

Troca a cena atual: background, dimensões da janela, música e os personagens visíveis
(cada `Canvas` tem seu próprio conjunto de personagens — eles não atravessam a troca
de cena sozinhos; use `enter()` de novo se precisar deles na cena nova).

- `transition=None` (padrão): troca instantânea.
- `transition="fade"`: fade out da cena atual → troca → fade in da cena nova, em
  `duration` segundos ao todo.

## Exemplo completo

```python
from src.MyNovellib.scene import Canvas
from src.MyNovellib.character import Character
from src.MyNovellib.engine import Engine
from src.MyNovellib.dialogue import speak
from src.MyNovellib.story import enter, emotion, move, pause, exit as sair, change_scene

jef = Character("Jef")
jef.add_emotion("normal", idle="assets/char/jefer/jefer.png", talking="assets/char/jefer/jefer_falano.png")
jef.add_emotion("bravo", idle="assets/char/jefer/jefer_soco.png")
jef.emotion("normal")

ken = Character("Ken")
ken.add_emotion("normal", idle="assets/char/ken/ken.png", talking="assets/char/ken/ken_falando.png")
ken.emotion("normal")

campo = Canvas("campo", "assets/fundos/campo.jpg", 1920, 1080)
quarto = Canvas("quarto", "assets/fundos/quarto.jpg", 1920, 1080)

campo.add_character(ken, position=3, scale=0.5)

story = [
    speak(ken, "Tem alguém aí?"),
    enter(jef, position=1),
    emotion(jef, "bravo"),
    speak(jef, "EU ESTOU AQUI!"),
    move(jef, position=2, scale=0.7),
    pause(0.5),
    speak(ken, "Você é assustador."),
    sair(jef),
    change_scene(quarto, transition="fade", duration=1.0),
]

engine = Engine()
engine.run(campo, story)
```

## Exemplos

A pasta [`exemples/`](exemples/) tem um arquivo por função, todos executáveis
diretamente:

| Arquivo | Função demonstrada |
|---|---|
| `00_demo_completa.py` | Todas as funções juntas, em uma história só |
| `01_speak.py` | `speak()` — digitação, `speed`, `delay`, `dub` |
| `02_emotion.py` | `emotion()` |
| `03_add_character.py` | `Canvas.add_character()` (configuração de cena) |
| `04_remove_character.py` | `remove_character()` (Action) |
| `05_enter.py` | `enter()` |
| `06_exit.py` | `exit()` |
| `07_move.py` | `move()` — atualização parcial de posição/escala/offset |
| `08_pause.py` | `pause()` |
| `09_change_scene.py` | `change_scene()` — troca instantânea e com fade |

```bash
.venv/Scripts/python.exe exemples/01_speak.py
```

## Estrutura do projeto

```
myNovel/
├── assets/                  # imagens, músicas e dublagens
├── src/MyNovellib/
│   ├── character.py         # Character
│   ├── scene.py              # Canvas
│   ├── dialogue.py           # Dialogue / speak()
│   ├── story.py               # Action e as demais Actions (emotion, move, enter, exit, pause, change_scene, ...)
│   ├── transitions.py         # FadeTransition
│   └── engine.py               # Engine
├── exemples/                  # um exemplo funcional por função
├── tests/                      # testes de regressão (sem dependências externas)
└── main.py                     # ponto de entrada / demo original
```

## Limitações conhecidas

- **Música e dublagem dividem o mesmo canal de áudio** (`pygame.mixer.music`) — tocar
  um dub interrompe a música ambiente. Ainda não corrigido.
- **Só existe a transição `fade`** — `shake`, `flash`, `show_image`/`hide_image` ainda
  não foram implementados.
- **`enter`/`exit`/`move` são instantâneos** — sem animação de movimento ainda.
- **Nomes internos em português**: `Character.nome`, `Canvas.nome/imagem/tamanho` são
  em português, enquanto a API pública de Actions (`speak`, `emotion`, `move`, ...) é
  em inglês. É uma inconsistência conhecida, não corrigida ainda por exigir uma
  refatoração maior em vários arquivos.
- Sprites são recarregados do disco a cada frame (sem cache de imagem) — funciona,
  mas não é o mais performático.

Ainda **não implementado** (por escolha, não é bug): editor visual, timeline gráfica,
sistema de escolhas, save/load, rollback, gerenciador de voz avançado, sistema de SFX,
lip sync, animações complexas, partículas, scripting próprio, exportação para
executável, versão web, sistema de plugins, multiplayer.
