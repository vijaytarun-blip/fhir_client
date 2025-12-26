"""
Unit tests for FHIR Client.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.client import FHIRClient, FHIRClientError


class TestFHIRClient(unittest.TestCase):
    """Test cases for FHIRClient class."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "https://hapi.fhir.org/baseR4"
        self.client = FHIRClient(base_url=self.base_url)

        self.sample_patient = {
            "resourceType": "Patient",
            "name": [{"use": "official", "family": "Doe", "given": ["John"]}],
            "gender": "male",
            "birthDate": "1980-01-01",
        }

    def tearDown(self):
        """Clean up after tests."""
        self.client.close()

    @patch("requests.Session.post")
    def test_create_resource_success(self, mock_post):
        """Test successful resource creation."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {**self.sample_patient, "id": "123"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = self.client.create_resource(self.sample_patient)

        self.assertEqual(result["id"], "123")
        self.assertEqual(result["resourceType"], "Patient")
        mock_post.assert_called_once()

    @patch("requests.Session.post")
    def test_create_resource_without_resource_type(self, mock_post):
        """Test that creating resource without resourceType raises error."""
        invalid_resource = {"name": "Test"}

        with self.assertRaises(FHIRClientError) as context:
            self.client.create_resource(invalid_resource)

        self.assertIn("resourceType", str(context.exception))

    @patch("requests.Session.get")
    def test_read_resource_success(self, mock_get):
        """Test successful resource read."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {**self.sample_patient, "id": "123"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client.read_resource("Patient", "123")

        self.assertEqual(result["id"], "123")
        self.assertEqual(result["resourceType"], "Patient")
        mock_get.assert_called_once()

    @patch("requests.Session.put")
    def test_update_resource_success(self, mock_put):
        """Test successful resource update."""
        updated_patient = {**self.sample_patient, "id": "123"}
        updated_patient["name"][0]["given"] = ["Jane"]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = updated_patient
        mock_response.raise_for_status = Mock()
        mock_put.return_value = mock_response

        result = self.client.update_resource(updated_patient)

        self.assertEqual(result["name"][0]["given"], ["Jane"])
        mock_put.assert_called_once()

    @patch("requests.Session.put")
    def test_update_resource_without_id(self, mock_put):
        """Test that updating resource without id raises error."""
        resource_without_id = self.sample_patient.copy()

        with self.assertRaises(FHIRClientError) as context:
            self.client.update_resource(resource_without_id)

        self.assertIn("id", str(context.exception))

    @patch("requests.Session.delete")
    def test_delete_resource_success(self, mock_delete):
        """Test successful resource deletion."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        result = self.client.delete_resource("Patient", "123")

        self.assertTrue(result)
        mock_delete.assert_called_once()

    @patch("requests.Session.get")
    def test_search_resources(self, mock_get):
        """Test resource search."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": 1,
            "entry": [{"resource": self.sample_patient}],
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client.search("Patient", {"family": "Doe"})

        self.assertEqual(result["total"], 1)
        self.assertEqual(result["resourceType"], "Bundle")
        mock_get.assert_called_once()

    @patch("requests.Session.get")
    def test_get_capability_statement(self, mock_get):
        """Test capability statement retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "resourceType": "CapabilityStatement",
            "status": "active",
        }
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = self.client.get_capability_statement()

        self.assertEqual(result["resourceType"], "CapabilityStatement")
        mock_get.assert_called_once()

    def test_client_initialization(self):
        """Test client initialization with various parameters."""
        client_with_auth = FHIRClient(
            base_url=self.base_url, auth=("user", "pass"), timeout=60, verify_ssl=False
        )

        self.assertEqual(client_with_auth.base_url, self.base_url)
        self.assertEqual(client_with_auth.timeout, 60)
        self.assertEqual(client_with_auth.verify_ssl, False)
        self.assertEqual(client_with_auth.session.auth, ("user", "pass"))

        client_with_auth.close()


if __name__ == "__main__":
    unittest.main()
