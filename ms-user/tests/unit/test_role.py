from src.ms_user.domain.role import Role

def test_roles_exist():
    assert UserRole.USER.value == "USER"
    assert UserRole.OPERATEUR.value == "OPERATEUR"