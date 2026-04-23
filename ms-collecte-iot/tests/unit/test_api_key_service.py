from __future__ import annotations

"""
Tests unitaires pour app/security/api_key_service.py.

On teste les cas non couverts par les tests d'intégration :
  - Capteur désactivé (enabled=False) → 401
  - Clé API expirée → 401
  - reload_api_keys() recharge le registre depuis le fichier

Stratégie :
  On patche _SENSOR_REGISTRY (le dictionnaire module-level) pour simuler
  différents états du registre sans modifier le fichier api_keys.json.
"""

from unittest.mock import patch

import pytest
from fastapi import HTTPException

import app.security.api_key_service as api_key_module
from app.security.api_key_service import reload_api_keys, verify_api_key


class TestVerifyApiKeyDisabledSensor:
    """Test : capteur désactivé dans le registre."""

    def test_disabled_sensor_raises_401(self) -> None:
        """Un capteur avec enabled=False doit lever une HTTPException 401."""
        fake_registry = {
            "key_disabled_sensor": {
                "sensor_id": "radar_disabled",
                "mac_address": "00:AA:BB:CC:DD:EE",
                "sensor_type": "radar",
                "zone_id": "int_001",
                "enabled": False,             # ← capteur désactivé
                "expires_at": "2099-12-31T23:59:59Z",
            }
        }

        with patch("app.security.api_key_service._SENSOR_REGISTRY", fake_registry):
            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(x_api_key="key_disabled_sensor")

        assert exc_info.value.status_code == 401
        assert "désactivé" in exc_info.value.detail


class TestVerifyApiKeyExpired:
    """Test : clé API expirée."""

    def test_expired_key_raises_401(self) -> None:
        """Une clé dont la date d'expiration est passée doit lever une HTTPException 401."""
        fake_registry = {
            "key_expired": {
                "sensor_id": "radar_expired",
                "mac_address": "00:AA:BB:CC:DD:FF",
                "sensor_type": "radar",
                "zone_id": "int_001",
                "enabled": True,
                "expires_at": "2020-01-01T00:00:00Z",  # ← date passée
            }
        }

        with patch("app.security.api_key_service._SENSOR_REGISTRY", fake_registry):
            with pytest.raises(HTTPException) as exc_info:
                verify_api_key(x_api_key="key_expired")

        assert exc_info.value.status_code == 401
        assert "expir" in exc_info.value.detail.lower()


class TestVerifyApiKeyNoExpiry:
    """Test : clé sans date d'expiration (champ optionnel)."""

    def test_key_without_expiry_is_accepted(self) -> None:
        """Si expires_at est absent, la clé doit être acceptée (pas de contrôle de date)."""
        fake_registry = {
            "key_no_expiry": {
                "sensor_id": "radar_no_expiry",
                "mac_address": "00:AA:BB:CC:EE:FF",
                "sensor_type": "radar",
                "zone_id": "int_001",
                "enabled": True,
                # Pas de champ expires_at → pas de vérification de date
            }
        }

        with patch("app.security.api_key_service._SENSOR_REGISTRY", fake_registry):
            sensor_info = verify_api_key(x_api_key="key_no_expiry")

        assert sensor_info["sensor_id"] == "radar_no_expiry"


class TestReloadApiKeys:
    """Tests de reload_api_keys() : rechargement à chaud du registre."""

    def test_reload_updates_registry(self) -> None:
        """reload_api_keys() doit remplacer _SENSOR_REGISTRY par les données rechargées."""
        new_data = {
            "key_new_sensor": {
                "sensor_id": "new_radar_001",
                "enabled": True,
            }
        }

        # On patche _load_api_keys pour contrôler ce qu'il retourne
        with patch("app.security.api_key_service._load_api_keys", return_value=new_data):
            reload_api_keys()

        # Après le rechargement, _SENSOR_REGISTRY doit contenir les nouvelles données
        assert "key_new_sensor" in api_key_module._SENSOR_REGISTRY

    def test_reload_replaces_old_registry(self) -> None:
        """reload_api_keys() doit supprimer les anciennes clés qui ne sont plus dans le fichier."""
        # Etat initial : une clé qui devrait disparaître après rechargement
        initial_registry = {"old_key": {"sensor_id": "old_sensor"}}
        empty_reload = {}

        with patch.object(api_key_module, "_SENSOR_REGISTRY", initial_registry):
            with patch("app.security.api_key_service._load_api_keys", return_value=empty_reload):
                reload_api_keys()

        # Après rechargement avec un registre vide, l'ancienne clé ne doit plus être là
        assert "old_key" not in api_key_module._SENSOR_REGISTRY
