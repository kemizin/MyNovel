# Project Data: representação de um projeto MyNovel como dados puros,
# independente da Engine/Runtime (src/MyNovellib/*.py).
#
# Nada neste subpacote importa pygame, abre janela, renderiza ou
# executa história -- só descreve o que um projeto "é". A conversão
# pra objetos de Runtime (Character, Canvas, Action, Engine) acontece
# em camadas separadas (ver Action Factory / Project Runtime Loading),
# não aqui.
