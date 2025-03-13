import json
import os
from unittest.mock import patch


class TestUtilsFunctions:
    def test_require_api_key_valid(self, client, sample_time_capsule_data):
        custom_key = "custom-test-key"
        with patch.dict(os.environ, {"API_KEY": custom_key}):
            response = client.post(
                "/create",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps(sample_time_capsule_data),
            )
            assert response.status_code == 200

    def test_require_api_key_invalid(self, client, sample_time_capsule_data):
        response = client.post(
            "/create",
            headers={"X-API-Key": "invalid-key", "Content-Type": "application/json"},
            data=json.dumps(sample_time_capsule_data),
        )
        assert response.status_code == 401

    def test_require_api_key_missing(self, client, sample_time_capsule_data):
        response = client.post(
            "/create", headers={"Content-Type": "application/json"}, data=json.dumps(sample_time_capsule_data)
        )
        assert response.status_code == 401
