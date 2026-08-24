# MyNovel

Biblioteca Python para criação de Visual Novels usando [Pygame](https://www.pygame.org/).

O objetivo é deixar quem escreve a história pensando em **personagens, cenas, falas,
emoções, acontecimentos e escolhas do jogador** — sem precisar conhecer Pygame, event
loops, surfaces ou qualquer detalhe interno de renderização.

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
| `GameState` | Estado narrativo em memória (valores e flags) que a história lê/altera. |
| `Project` | Um projeto MyNovel como **dados** (`project.mynovel`) — ver [Sistema de Projetos](#sistema-de-projetos-project-data). |

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

## Gameplay: escolhas, estado e condições

Além da história linear, a MyNovel permite que o jogador escolha um caminho — a
história muda de verdade dependendo da escolha.

### `choice(*options)`

Pausa a história e mostra as opções na tela. **Controles**: setas (↑↓←→) navegam,
espaço/enter confirma a opção destacada; o mouse também funciona — passar por cima
destaca (hover), clicar confirma. Só apertar espaço/enter/clicar confirma — navegar
(seta ou hover) nunca escolhe por acidente. A Engine fica parada nesse ponto até o
jogador confirmar uma opção.

Cada opção pode ser:

```python
# só o texto
choice("Ir para casa", "Ficar aqui")

# (texto, efeitos) -- efeitos é um dict {chave: quantidade}, somado no
# GameState (via GameState.increment()) quando a opção é confirmada
choice(
    ("Ajudar Jef", {"amizade": 1}),
    ("Ignorar Jef", {"amizade": 0}),
)

# (texto, efeitos, actions) -- além de alterar o GameState, executa
# essa lista de Actions imediatamente: ramificação real da história
choice(
    ("Sim", {"ajudou": 1}, [speak(jef, "Claro.")]),
    ("Não", {"ajudou": 0}, [speak(jef, "Nem pensar.")]),
)
```

Depois que a Engine processa a Choice, o resultado fica disponível em
`minha_choice.selected_index` (0, 1, 2, ...) — útil se você guardou a Action numa
variável e quer checar depois.

### `GameState`

Estado narrativo simples, em memória (sem save/load, sem banco de dados):

```python
from src.MyNovellib.state import GameState

state = GameState()          # default=0 pra chaves nunca definidas
state.set("amizade", 10)
state.get("amizade")         # 10
state.get("nunca_existiu")   # 0 (o default, não erro/None por acaso)
state.increment("amizade")   # soma 1 -> 11
state.increment("amizade", 5)  # soma 5 -> 16

state.set("porta_aberta", True)  # flags booleanas funcionam do mesmo jeito
```

`GameState(default=algum_valor)` configura o valor padrão pra chaves nunca definidas.
`get(chave, default=X)` também aceita um default só pra aquela chamada, sobrepondo o
global.

Pra usar um `GameState` específico (em vez do que a `Engine` cria sozinha), passe pra
`Engine`:

```python
state = GameState()
engine = Engine(state=state)
engine.run(campo, story)

state.get("amizade")  # o mesmo objeto foi alterado pela história
```

### `if_state(key, operator, value, actions)`

Executa uma lista de Actions **só se** a condição sobre o `GameState` for verdadeira:

```python
if_state(
    "amizade", ">=", 10,
    [speak(jef, "Eu confio em você.")]
)
```

Operadores aceitos: `==` `!=` `>` `<` `>=` `<=`. Funciona com números, strings e
booleanos (`if_state("porta_aberta", "==", True, [...])`). `if_state` pode aparecer
dentro de outro `if_state` (condições aninhadas).

### `set_state(key, value)`

Define um valor no `GameState` diretamente — **atribuição**, diferente dos efeitos de
`choice()` (que sempre somam). Útil pra marcar uma flag fora de uma escolha:

```python
set_state("viu_final_bom", True)
```

### Juntando tudo: ramificação real

```python
story = [
    speak(ken, "Você vai me ajudar?"),

    choice(
        ("Ajudar", {"amizade": 5}),
        ("Ignorar", {"amizade": 0}),
    ),

    if_state("amizade", ">=", 5, [
        speak(jef, "Obrigado por ajudar."),
        set_state("final", "bom"),
    ]),

    if_state("amizade", "<", 5, [
        speak(jef, "Tudo bem, eu entendo."),
        set_state("final", "neutro"),
    ]),
]
```

Os dois `if_state` acima também podiam ter sido escritos direto como a terceira forma
de `choice()` (ramificação inline) — as duas formas são válidas; use a que ficar mais
legível pra cada caso.

### Input

Espaço, clique esquerdo, setas e enter são os únicos controles hoje (sem controles
configuráveis ainda). Um diálogo (`speak`) só reage a espaço/clique; uma `choice()`
reage a setas, espaço/enter e mouse. Isso é organizado internamente por
`src/MyNovellib/input.py` (`Input.poll()`), então nenhuma Action nova precisa lidar
com `pygame.KEYDOWN`/`MOUSEBUTTONDOWN` na mão.

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

## Exemplo interativo (com escolhas)

Versão resumida de [`exemples/10_gameplay_demo.py`](exemples/10_gameplay_demo.py) —
o arquivo completo é jogável do início ao fim (2 cenas, 2 caminhos diferentes):

```python
from src.MyNovellib.state import GameState
from src.MyNovellib.story import choice, if_state, change_scene

story = [
    speak(ken, "Ouvi um barulho estranho. Você vem comigo checar?"),

    choice(
        ("Ajudar Ken", {"coragem": 5}, [
            speak(jef, "Claro, vamos juntos."),
        ]),
        ("Deixar Ken ir sozinho", {"coragem": 0}, [
            speak(jef, "Acho melhor você ir sozinho dessa vez."),
        ]),
    ),

    change_scene(quarto, transition="fade", duration=1.0),

    if_state("coragem", ">=", 5, [
        speak(ken, "Ainda bem que você veio comigo."),
    ]),

    if_state("coragem", "<", 5, [
        speak(jef, "Espero que esteja tudo bem com ele."),
    ]),
]

engine = Engine(state=GameState())
engine.run(campo, story)
```

## Sistema de Projetos (Project Data)

Tudo que foi descrito até aqui é escrito em Python. A MyNovel também tem um formato de
**projeto** — um jeito de descrever uma Visual Novel inteira como **dados** (arquivos
`.mynovel` em JSON), sem escrever nenhuma linha de Python. É a base do
[**MyNovel Studio**](#mynovel-studio), o editor visual onde quem não programa também
consegue criar uma VN.

### Project Data × Runtime

```
                    MYNOVEL CORE
                         │
          ┌──────────────┴──────────────┐
          │                              │
     PROJECT DATA                     RUNTIME
   (sem pygame, sem                 (Character, Canvas,
    janela, só dados)                Engine, Actions)
          │                              │
          └────────── LOAD ──────────────┘
```

- **Project Data** (`src/MyNovellib/project/`) — `Project`, `CharacterData`, `SceneData`,
  `StoryData`, `Asset`. Só dados: nenhum desses arquivos importa Pygame, abre janela ou
  executa história. É o que o [MyNovel Studio](#mynovel-studio) lê e escreve.
- **Runtime** (`src/MyNovellib/*.py`, descrito no resto deste README) — `Character`,
  `Canvas`, `Engine`, as Actions. É quem de fato roda o jogo.
- **Carregar** (`project.create_runtime()`) é a ponte entre os dois: transforma dados em
  objetos de Runtime e devolve pronto pra rodar pela `Engine` — a mesma `Engine`, não uma
  paralela.

### `project.mynovel`

Um projeto é uma pasta com um arquivo `project.mynovel` (JSON) na raiz:

```
MeuJogo/
├── project.mynovel
├── assets/
│   ├── characters/
│   │   └── jef/
│   │       ├── normal_idle.png
│   │       └── normal_talking.png
│   └── backgrounds/
│       └── campo.png
├── scenes/     # reservado pra uso futuro -- ver nota abaixo
└── stories/    # reservado pra uso futuro -- ver nota abaixo
```

Hoje, os dados de cena e história ficam **dentro** do próprio `project.mynovel` (JSON
aninhado), não em arquivos `.myscene`/`.mystory` separados por cena — as pastas
`scenes/`/`stories/` existem na estrutura (`create_project()` já as cria), mas
serializar cada cena/história em arquivo próprio é uma extensão futura, ainda não feita.

```json
{
  "format": "mynovel",
  "version": 1,
  "name": "Meu Jogo",
  "resolution": [1920, 1080],
  "characters": {
    "jef": {
      "name": "Jef",
      "emotions": {
        "normal": {
          "idle": "assets/characters/jef/normal_idle.png",
          "talking": "assets/characters/jef/normal_talking.png"
        }
      }
    }
  },
  "scenes": {
    "campo": {
      "name": "campo",
      "background": "assets/backgrounds/campo.png",
      "music": null,
      "characters": [
        {"character": "jef", "position": 1, "scale": 0.5, "emotion": "normal"}
      ]
    }
  },
  "stories": {
    "intro": {
      "name": "intro",
      "actions": [
        {"type": "speak", "character": "jef", "text": "Olá!"}
      ]
    }
  },
  "assets": {}
}
```

### Criando e carregando um projeto

```python
from src.MyNovellib.project.directory import create_project

directory = create_project("MeuJogo", resolution=(1920, 1080))
project = directory.project   # um Project em memória, já salvo em MeuJogo/project.mynovel
```

```python
from src.MyNovellib.project.character_data import CharacterData
from src.MyNovellib.project.scene_data import SceneData
from src.MyNovellib.project.story_data import StoryData

jef = CharacterData("Jef")
jef.add_emotion("normal", idle="assets/characters/jef/normal_idle.png")
project.characters["jef"] = jef

campo = SceneData(name="campo", background="assets/backgrounds/campo.png")
campo.add_character("jef", position=1, scale=0.5, emotion="normal")
project.scenes["campo"] = campo

intro = StoryData(name="intro")
intro.add_action("speak", character="jef", text="Olá!")
intro.add_action("pause", duration=1)
project.stories["intro"] = intro

directory.save()  # regrava MeuJogo/project.mynovel com os dados novos
```

Pra rodar depois (o mesmo projeto, ou um projeto de outra pessoa):

```python
from src.MyNovellib.project.model import Project

project = Project.load("MeuJogo/project.mynovel")
runtime = project.create_runtime()
runtime.run()  # funciona sozinho se houver 1 cena e 1 história; senão:
# runtime.run(scene="campo", story="intro")
```

`Actions` suportadas como dado hoje (subconjunto pequeno, de propósito):
`speak`, `emotion`, `move`, `enter`, `exit`, `pause`. Escolha (`choice`), condições
(`if_state`) e o resto da API de Runtime ainda só existem escritas em Python — dá pra
misturar os dois mundos livremente (nada impede um projeto carregado de ser combinado
com Actions escritas à mão antes de chamar `engine.run()`).

Um projeto real e completo, carregável do jeito que está no disco, está em
[`exemples/project_demo/`](exemples/project_demo/).

## MyNovel Studio

Além de editar `.mynovel` na mão ou por código (seção anterior), a MyNovel tem um
editor visual de verdade: o **MyNovel Studio**, uma interface desktop (Tkinter) pra
criar e editar projetos sem escrever Python.

### Project Data × Studio × Runtime

```
                        MYNOVEL CORE
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                   │
     PROJECT DATA         STUDIO              RUNTIME
   (sem pygame, sem      (Tkinter --        (Character, Canvas,
    janela, só dados)    edita Project       Engine, Actions)
                          Data)

     PROJECT DATA ── carrega / salva ── STUDIO
     PROJECT DATA ── Play (create_runtime()) ── RUNTIME
```

- O **Studio nunca duplica a Engine** — ele só lê e escreve Project Data (`Project`,
  `CharacterData`, `SceneData`, `Asset`), do mesmo jeito que qualquer código Python
  faria com `project.characters["jef"] = ...`. A única exceção é o botão **Play**, que
  chama `project.create_runtime()` e roda a MESMA `Engine` de sempre, numa janela
  pygame separada e síncrona — o Studio fica pausado enquanto o jogo roda, e volta ao
  normal quando o jogador fecha a janela ou a história termina.
- O Project System (`src/MyNovellib/project/`) continua sem importar Tkinter ou
  Pygame — o Studio é só mais um consumidor dessa camada de dados, como o Runtime já
  era.

### Abrindo o Studio

```bash
.venv/Scripts/python.exe studio.py
```

### Fluxo básico

1. **File → New Project...** — pede nome, pasta e resolução, cria a estrutura de
   pastas (`assets/`, `scenes/`, `stories/`, `project.mynovel`) e já abre o projeto
   recém-criado. Ou **File → Open Project...** pra abrir um `project.mynovel`
   existente.
2. **Project Explorer** (aba "Project" da barra lateral) — Characters, Scenes,
   Stories e Assets do projeto em árvore. Clicar num personagem ou cena abre o editor
   correspondente no painel Properties; qualquer outra seleção mostra um resumo
   somente-leitura.
3. **Character Editor** — nome do personagem, e uma linha por emoção com os sprites
   (idle/talking, com botão "Browse...") e um botão "Remove Emotion". "+ Add Emotion"
   abre um diálogo pra cadastrar uma nova emoção.
4. **Scene Editor** — preview da cena (fundo + personagens posicionados) num canvas;
   arrastar um personagem no preview ajusta `offset_x`/`offset_y` em tempo real, e o
   painel ao lado tem campos "Position", "Scale", "Offset X", "Offset Y" e a emoção
   inicial de cada personagem da cena.
5. **File → Save** (ou **Save As...** pra salvar em outro lugar) — grava o
   `project.mynovel` com as edições. O título da janela mostra `*` quando há
   alterações não salvas (ex.: `MyNovel Studio — MeuJogo *`), e some assim que salva;
   fechar com alterações pendentes pergunta se quer salvar antes.
6. **▶ Play** (toolbar ou Build → Play) — roda o projeto atual pela Engine de
   verdade, numa janela separada; o Studio continua aberto e volta ao normal quando o
   jogo termina.

A outra aba da barra lateral, **Assets**, lista todos os assets do projeto agrupados
por tipo (personagem, fundo, música, dublagem, outros), com miniatura sob demanda pra
imagens.

### Experimentando

[`exemples/studio_demo/`](exemples/studio_demo/) é um projeto pequeno (1 personagem,
1 cena, 2 falas — o foco é o fluxo, não o tamanho da história) já pronto pra abrir no
Studio (**File → Open Project...** → `exemples/studio_demo/project.mynovel`) e seguir
o fluxo inteiro na mão: navegar o Explorer, editar o personagem e a cena, salvar, e
dar Play.

### O que o Studio ainda não faz

Criar ou remover personagens/cenas pela interface (hoje só edita os que já existem no
projeto), editor de Diálogo/Escolha, Timeline, editor de Animação, editor de
Voz/Áudio, Node Editor (fluxo de história visual), Build/Export, empacotamento pra
Windows, versão web, colaboração/nuvem, plugins, temas, marketplace. Nada disso é bug
— é escopo definido pra essa fase.

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
| `10_gameplay_demo.py` | `choice()`, `GameState`, `if_state()` — história jogável com 2 caminhos |

```bash
.venv/Scripts/python.exe exemples/01_speak.py
```

[`exemples/project_demo/`](exemples/project_demo/) é diferente dos demais: não é um
script `.py`, é um **projeto MyNovel de verdade** (`project.mynovel` + assets) — veja
[Sistema de Projetos](#sistema-de-projetos-project-data) pra carregá-lo e rodá-lo.

## Estrutura do projeto

```
myNovel/
├── assets/                  # imagens, músicas e dublagens
├── src/MyNovellib/
│   ├── character.py         # Character (Runtime)
│   ├── scene.py              # Canvas (Runtime)
│   ├── dialogue.py           # Dialogue / speak() (Runtime)
│   ├── story.py               # Action e as demais Actions (Runtime)
│   ├── state.py                # GameState (Runtime)
│   ├── choice_ui.py             # ChoiceUI (Runtime)
│   ├── input.py                  # Input.poll() (Runtime)
│   ├── transitions.py             # FadeTransition (Runtime)
│   ├── engine.py                   # Engine (Runtime)
│   ├── project/                     # Project Data -- sem pygame, só dados
│   │   ├── model.py                  # Project (+ save/load, create_runtime())
│   │   ├── directory.py               # ProjectDirectory, create_project()
│   │   ├── assets.py                   # Asset (registro de metadados)
│   │   ├── character_data.py            # CharacterData
│   │   ├── scene_data.py                 # SceneData, SceneCharacter
│   │   ├── story_data.py                  # ActionData, StoryData
│   │   ├── action_factory.py               # ActionData -> Actions de Runtime
│   │   └── runtime_loader.py                # ProjectRuntime (Project -> Engine)
│   └── studio/                       # MyNovel Studio -- Tkinter, edita Project Data
│       └── app.py                          # StudioApp (janela, menus, editores, Play)
├── exemples/                  # um exemplo funcional por função + project_demo/ + studio_demo/
├── tests/                      # testes de regressão (sem dependências externas)
├── studio.py                   # ponto de entrada do MyNovel Studio
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
- **Sem `goto`/`label`** (loop/repetição de trechos da história) — avaliado de
  propósito e decidido não implementar por enquanto: `choice()` + `GameState` +
  `if_state()` já cobrem convergência (branches diferentes levando ao mesmo trecho
  seguinte) e reuso (a mesma lista de Actions em mais de um lugar, como variável
  Python normal). O único caso que faltaria é repetir/voltar atrás, raro numa visual
  novel — e um `goto` genérico exigiria achatar a árvore de Actions aninhadas (Choice/
  if_state) numa sequência indexável, um redesenho grande pra um caso raro.

Ainda **não implementado** (por escolha, não é bug): timeline gráfica, save/load (do
estado de uma partida em andamento), rollback, histórico de escolhas, gerenciador de
voz avançado, sistema de SFX, lip sync, animações complexas, partículas, scripting
próprio, exportação para executável, versão web, sistema de plugins, multiplayer. O
[MyNovel Studio](#mynovel-studio) já cobre o essencial de "editor visual"; o que ainda
falta nele especificamente está listado em [O que o Studio ainda não
faz](#o-que-o-studio-ainda-não-faz).
