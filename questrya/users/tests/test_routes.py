import json
# import pytest
from unittest.mock import patch, MagicMock
from uuid import UUID

from questrya.users.domain import User
# from questrya.common.value_objects.email import Email


class TestUserRoutes:
    @patch('questrya.users.routes.user_service')
    def test_create_user_success(self, mock_user_service, test_client):
        # Arrange
        mock_user = MagicMock(spec=User)
        mock_user.uuid = UUID('12345678-1234-5678-1234-567812345678')
        mock_user_service.register_user.return_value = mock_user

        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }

        # Act
        response = test_client.post(
            '/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert 'uuid' in response_data
        assert response_data['uuid'] == '12345678-1234-5678-1234-567812345678'

        # Verify service was called with correct parameters
        mock_user_service.register_user.assert_called_once_with(
            "testuser", "test@example.com", "password123"
        )

    def test_create_user_invalid_data(self, test_client):
        # Test with invalid email
        request_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123"
        }

        response = test_client.post(
            '/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data

        # Test with short password
        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short"
        }

        response = test_client.post(
            '/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data

        # Test with empty username
        request_data = {
            "username": "",
            "email": "test@example.com",
            "password": "password123"
        }

        response = test_client.post(
            '/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data

    @patch('questrya.users.routes.user_service')
    def test_create_user_service_error(self, mock_user_service, test_client):
        # Arrange
        mock_user_service.register_user.side_effect = ValueError("User already exists")

        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }

        # Act
        response = test_client.post(
            '/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert response_data['error'] == "User already exists"

    @patch('questrya.users.routes.user_service')
    def test_create_user_server_error(self, mock_user_service, test_client):
        # Arrange
        mock_user_service.register_user.side_effect = Exception("Database connection error")

        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }

        # Act
        response = test_client.post(
            '/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # Assert
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert response_data['error'] == "Database connection error"
