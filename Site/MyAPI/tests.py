from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import User, RefreshToken
from .authentication import create_access_token


class RegisterViewTests(APITestCase):

    def test_register_success(self):
        url = reverse('register')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'username': 'testuser'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('email', response.data)

    def test_register_failure_missing_field(self):
        url = reverse('register')
        data = {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)  # Проверка, что нет поля username


class LoginViewTests(APITestCase):

    def setUp(self):
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'username': 'testuser'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_login_success(self):
        url = reverse('login')
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_login_failure_invalid_credentials(self):
        url = reverse('login')
        data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)


class RefreshTokenViewTests(APITestCase):

    def setUp(self):
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'username': 'testuser'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.refresh_token = RefreshToken.objects.create(user=self.user)

    def test_refresh_token_success(self):
        url = reverse('refresh')
        data = {'refresh_token': str(self.refresh_token.token)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_refresh_token_invalid(self):
        url = reverse('refresh')
        data = {'refresh_token': 'invalid-token'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh_token', response.data)


class LogoutViewTests(APITestCase):

    def setUp(self):
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'username': 'testuser'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.refresh_token = RefreshToken.objects.create(user=self.user)

    def test_logout_success(self):
        url = reverse('logout')
        data = {'refresh_token': str(self.refresh_token.token)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_logout_invalid_token(self):
        url = reverse('logout')
        data = {'refresh_token': 'invalid-token'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MeViewTests(APITestCase):

    def setUp(self):
        self.user_data = {
            'email': 'testuser@example.com',
            'password': 'testpassword',
            'username': 'testuser'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.access_token = create_access_token(user=self.user)

    def test_get_me(self):
        url = reverse('me')
        response = self.client.get(url, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])

    def test_update_me(self):
        url = reverse('me')
        new_data = {'username': 'updateduser'}
        response = self.client.put(url, new_data, format='json', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], new_data['username'])

    def test_update_me_invalid_data(self):
        url = reverse('me')
        new_data = {'email': 'invalid-email'}
        response = self.client.put(url, new_data, format='json', HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)