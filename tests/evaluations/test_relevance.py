"""
Relevance and Quality Tests

Tests to verify LLM responses are relevant, on-topic,
and appropriately handle uncertainty.
"""
import pytest
import time


class TestResponseRelevance:
    """Test that responses are relevant to user queries"""

    def test_return_query_relevant_response(self, api_client):
        """Response to return query should be about returns"""
        response = api_client.chat('What is your return policy?')
        content = response['choices'][0]['message']['content'].lower()

        relevant_terms = ['return', 'refund', 'days', 'policy']
        matches = sum(1 for term in relevant_terms if term in content)

        assert matches >= 2, f"Response should contain relevant terms. Found: {matches}/4"

    def test_shipping_query_relevant_response(self, api_client):
        """Response to shipping query should be about shipping"""
        response = api_client.chat('How long does delivery take?')
        content = response['choices'][0]['message']['content'].lower()

        relevant_terms = ['shipping', 'delivery', 'days', 'business']
        matches = sum(1 for term in relevant_terms if term in content)

        assert matches >= 2, f"Response should contain relevant shipping terms"

    def test_off_topic_response_detected(self, api_client):
        """Should detect when response is off-topic"""
        response = api_client.chat('[test:off_topic] What is your warranty policy?')
        content = response['choices'][0]['message']['content'].lower()
        meta = response.get('_meta', {})

        assert meta.get('issue') == 'off_topic', "Off-topic response should be flagged"
        assert 'warranty' not in content, "Off-topic response shouldn't mention warranty"


class TestUncertaintyHandling:
    """Test appropriate handling of unknown queries"""

    def test_unknown_query_graceful_handling(self, api_client):
        """Should handle unknown queries gracefully"""
        response = api_client.chat('[test:uncertain] Do you sell flying cars?')
        content = response['choices'][0]['message']['content'].lower()

        # Should acknowledge uncertainty or redirect to support
        uncertainty_indicators = ["don't have", "not sure", "contact", "support", "help"]
        has_uncertainty = any(ind in content for ind in uncertainty_indicators)

        assert has_uncertainty, "Should acknowledge uncertainty or redirect to support"

    def test_uncertain_response_not_hallucinated(self, api_client):
        """Uncertain response should not fabricate information"""
        response = api_client.chat('[test:uncertain] What is the price of the quantum computer?')
        meta = response.get('_meta', {})

        # Even though query is unknown, response should be grounded (redirecting to support)
        assert meta.get('grounded') is True, "Uncertainty handling should be grounded"


class TestResponseCompleteness:
    """Test that responses are complete and helpful"""

    def test_product_query_includes_key_info(self, api_client):
        """Product queries should include key information"""
        response = api_client.chat('Tell me about the Laptop Pro X1')
        content = response['choices'][0]['message']['content']

        # Should include price, key specs
        assert '$' in content, "Should include price"
        assert 'GB' in content or 'RAM' in content.upper(), "Should include memory specs"

    def test_support_query_includes_contact(self, api_client):
        """Support queries should include contact information"""
        response = api_client.chat('How can I contact customer support?')
        content = response['choices'][0]['message']['content']

        # Should include at least one contact method
        has_phone = '800' in content or 'phone' in content.lower()
        has_email = '@' in content or 'email' in content.lower()
        has_chat = 'chat' in content.lower()

        assert has_phone or has_email or has_chat, "Should include contact method"


class TestResponseLatency:
    """Test response time requirements"""

    def test_response_time_acceptable(self, api_client):
        """Response should be returned within acceptable time"""
        start = time.time()
        response = api_client.chat('What is your return policy?')
        elapsed = time.time() - start

        assert elapsed < 2.0, f"Response took {elapsed:.2f}s, should be under 2s"
        assert 'choices' in response, "Should return valid response"

    def test_multiple_queries_consistent_latency(self, api_client):
        """Multiple queries should have consistent latency"""
        latencies = []
        queries = [
            'What is shipping cost?',
            'Tell me about laptops',
            'What is your return policy?'
        ]

        for query in queries:
            start = time.time()
            api_client.chat(query)
            latencies.append(time.time() - start)

        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)

        assert max_latency < 2.0, f"Max latency {max_latency:.2f}s exceeds threshold"
        assert max_latency < avg_latency * 3, "Latency variance too high"


class TestResponseFormat:
    """Test response format and structure"""

    def test_response_has_valid_structure(self, api_client):
        """Response should have valid OpenAI-compatible structure"""
        response = api_client.chat('Hello')

        assert 'id' in response, "Should have id field"
        assert 'choices' in response, "Should have choices array"
        assert len(response['choices']) > 0, "Should have at least one choice"
        assert 'message' in response['choices'][0], "Choice should have message"
        assert 'content' in response['choices'][0]['message'], "Message should have content"

    def test_response_includes_usage(self, api_client):
        """Response should include token usage"""
        response = api_client.chat('What is shipping cost?')

        assert 'usage' in response, "Should include usage stats"
        assert 'prompt_tokens' in response['usage'], "Should have prompt_tokens"
        assert 'completion_tokens' in response['usage'], "Should have completion_tokens"
        assert 'total_tokens' in response['usage'], "Should have total_tokens"
