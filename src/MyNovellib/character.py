class Character:

    def __init__(self, nome):

        self.nome = nome
        self.emotions = {}
        self.current_emotion = None
        self.position = None
        self.is_speaking = False

    def add_emotion(self, nome, idle, talking=None):

        self.emotions[nome] = {
            "idle": idle,
            "talking": talking
        }

    def emotion(self, nome):

        if nome not in self.emotions:
            raise ValueError(
                f"A emoção '{nome}' não foi cadastrada para {self.nome}."
            )

        self.current_emotion = nome