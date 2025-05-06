import json
# import pytest
from unittest.mock import patch, MagicMock
from uuid import UUID

from questrya.users.domain import User
# from questrya.common.value_objects.email import Email


class TestUserCreateRoute:
    @patch('questrya.users.routes.user_service')
    def test_create_user_successfully(self, mock_user_service, test_client):
        # GIVEN
        mock_user = MagicMock(spec=User)
        mock_user.uuid = UUID('12345678-1234-5678-1234-567812345678')
        mock_user_service.register_user.return_value = mock_user

        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }

        # WHEN
        response = test_client.post(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # THEN
        assert response.status_code == 201

        # Verify service was called with correct parameters
        mock_user_service.register_user.assert_called_once_with(
            "testuser", "test@example.com", "password123"
        )

        response_data = json.loads(response.data)
        assert 'uuid' in response_data
        assert response_data['uuid'] == '12345678-1234-5678-1234-567812345678'

    def test_create_user_invalid_data_must_fail(self, test_client):
        # invalid email
        request_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123"
        }

        response = test_client.post(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'invalid email address' in response_data['error'].lower()

        # short password
        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "short"
        }

        response = test_client.post(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'password must be at least 8 characters long' in response_data['error'].lower()

        # empty username
        request_data = {
            "username": "",
            "email": "test@example.com",
            "password": "password123"
        }

        response = test_client.post(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'username cannot be empty' in response_data['error'].lower()

    @patch('questrya.users.routes.user_service')
    def test_create_user_service_error(self, mock_user_service, test_client):
        # GIVEN
        mock_user_service.register_user.side_effect = ValueError("User already exists")

        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }

        # WHEN
        response = test_client.post(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # THEN
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert response_data['error'] == "User already exists"

    @patch('questrya.users.routes.user_service')
    def test_create_user_server_error(self, mock_user_service, test_client):
        # GIVEN
        mock_user_service.register_user.side_effect = Exception("Database connection error")

        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }

        # WHEN
        response = test_client.post(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # THEN
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert response_data['error'] == "Database connection error"


class TestUserUpdateRoute:
    def create_user_with_api(self, test_client):
        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        response = test_client.post(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        assert response.status_code == 201
        response_data = response.json
        print(response_data)

    @patch('questrya.users.routes.get_jwt_identity')
    def test_update_user_successfully(self, mock_jwt_identity, test_client):
        # GIVEN
        # FIXME: continue from here, this was failing
        created_user = self.create_user_with_api(test_client)

        # ---
        user_uuid = '12345678-1234-5678-1234-567812345678'
        mock_jwt_identity.return_value = user_uuid

        mock_user = MagicMock(spec=User)
        mock_user.uuid = UUID(user_uuid)
        mock_user.email = "updated@example.com"
        # mock_user_service.update_user.return_value = mock_user

        request_data = {
            "email": "updated@example.com",
            "password": "newpassword123"
        }

        # WHEN
        response = test_client.patch(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # THEN
        assert response.status_code == 200

        # Verify service was called with correct parameters
        # mock_user_service.update_user.assert_called_once_with(
        #     user_uuid,
        #     email="updated@example.com",
        #     password="newpassword123"
        # )

        response_data = json.loads(response.data)
        assert 'uuid' in response_data
        assert response_data['uuid'] == user_uuid
        assert response_data['email'] == "updated@example.com"
        assert response_data['password'] == "UPDATED"

    @patch('questrya.users.routes.user_service')
    @patch('questrya.users.routes.get_jwt_identity')
    def test_update_user_invalid_data_must_fail(self, mock_jwt_identity, mock_user_service, test_client):
        # GIVEN
        user_uuid = '12345678-1234-5678-1234-567812345678'
        mock_jwt_identity.return_value = user_uuid

        # invalid email
        request_data = {
            "email": "invalid-email",
            "password": "newpassword123"
        }

        # WHEN
        response = test_client.patch(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # THEN
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'invalid email address' in response_data['error'].lower()

        # short password
        request_data = {
            "email": "valid@example.com",
            "password": "short"
        }

        response = test_client.patch(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'password must be at least 8 characters long' in response_data['error'].lower()

    @patch('questrya.users.routes.user_service')
    @patch('questrya.users.routes.get_jwt_identity')
    def test_update_user_service_error(self, mock_jwt_identity, mock_user_service, test_client):
        # GIVEN
        user_uuid = '12345678-1234-5678-1234-567812345678'
        mock_jwt_identity.return_value = user_uuid
        mock_user_service.update_user.side_effect = ValueError("User not found")

        request_data = {
            "email": "updated@example.com",
            "password": "newpassword123"
        }

        # WHEN
        response = test_client.patch(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # THEN
        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert response_data['error'] == "User not found"

    @patch('questrya.users.routes.user_service')
    @patch('questrya.users.routes.get_jwt_identity')
    def test_update_user_server_error(self, mock_jwt_identity, mock_user_service, test_client):
        # GIVEN
        user_uuid = '12345678-1234-5678-1234-567812345678'
        mock_jwt_identity.return_value = user_uuid
        mock_user_service.update_user.side_effect = Exception("Database connection error")

        request_data = {
            "email": "updated@example.com",
            "password": "newpassword123"
        }

        # WHEN
        response = test_client.patch(
            '/api/users/user',
            data=json.dumps(request_data),
            content_type='application/json'
        )

        # THEN
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert response_data['error'] == "Database connection error"


class TestUserGetRoute:
    @patch('questrya.users.routes.user_service')
    @patch('questrya.users.routes.get_jwt_identity')
    def test_get_user_successfully(self, mock_jwt_identity, mock_user_service, test_client):
        # GIVEN
        user_uuid = '12345678-1234-5678-1234-567812345678'
        mock_jwt_identity.return_value = user_uuid

        mock_user = MagicMock(spec=User)
        mock_user.uuid = UUID(user_uuid)
        mock_user.email = "user@example.com"
        mock_user.username = "testuser"
        mock_user_service.get_user.return_value = mock_user

        # WHEN
        response = test_client.get('/api/users/user')

        # THEN
        assert response.status_code == 200

        # Verify service was called with correct parameters
        mock_user_service.get_user.assert_called_once_with(user_uuid)

        response_data = json.loads(response.data)
        assert 'uuid' in response_data
        assert response_data['uuid'] == user_uuid
        assert response_data['email'] == "user@example.com"
        assert response_data['username'] == "testuser"

    @patch('questrya.users.routes.user_service')
    @patch('questrya.users.routes.get_jwt_identity')
    def test_get_user_server_error(self, mock_jwt_identity, mock_user_service, test_client):
        # GIVEN
        user_uuid = '12345678-1234-5678-1234-567812345678'
        mock_jwt_identity.return_value = user_uuid
        mock_user_service.get_user.side_effect = Exception("Database connection error")

        # WHEN
        response = test_client.get('/api/users/user')

        # THEN
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert response_data['error'] == "Database connection error"
