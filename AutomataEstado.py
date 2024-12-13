from enum import Enum

class AutomataEstado(Enum):
    INICIO = 0
    COND_1 = 1
    PROP = 2
    NEG = 3
    NEG_PA = 4
    PROP_A = 5
    COND_2 = 6
    NEG_PB = 7
    PROP_B = 8
    FIN = 9
    ERROR = 10