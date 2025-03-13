import json
import os
from unittest.mock import patch

from api.app import DEV_PATHS, TIME_CAPSULES_DB


class TestPublicEndpoints:

    def test_home_endpoint(self, client):
        response = client.get("/")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert "service" in data
        assert "endpoints" in data
        assert len(data["endpoints"]) >= 4

    def test_quote_endpoint(self, client):
        response = client.get("/quote")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert "text" in data
        assert "author" in data

    def test_paths_endpoint(self, client):
        response = client.get("/paths")
        data = json.loads(response.data)

        assert response.status_code == 200
        assert "available_paths" in data
        assert len(data["available_paths"]) == len(DEV_PATHS.keys())

        # Check that all paths from DEV_PATHS are in the response
        for path in DEV_PATHS.keys():
            assert path in data["available_paths"]


class TestTimeCapsuleCreation:

    def test_create_time_capsule_success(self, client, sample_time_capsule_data):
        custom_key = "custom-test-key"
        with patch.dict(os.environ, {"API_KEY": custom_key}):
            response = client.post(
                "/create",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps(sample_time_capsule_data),
            )
            data = json.loads(response.data)

            assert response.status_code == 200
            assert "capsule_id" in data
            assert "message" in data
            assert "summary" in data
            assert data["summary"]["name"] == sample_time_capsule_data["name"]
            assert data["summary"]["timeframe"] == f"{sample_time_capsule_data['timeframe']} months"
            capsule_id = data["capsule_id"]
            assert capsule_id in TIME_CAPSULES_DB

    def test_create_time_capsule_missing_fields(self, client):
        custom_key = "custom-test-key"
        with patch.dict(os.environ, {"API_KEY": custom_key}):
            response = client.post(
                "/create",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps(
                    {
                        "name": "Test User",
                        # Missing email, interests, timeframe
                    }
                ),
            )
            data = json.loads(response.data)

            assert response.status_code == 400
            assert "error" in data
            assert "required_fields" in data

    def test_create_time_capsule_invalid_interests(self, client, sample_time_capsule_data):
        custom_key = "custom-test-key"
        with patch.dict(os.environ, {"API_KEY": custom_key}):
            invalid_data = sample_time_capsule_data.copy()
            invalid_data["interests"] = ["invalid_path", "frontend"]

            response = client.post(
                "/create",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps(invalid_data),
            )
            data = json.loads(response.data)

            assert response.status_code == 400
            assert "error" in data
            assert "available_paths" in data

    def test_create_time_capsule_invalid_timeframe(self, client, sample_time_capsule_data):
        custom_key = "custom-test-key"
        with patch.dict(os.environ, {"API_KEY": custom_key}):
            # Test negative timeframe
            negative_data = sample_time_capsule_data.copy()
            negative_data["timeframe"] = -1

            response1 = client.post(
                "/create",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps(negative_data),
            )

            # Test too large timeframe
            large_data = sample_time_capsule_data.copy()
            large_data["timeframe"] = 30

            response2 = client.post(
                "/create",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps(large_data),
            )

            # Test non-numeric timeframe
            string_data = sample_time_capsule_data.copy()
            string_data["timeframe"] = "six"

            response3 = client.post(
                "/create",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps(string_data),
            )

            assert response1.status_code == 400
            assert response2.status_code == 400
            assert response3.status_code == 400


class TestTimeCapsuleRetrieval:
    def test_get_time_capsule(self, client, sample_time_capsule_data):
        custom_key = "custom-test-key"
        with patch.dict(os.environ, {"API_KEY": custom_key}):
            create_response = client.post(
                "/create",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps(sample_time_capsule_data),
            )
            create_data = json.loads(create_response.data)
            capsule_id = create_data["capsule_id"]

            # Then retrieve it
            response = client.get(f"/capsule/{capsule_id}", headers={"X-API-Key": custom_key})
            data = json.loads(response.data)

            assert response.status_code == 200
            assert data["id"] == capsule_id
            assert data["name"] == sample_time_capsule_data["name"]
            assert data["email"] == sample_time_capsule_data["email"]
            assert "roadmap" in data
            assert len(data["roadmap"]) > 0

    def test_get_nonexistent_time_capsule(self, client):
        custom_key = "custom-test-key"
        with patch.dict(os.environ, {"API_KEY": custom_key}):
            response = client.get("/capsule/nonexistent-id", headers={"X-API-Key": custom_key})
            data = json.loads(response.data)

            assert response.status_code == 404
            assert "error" in data


class TestMilestoneUpdates:
    def test_update_milestone(self, client, sample_time_capsule_data):
        custom_key = "custom-test-key"
        with patch.dict(os.environ, {"API_KEY": custom_key}):
            create_response = client.post(
                "/create",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps(sample_time_capsule_data),
            )
            create_data = json.loads(create_response.data)
            capsule_id = create_data["capsule_id"]

            # Then update the first milestone
            response = client.put(
                f"/capsule/{capsule_id}/milestone/0",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps({"completed": True}),
            )
            data = json.loads(response.data)

            assert response.status_code == 200
            assert "message" in data
            assert "milestone" in data
            assert data["milestone"]["completed"] is True
            assert "progress" in data
            assert data["progress"] > 0

            # Verify the update in the database
            assert TIME_CAPSULES_DB[capsule_id]["roadmap"][0]["completed"] is True

    def test_update_invalid_milestone_index(self, client, sample_time_capsule_data):
        custom_key = "custom-test-key"
        with patch.dict(os.environ, {"API_KEY": custom_key}):
            create_response = client.post(
                "/create",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps(sample_time_capsule_data),
            )
            create_data = json.loads(create_response.data)
            capsule_id = create_data["capsule_id"]

            # Try to update a milestone with a negative index
            response1 = client.put(
                f"/capsule/{capsule_id}/milestone/-1",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps({"completed": True}),
            )

            # Try to update a milestone with an out-of-bounds index
            response2 = client.put(
                f"/capsule/{capsule_id}/milestone/999",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps({"completed": True}),
            )

            assert response1.status_code == 404
            assert response2.status_code == 400

    def test_update_milestone_missing_field(self, client, sample_time_capsule_data):
        custom_key = "custom-test-key"
        with patch.dict(os.environ, {"API_KEY": custom_key}):
            create_response = client.post(
                "/create",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps(sample_time_capsule_data),
            )
            create_data = json.loads(create_response.data)
            capsule_id = create_data["capsule_id"]

            # Try to update a milestone without the required field
            response = client.put(
                f"/capsule/{capsule_id}/milestone/0",
                headers={"X-API-Key": custom_key, "Content-Type": "application/json"},
                data=json.dumps({}),  # Missing 'completed' field
            )

            assert response.status_code == 400
            assert "error" in json.loads(response.data)
