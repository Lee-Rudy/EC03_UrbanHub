import enum

class Role(str, enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    CELLULE_DECISIONNEL = "CELLULE_DECISIONNEL"
    OPERATEUR = "OPERATEUR"
