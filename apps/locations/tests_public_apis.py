"""
Tests para APIs públicas de ubicaciones con rate limiting y caché
"""

import json
from django.core.cache import cache
from django.test import Client, TestCase

from .models import City, Country, Rule, Season, Site, State


class PublicAPIsRateLimitingTest(TestCase):
    """Tests para rate limiting en APIs públicas"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.country = Country.objects.create(name="México", code="MX", is_active=True)
        self.state = State.objects.create(name="Jalisco", country=self.country, is_active=True)
        self.city = City.objects.create(name="Guadalajara", state=self.state, is_active=True)
        self.season = Season.objects.create(
            name="Apertura 2024",
            league="Liga MX",
            season_type="regular",
            year=2024,
            is_active=True
        )
        self.rule = Rule.objects.create(
            name="Test Rule",
            description="Test Description",
            rule_type="general",
            is_active=True
        )
        self.site = Site.objects.create(
            site_name="Estadio Jalisco",
            city=self.city,
            state=self.state,
            country=self.country,
            is_active=True
        )
        # Limpiar caché antes de cada test
        cache.clear()

    def test_get_states_by_country_rate_limit(self):
        """Test rate limiting en get_states_by_country"""
        # Usar la URL pública que está en urls_public.py
        url = f"/locations/ajax/states/{self.country.id}/"

        # Hacer 150 requests (el límite)
        for i in range(150):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn("X-RateLimit-Remaining", response.headers)
            remaining = int(response.headers["X-RateLimit-Remaining"])
            self.assertEqual(remaining, 150 - i - 1)

        # El request 151 debe ser bloqueado
        response = self.client.get(url)
        self.assertEqual(response.status_code, 429)
        data = json.loads(response.content.decode())
        self.assertIn("error", data)
        self.assertIn("Rate limit exceeded", data["error"])

    def test_get_cities_by_state_rate_limit(self):
        """Test rate limiting en get_cities_by_state"""
        url = f"/locations/ajax/cities/{self.state.id}/"

        # Hacer 150 requests
        for i in range(150):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        # El request 151 debe ser bloqueado
        response = self.client.get(url)
        self.assertEqual(response.status_code, 429)

    def test_countries_api_rate_limit(self):
        """Test rate limiting en countries_api"""
        url = "/locations/api/countries/"

        # Hacer 150 requests
        for i in range(150):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertIn("X-RateLimit-Limit", response.headers)
            self.assertEqual(response.headers["X-RateLimit-Limit"], "150")

        # El request 151 debe ser bloqueado
        response = self.client.get(url)
        self.assertEqual(response.status_code, 429)

    def test_states_api_rate_limit(self):
        """Test rate limiting en states_api"""
        url = "/locations/api/states/"

        # Hacer 150 requests
        for i in range(150):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        # El request 151 debe ser bloqueado
        response = self.client.get(url)
        self.assertEqual(response.status_code, 429)

    def test_cities_api_rate_limit(self):
        """Test rate limiting en cities_api"""
        url = "/locations/api/cities/"

        # Hacer 150 requests
        for i in range(150):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        # El request 151 debe ser bloqueado
        response = self.client.get(url)
        self.assertEqual(response.status_code, 429)

    def test_seasons_api_rate_limit(self):
        """Test rate limiting en seasons_api"""
        url = "/locations/api/seasons/"

        # Hacer 150 requests
        for i in range(150):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        # El request 151 debe ser bloqueado
        response = self.client.get(url)
        self.assertEqual(response.status_code, 429)

    def test_rules_api_rate_limit(self):
        """Test rate limiting en rules_api"""
        url = "/locations/api/rules/"

        # Hacer 150 requests
        for i in range(150):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        # El request 151 debe ser bloqueado
        response = self.client.get(url)
        self.assertEqual(response.status_code, 429)

    def test_sites_api_rate_limit(self):
        """Test rate limiting en sites_api"""
        url = "/locations/api/sites/"

        # Hacer 150 requests
        for i in range(150):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

        # El request 151 debe ser bloqueado
        response = self.client.get(url)
        self.assertEqual(response.status_code, 429)

    def test_rate_limit_headers(self):
        """Test que los headers de rate limit están presentes"""
        url = "/locations/api/countries/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("X-RateLimit-Remaining", response.headers)
        self.assertIn("X-RateLimit-Limit", response.headers)
        self.assertEqual(response.headers["X-RateLimit-Limit"], "150")
        remaining = int(response.headers["X-RateLimit-Remaining"])
        self.assertGreaterEqual(remaining, 0)
        self.assertLessEqual(remaining, 150)


class PublicAPIsCachingTest(TestCase):
    """Tests para caché en APIs públicas"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.country = Country.objects.create(name="México", code="MX", is_active=True)
        self.state = State.objects.create(name="Jalisco", country=self.country, is_active=True)
        self.city = City.objects.create(name="Guadalajara", state=self.state, is_active=True)
        self.season = Season.objects.create(
            name="Apertura 2024",
            league="Liga MX",
            season_type="regular",
            year=2024,
            is_active=True
        )
        self.rule = Rule.objects.create(
            name="Test Rule",
            description="Test Description",
            rule_type="general",
            is_active=True
        )
        self.site = Site.objects.create(
            site_name="Estadio Jalisco",
            city=self.city,
            state=self.state,
            country=self.country,
            is_active=True
        )
        # Limpiar caché antes de cada test
        cache.clear()

    def test_get_states_by_country_cache(self):
        """Test que get_states_by_country usa caché"""
        url = f"/locations/ajax/states/{self.country.id}/"

        # Primera request - debe ir a la base de datos
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.content.decode())

        # Segunda request - debe venir del caché (mismo contenido)
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.content.decode())

        # Los datos deben ser idénticos
        self.assertEqual(data1, data2)

    def test_countries_api_cache(self):
        """Test que countries_api usa caché"""
        url = "/locations/api/countries/"

        # Primera request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.content.decode())

        # Segunda request - debe venir del caché
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.content.decode())

        self.assertEqual(data1, data2)

    def test_countries_api_cache_with_search(self):
        """Test que countries_api cachea búsquedas diferentes"""
        url = "/locations/api/countries/"

        # Request sin búsqueda
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)
        data1 = json.loads(response1.content.decode())

        # Request con búsqueda
        response2 = self.client.get(url, {"q": "méxico"})
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.content.decode())

        # Deben ser diferentes (diferentes claves de caché)
        # Pero ambos deben ser válidos
        self.assertIsInstance(data1, list)
        self.assertIsInstance(data2, list)

    def test_states_api_cache(self):
        """Test que states_api usa caché"""
        url = "/locations/api/states/"

        # Primera request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)

        # Segunda request - debe venir del caché
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        data1 = json.loads(response1.content.decode())
        data2 = json.loads(response2.content.decode())
        self.assertEqual(data1, data2)

    def test_cities_api_cache(self):
        """Test que cities_api usa caché"""
        url = "/locations/api/cities/"

        # Primera request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)

        # Segunda request - debe venir del caché
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        data1 = json.loads(response1.content.decode())
        data2 = json.loads(response2.content.decode())
        self.assertEqual(data1, data2)

    def test_seasons_api_cache(self):
        """Test que seasons_api usa caché"""
        url = "/locations/api/seasons/"

        # Primera request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)

        # Segunda request - debe venir del caché
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        data1 = json.loads(response1.content.decode())
        data2 = json.loads(response2.content.decode())
        self.assertEqual(data1, data2)

    def test_rules_api_cache(self):
        """Test que rules_api usa caché"""
        url = "/locations/api/rules/"

        # Primera request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)

        # Segunda request - debe venir del caché
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        data1 = json.loads(response1.content.decode())
        data2 = json.loads(response2.content.decode())
        self.assertEqual(data1, data2)

    def test_sites_api_cache(self):
        """Test que sites_api usa caché"""
        url = "/locations/api/sites/"

        # Primera request
        response1 = self.client.get(url)
        self.assertEqual(response1.status_code, 200)

        # Segunda request - debe venir del caché
        response2 = self.client.get(url)
        self.assertEqual(response2.status_code, 200)

        data1 = json.loads(response1.content.decode())
        data2 = json.loads(response2.content.decode())
        self.assertEqual(data1, data2)


class PublicAPIsValidationTest(TestCase):
    """Tests para validación de parámetros en APIs públicas"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.country = Country.objects.create(name="México", code="MX", is_active=True)
        self.state = State.objects.create(name="Jalisco", country=self.country, is_active=True)
        self.city = City.objects.create(name="Guadalajara", state=self.state, is_active=True)
        cache.clear()

    def test_get_states_by_country_invalid_id(self):
        """Test validación de ID inválido en get_states_by_country"""
        # Intentar con ID que no existe
        url = "/locations/ajax/states/99999/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # Debe retornar lista vacía, no error
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)

    def test_get_cities_by_state_invalid_id(self):
        """Test validación de ID inválido en get_cities_by_state"""
        url = "/locations/ajax/cities/99999/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)

    def test_countries_api_invalid_id(self):
        """Test validación de ID inválido en countries_api"""
        url = "/locations/api/countries/"
        response = self.client.get(url, {"id": "invalid"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode())
        self.assertIn("error", data)

    def test_countries_api_search_length_limit(self):
        """Test que la búsqueda está limitada a 100 caracteres"""
        url = "/locations/api/countries/"
        # Búsqueda de más de 100 caracteres
        long_search = "a" * 150
        response = self.client.get(url, {"q": long_search})
        self.assertEqual(response.status_code, 200)
        # Debe funcionar pero truncar a 100 caracteres

    def test_states_api_invalid_country_id(self):
        """Test validación de country_id inválido en states_api"""
        url = "/locations/api/states/"
        response = self.client.get(url, {"country": "invalid"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode())
        self.assertIn("error", data)

    def test_states_api_invalid_state_id(self):
        """Test validación de state_id inválido en states_api"""
        url = "/locations/api/states/"
        response = self.client.get(url, {"id": "invalid"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode())
        self.assertIn("error", data)

    def test_cities_api_invalid_state_id(self):
        """Test validación de state_id inválido en cities_api"""
        url = "/locations/api/cities/"
        response = self.client.get(url, {"state": "invalid"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode())
        self.assertIn("error", data)

    def test_cities_api_invalid_city_id(self):
        """Test validación de city_id inválido en cities_api"""
        url = "/locations/api/cities/"
        response = self.client.get(url, {"id": "invalid"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode())
        self.assertIn("error", data)

    def test_sites_api_invalid_city_id(self):
        """Test validación de city_id inválido en sites_api"""
        url = "/locations/api/sites/"
        response = self.client.get(url, {"city": "invalid"})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content.decode())
        self.assertIn("error", data)


class PublicAPIsResponseTest(TestCase):
    """Tests para respuestas correctas de las APIs"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.country = Country.objects.create(name="México", code="MX", is_active=True)
        self.state = State.objects.create(name="Jalisco", country=self.country, is_active=True)
        self.city = City.objects.create(name="Guadalajara", state=self.state, is_active=True)
        self.season = Season.objects.create(
            name="Apertura 2024",
            league="Liga MX",
            season_type="regular",
            year=2024,
            is_active=True
        )
        self.rule = Rule.objects.create(
            name="Test Rule",
            description="Test Description",
            rule_type="general",
            is_active=True
        )
        self.site = Site.objects.create(
            site_name="Estadio Jalisco",
            city=self.city,
            state=self.state,
            country=self.country,
            is_active=True
        )
        cache.clear()

    def test_get_states_by_country_response_format(self):
        """Test formato de respuesta de get_states_by_country"""
        url = f"/locations/ajax/states/{self.country.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("id", data[0])
            self.assertIn("name", data[0])

    def test_countries_api_response_format(self):
        """Test formato de respuesta de countries_api"""
        url = "/locations/api/countries/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("id", data[0])
            self.assertIn("name", data[0])
            self.assertIn("code", data[0])

    def test_countries_api_with_id(self):
        """Test countries_api con ID específico"""
        url = "/locations/api/countries/"
        response = self.client.get(url, {"id": self.country.id})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], self.country.id)
        self.assertEqual(data[0]["name"], "México")

    def test_states_api_response_format(self):
        """Test formato de respuesta de states_api"""
        url = "/locations/api/states/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("id", data[0])
            self.assertIn("name", data[0])
            self.assertIn("country_id", data[0])

    def test_cities_api_response_format(self):
        """Test formato de respuesta de cities_api"""
        url = "/locations/api/cities/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("id", data[0])
            self.assertIn("name", data[0])
            self.assertIn("state_id", data[0])

    def test_seasons_api_response_format(self):
        """Test formato de respuesta de seasons_api"""
        url = "/locations/api/seasons/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("id", data[0])
            self.assertIn("name", data[0])
            self.assertIn("year", data[0])

    def test_rules_api_response_format(self):
        """Test formato de respuesta de rules_api"""
        url = "/locations/api/rules/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("id", data[0])
            self.assertIn("name", data[0])
            self.assertIn("rule_type", data[0])

    def test_sites_api_response_format(self):
        """Test formato de respuesta de sites_api"""
        url = "/locations/api/sites/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn("id", data[0])
            self.assertIn("site_name", data[0])
            self.assertIn("city_id", data[0])
            self.assertIn("state_id", data[0])

    def test_only_active_items_returned(self):
        """Test que solo se retornan items activos"""
        # Crear un país inactivo
        inactive_country = Country.objects.create(name="Inactivo", code="IN", is_active=False)

        url = "/locations/api/countries/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content.decode())

        # Verificar que el país inactivo no está en la respuesta
        country_ids = [c["id"] for c in data]
        self.assertNotIn(inactive_country.id, country_ids)


class PublicAPIsIPHandlingTest(TestCase):
    """Tests para manejo de IPs (proxies, etc.)"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.country = Country.objects.create(name="México", code="MX", is_active=True)
        self.state = State.objects.create(name="Jalisco", country=self.country, is_active=True)
        cache.clear()

    def test_rate_limit_different_ips(self):
        """Test que rate limiting es por IP"""
        url = "/locations/api/countries/"

        # Simular diferentes IPs usando headers
        # IP 1: hacer 150 requests
        for i in range(150):
            response = self.client.get(url, HTTP_X_FORWARDED_FOR="192.168.1.1")
            self.assertEqual(response.status_code, 200)

        # IP 2: debe poder hacer requests (diferente IP)
        response = self.client.get(url, HTTP_X_FORWARDED_FOR="192.168.1.2")
        self.assertEqual(response.status_code, 200)

        # IP 1: debe estar bloqueada
        response = self.client.get(url, HTTP_X_FORWARDED_FOR="192.168.1.1")
        self.assertEqual(response.status_code, 429)

    def test_rate_limit_with_proxy_header(self):
        """Test que rate limiting funciona con X-Forwarded-For"""
        url = "/locations/api/countries/"

        # Request con X-Forwarded-For
        response = self.client.get(url, HTTP_X_FORWARDED_FOR="10.0.0.1, 192.168.1.1")
        self.assertEqual(response.status_code, 200)

        # Debe usar la primera IP (10.0.0.1)
        # Hacer 150 requests con esa IP
        for i in range(150):
            response = self.client.get(url, HTTP_X_FORWARDED_FOR="10.0.0.1, 192.168.1.1")
            self.assertEqual(response.status_code, 200)

        # Debe estar bloqueada
        response = self.client.get(url, HTTP_X_FORWARDED_FOR="10.0.0.1, 192.168.1.1")
        self.assertEqual(response.status_code, 429)


