"""
Pytest configuration and fixtures for LLM evaluation tests
"""
import pytest
import requests
import os

BASE_URL = os.getenv('LLM_API_URL', 'http://localhost:3100')


@pytest.fixture
def api_client():
    """HTTP client for the mock LLM API"""
    class APIClient:
        def __init__(self, base_url):
            self.base_url = base_url

        def chat(self, message, system_prompt=None):
            """Send a chat completion request"""
            messages = []
            if system_prompt:
                messages.append({'role': 'system', 'content': system_prompt})
            messages.append({'role': 'user', 'content': message})

            response = requests.post(
                f'{self.base_url}/v1/chat/completions',
                json={'messages': messages, 'model': 'mock-llm-v1'},
                timeout=10
            )
            return response.json()

        def search_knowledge(self, query):
            """Search the knowledge base"""
            response = requests.get(
                f'{self.base_url}/v1/knowledge/search',
                params={'query': query},
                timeout=10
            )
            return response.json()

        def health(self):
            """Check API health"""
            response = requests.get(f'{self.base_url}/health', timeout=5)
            return response.json()

    return APIClient(BASE_URL)


@pytest.fixture
def knowledge_base():
    """Reference knowledge base for fact-checking"""
    return {
        'return_policy': {
            'days': 30,
            'conditions': ['unused', 'original packaging', 'receipt required'],
            'refund_time': '5-7 business days'
        },
        'shipping': {
            'standard': '5-7 business days',
            'express': '2-3 days',
            'express_cost': 9.99,
            'free_threshold': 50
        },
        'products': {
            'laptop_pro_x1': {
                'price': 1299,
                'ram': '16GB',
                'storage': '512GB SSD',
                'processor': 'Intel i7',
                'battery': '10 hours'
            },
            'headphones_max': {
                'price': 249,
                'battery': '30 hours',
                'colors': ['black', 'white', 'blue'],
                'features': ['noise cancellation', 'Bluetooth 5.0']
            }
        },
        'support': {
            'phone': '1-800-555-0123',
            'email': 'support@techstore.com',
            'hours': '24/7'
        }
    }
