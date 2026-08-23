from src.MyNovellib.story import Action


# Dialogue é uma Action: representa uma fala a ser executada depois,
# não na hora em que speak() é chamado.
class Dialogue(Action):

    def __init__(
        self,
        character,
        text,
        speed=0.03,
        delay=None,
        dub=None
    ):
        self.character = character
        self.text = text
        self.speed = speed
        self.delay = delay
        self.dub = dub



def speak(
    character,
    text,
    speed=0.03,
    delay=None,
    dub=None
):
    return Dialogue(
        character,
        text,
        speed,
        delay,
        dub
    )