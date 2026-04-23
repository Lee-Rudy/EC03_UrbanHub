import enum

class Role(str, enum.Enum):
    USER = "USER"
    CELLULE_DECISIONNEL = "CELLULE_DECISIONNEL"
    OPERATEUR = "OPERATEUR"
