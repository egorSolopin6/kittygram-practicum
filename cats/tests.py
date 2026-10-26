from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from rest_framework.test import APITestCase
from .models import Achievement, Cat
from showcase.roles import configure_roles, OWNER_GROUP


class PracticumTests(APITestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user('practice_owner', password='test-only-password')
        self.other = get_user_model().objects.create_user('practice_other', password='test-only-password')
        groups = configure_roles()
        self.owner.groups.add(groups[OWNER_GROUP])
        self.other.groups.add(groups[OWNER_GROUP])
        self.achievement = Achievement.objects.create(name='Ловит мяч', description='Приносит игрушку.')
        self.cat = Cat.objects.create(name='Луна', color='black', birth_year=2022, owner=self.owner)
        self.cat2 = Cat.objects.create(name='Алиса', color='white', birth_year=2024, owner=self.owner)
        self.foreign = Cat.objects.create(name='Персик', color='orange', birth_year=2022, owner=self.other)

    def test_achievement_dictionary_is_public_and_read_only(self):
        response = self.client.get('/api/achievements/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'][0]['id'], self.achievement.id)
        self.assertEqual(self.client.get(f'/api/achievements/{self.achievement.id}/').status_code, 200)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.post('/api/achievements/', {'name': 'Нельзя'}).status_code, 405)

    def test_crud_achievement_relation_and_invalid_ids(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post('/api/cats/', {'name':'Мурка','color':'gray','birth_year':2023,'achievements':[self.achievement.id]})
        self.assertEqual(response.status_code, 201)
        cat = Cat.objects.get(id=response.data['id'])
        self.assertEqual(list(cat.achievements.all()), [self.achievement])
        response = self.client.put(f'/api/cats/{cat.id}/', {'name':'Мурка','color':'white','achievements':[]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['achievements'], [])
        self.assertEqual(self.client.patch(f'/api/cats/{cat.id}/', {'achievements':[999999]}).status_code, 400)
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.patch(f'/api/cats/{cat.id}/', {'achievements':[self.achievement.id]}).status_code, 404)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(f'/api/cats/{cat.id}/').status_code, 204)

    def test_validation_returns_all_three_errors(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post('/api/cats/', {'name':'А','color':'x','birth_year':1899})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.data), {'name','color','birth_year'})

    def test_filters_search_ordering_and_pagination_preserve_ownership(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get('/api/cats/?search=black&birth_year=2022&owner=practice_owner&page_size=1')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.cat.id)
        self.assertEqual(self.client.get('/api/cats/?owner=practice_other').data['count'], 0)
        response = self.client.get('/api/cats/?ordering=name&page_size=1')
        self.assertEqual(response.data['results'][0]['id'], self.cat2.id)
        self.assertIsNotNone(response.data['next'])
        self.assertEqual(self.client.get('/api/cats/?birth_year=bad').status_code, 400)

    def test_profile_is_private_and_contains_no_credentials(self):
        self.assertEqual(self.client.get('/api/users/me/').status_code, 401)
        self.client.force_authenticate(self.owner)
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.data['username'], 'practice_owner')
        self.assertNotIn('password', response.data)
        self.assertNotIn('token', response.data)

    def test_openapi_and_redoc_are_available_without_login(self):
        response = self.client.get('/api/openapi.json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('/api/achievements/', response.data['paths'])
        self.assertIn('/api/users/me/', response.data['paths'])
        self.assertIn('post', response.data['paths']['/api/cats/'])
        self.assertContains(self.client.get('/api/docs/'), 'redoc.standalone.js')

    def test_achievement_name_is_unique(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Achievement.objects.create(name=self.achievement.name)
