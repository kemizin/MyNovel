# Estado narrativo em memória: valores simples e flags que a história
# pode ler/alterar (ex: "amizade", "porta_aberta"). Sem save/load, sem
# banco de dados, sem persistência -- só um dicionário com defaults
# previsíveis.

_MISSING = object()


class GameState:

    def __init__(self, default=0):

        self._values = {}
        self.default = default

    def set(self, key, value):

        self._values[key] = value

    # Sem `default` explícito, usa self.default (configurável na
    # criação do GameState) -- assim state.get("algo_novo") nunca
    # levanta erro nem retorna None por acaso.
    def get(self, key, default=_MISSING):

        if key in self._values:
            return self._values[key]

        if default is _MISSING:
            return self.default

        return default

    def increment(self, key, amount=1):

        self.set(key, self.get(key) + amount)
