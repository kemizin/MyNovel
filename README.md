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

## Estrutura do projeto

```
myNovel/
├── assets/                  # imagens, músicas e dublagens
├── src/MyNovellib/
│   ├── character.py         # Character
│   ├── scene.py              # Canvas
│   ├── dialogue.py           # Dialogue / speak()
│   ├── story.py               # Action e as demais Actions (emotion, move, enter, exit, pause,
│   │                          # change_scene, choice, if_state, set_state, ...)
│   ├── state.py                # GameState
│   ├── choice_ui.py             # ChoiceUI (desenho/hover/clique da Choice)
│   ├── input.py                  # Input.poll() (QUIT + gesto de avançar, organizados)
│   ├── transitions.py             # FadeTransition
│   └── engine.py                   # Engine
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
- **Sem `goto`/`label`** (loop/repetição de trechos da história) — avaliado de
  propósito e decidido não implementar por enquanto: `choice()` + `GameState` +
  `if_state()` já cobrem convergência (branches diferentes levando ao mesmo trecho
  seguinte) e reuso (a mesma lista de Actions em mais de um lugar, como variável
  Python normal). O único caso que faltaria é repetir/voltar atrás, raro numa visual
  novel — e um `goto` genérico exigiria achatar a árvore de Actions aninhadas (Choice/
  if_state) numa sequência indexável, um redesenho grande pra um caso raro.

Ainda **não implementado** (por escolha, não é bug): editor visual, timeline gráfica,
save/load, rollback, histórico de escolhas, gerenciador de voz avançado, sistema de
SFX, lip sync, animações complexas, partículas, scripting próprio, exportação para
executável, versão web, sistema de plugins, multiplayer.
