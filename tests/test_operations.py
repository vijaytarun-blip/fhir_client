"""
Unit tests for FHIR operations modules.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from src.client import FHIRClient
from src.operations.create import create_resource
from src.operations.read import read_resource
from src.operations.update import update_resource
from src.operations.delete import delete_resource


class TestOperations(unittest.TestCase):
    """Test cases for CRUD operations wrapper functions."""

    def setUp(self):
        """Set up test fixtures."""
        self.base_url = "https://hapi.fhir.org/baseR4"
        self.client = FHIRClient(base_url=self.base_url)

        self.test_resource = {
            "resourceType": "Patient",
            "name": [{"use": "official", "family": "Doe", "given": ["John"]}],
            "gender": "male",
            "birthDate": "1980-01-01",
        }

    def tearDown(self):
        """Clean up after tests."""
        self.client.close()

    @patch("requests.Session.post")
    def test_create_resource_operation(self, mock_post):
        """Test create_resource operation wrapper."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {**self.test_resource, "id": "test-123"}
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response

        result = create_resource(self.client, self.test_resource)

        self.assertEqual(result["id"], "test-123")
        self.assertEqual(result["resourceType"], "Patient")
        mock_post.assert_called_once()

    @patch("requests.Session.get")
    def test_read_resource_operation(self, mock_get):
        """Test read_resource operation wrapper."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {**self.test_resource, "id": "test-123"}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        result = read_resource(self.client, "Patient", "test-123")

        self.assertEqual(result["id"], "test-123")
        self.assertEqual(result["resourceType"], "Patient")
        mock_get.assert_called_once()

    @patch("requests.Session.put")
    def test_update_resource_operation(self, mock_put):
        """Test update_resource operation wrapper."""
        updated_resource = {**self.test_resource, "id": "test-123"}
        updated_resource["name"][0]["given"] = ["Jane"]

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = updated_resource
        mock_response.raise_for_status = Mock()
        mock_put.return_value = mock_response

        result = update_resource(self.client, updated_resource)

        self.assertEqual(result["name"][0]["given"], ["Jane"])
        mock_put.assert_called_once()

    @patch("requests.Session.delete")
    def test_delete_resource_operation(self, mock_delete):
        """Test delete_resource operation wrapper."""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()
        mock_delete.return_value = mock_response

        result = delete_resource(self.client, "Patient", "test-123")

        self.assertTrue(result)
        mock_delete.assert_called_once()


class TestModelsIntegration(unittest.TestCase):
    """Test cases for model classes with operations."""

    def setUp(self):
        """Set up test fixtures."""
        from src.models import Patient, Observation

        self.Patient = Patient
        self.Observation = Observation

    def test_patient_model_creation(self):
        """Test Patient model helper."""
        patient = self.Patient.create(
            family_name="Smith",
            given_names=["John", "Jacob"],
            gender="male",
            birth_date="1990-05-15",
        )

        self.assertEqual(patient["resourceType"], "Patient")
        self.assertEqual(patient["name"][0]["family"], "Smith")
        self.assertEqual(patient["gender"], "male")
        self.assertTrue(self.Patient.validate(patient))

    def test_patient_get_full_name(self):
        """Test Patient full name extraction."""
        patient = self.Patient.create(
            family_name="Smith", given_names=["John", "Jacob"]
        )

        full_name = self.Patient.get_full_name(patient)
        self.assertEqual(full_name, "John Jacob Smith")

    def test_observation_model_creation(self):
        """Test Observation model helper."""
        observation = self.Observation.create(
            patient_reference="Patient/123",
            code={
                "coding": [
                    {
                        "system": "http://loinc.org",
                        "code": "15074-8",
                        "display": "Glucose",
                    }
                ]
            },
            value={"value": 95, "unit": "mg/dL"},
        )

        self.assertEqual(observation["resourceType"], "Observation")
        self.assertEqual(observation["subject"]["reference"], "Patient/123")
        self.assertTrue(self.Observation.validate(observation))

    def test_observation_vital_sign_creation(self):
        """Test Observation vital sign shorthand."""
        observation = self.Observation.create_vital_sign(
            patient_reference="Patient/123",
            vital_type="heart_rate",
            value=72,
            unit="beats/min",
        )

        self.assertEqual(observation["resourceType"], "Observation")
        self.assertEqual(observation["valueQuantity"]["value"], 72)
        self.assertTrue(self.Observation.validate(observation))


if __name__ == "__main__":
    unittest.main()
