from src.ms_user.domain.role import Role

def test_roles_exist():
    assert Role.USER.value == "USER"
    assert Role.OPERATEUR.value == "OPERATEUR"