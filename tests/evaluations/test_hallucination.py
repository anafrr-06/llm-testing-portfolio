"""
Hallucination Detection Tests

Tests to verify the LLM doesn't generate false information
not present in the knowledge base.
"""
import pytest
import re


class TestPriceHallucination:
    """Test that product prices are accurate"""

    def test_laptop_price_correct(self, api_client, knowledge_base):
        """Verify laptop price matches knowledge base"""
        response = api_client.chat('What is the price of the Laptop Pro X1?')
        content = response['choices'][0]['message']['content']

        correct_price = knowledge_base['products']['laptop_pro_x1']['price']
        assert f'${correct_price:,}' in content or f'${correct_price}' in content, \
            f"Expected price ${correct_price} not found in response"

    def test_laptop_price_hallucination_detected(self, api_client):
        """Verify we can detect price hallucinations"""
        response = api_client.chat('[test:hallucination_price] What is the laptop price?')
        content = response['choices'][0]['message']['content']
        meta = response.get('_meta', {})

        assert meta.get('grounded') is False, "Hallucinated response should be marked as not grounded"
        assert meta.get('issue') == 'hallucination', "Issue type should be hallucination"
        assert '$599' in content, "Hallucinated price should be present for detection"

    def test_headphones_price_correct(self, api_client, knowledge_base):
        """Verify headphones price matches knowledge base"""
        response = api_client.chat('How much are the Wireless Headphones Max?')
        content = response['choices'][0]['message']['content']

        correct_price = knowledge_base['products']['headphones_max']['price']
        assert f'${correct_price}' in content, \
            f"Expected price ${correct_price} not found in response"


class TestPolicyHallucination:
    """Test that policy information is accurate"""

    def test_return_days_correct(self, api_client, knowledge_base):
        """Verify return policy days are accurate"""
        response = api_client.chat('How many days do I have to return a product?')
        content = response['choices'][0]['message']['content']

        correct_days = knowledge_base['return_policy']['days']
        assert str(correct_days) in content, \
            f"Expected {correct_days} days return policy not found"

    def test_return_policy_hallucination_detected(self, api_client):
        """Verify we can detect policy hallucinations"""
        response = api_client.chat('[test:hallucination_policy] What is your return policy?')
        content = response['choices'][0]['message']['content']
        meta = response.get('_meta', {})

        assert meta.get('grounded') is False
        assert '90 days' in content, "Hallucinated 90-day policy should be present"
        assert '30' not in content, "Correct 30-day policy should not be present in hallucination"

    def test_shipping_threshold_correct(self, api_client, knowledge_base):
        """Verify free shipping threshold is accurate"""
        response = api_client.chat('Is there free shipping?')
        content = response['choices'][0]['message']['content']

        threshold = knowledge_base['shipping']['free_threshold']
        assert f'${threshold}' in content, \
            f"Expected free shipping threshold ${threshold} not found"


class TestFeatureHallucination:
    """Test that product features are accurate"""

    def test_headphones_battery_correct(self, api_client, knowledge_base):
        """Verify headphones battery life is accurate"""
        response = api_client.chat('What is the battery life of the headphones?')
        content = response['choices'][0]['message']['content']

        # Accept "30 hours" or "30-hour"
        assert '30' in content and 'hour' in content.lower(), \
            "Expected 30-hour battery life not found"

    def test_headphones_battery_hallucination_detected(self, api_client):
        """Verify we can detect feature hallucinations"""
        response = api_client.chat('[test:hallucination_feature] Tell me about headphones battery')
        content = response['choices'][0]['message']['content']
        meta = response.get('_meta', {})

        assert meta.get('grounded') is False
        assert '100-hour' in content, "Hallucinated battery life should be present"

    def test_laptop_specs_correct(self, api_client, knowledge_base):
        """Verify laptop specifications are accurate"""
        response = api_client.chat('What are the specs of the Laptop Pro X1?')
        content = response['choices'][0]['message']['content']

        laptop = knowledge_base['products']['laptop_pro_x1']
        assert laptop['ram'] in content, f"Expected RAM {laptop['ram']} not found"
        assert 'i7' in content.lower(), "Expected processor i7 not found"


class TestGroundednessMetadata:
    """Test that grounded/hallucination metadata is correct"""

    def test_grounded_response_metadata(self, api_client):
        """Verify grounded responses are marked correctly"""
        response = api_client.chat('What is your return policy?')
        meta = response.get('_meta', {})

        assert meta.get('grounded') is True, "Factual response should be marked as grounded"
        assert meta.get('issue') is None, "Grounded response should have no issue"

    def test_hallucinated_response_metadata(self, api_client):
        """Verify hallucinated responses are marked correctly"""
        response = api_client.chat('[test:hallucination_price] Tell me about laptop')
        meta = response.get('_meta', {})

        assert meta.get('grounded') is False, "Hallucinated response should not be grounded"
        assert meta.get('issue') == 'hallucination'
        assert meta.get('details') is not None, "Should include details about the hallucination"
