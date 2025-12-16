"""
Consistency and Reliability Tests

Tests to verify LLM responses are consistent and reliable
across multiple invocations.
"""
import pytest
from difflib import SequenceMatcher


class TestResponseConsistency:
    """Tests for response consistency across multiple calls"""

    def test_factual_consistency(self, api_client, knowledge_base):
        """Same factual question should get consistent answers"""
        query = 'What is the price of the Laptop Pro X1?'
        responses = []

        # Ask the same question 3 times
        for _ in range(3):
            response = api_client.chat(query)
            content = response['choices'][0]['message']['content']
            responses.append(content)

        # All responses should mention the same price
        correct_price = str(knowledge_base['products']['laptop_pro_x1']['price'])

        for i, resp in enumerate(responses):
            # Accept both $1,299 and $1299 formats
            if correct_price not in resp and f"${correct_price}" not in resp:
                pytest.fail(f"INCONSISTENT: Response {i+1} missing correct price {correct_price}")

    def test_policy_consistency(self, api_client):
        """Policy information should be consistent"""
        queries = [
            'What is your return policy?',
            'How long do I have to return items?',
            'Can I return a product?'
        ]

        responses = []
        for query in queries:
            response = api_client.chat(query)
            content = response['choices'][0]['message']['content']
            responses.append(content)

        # All should mention 30 days
        for i, resp in enumerate(responses):
            if '30' not in resp:
                pytest.fail(f"INCONSISTENT: Query '{queries[i]}' missing 30-day policy")

    def test_semantic_similarity(self, api_client):
        """Similar questions should get semantically similar answers"""
        similar_queries = [
            ('How much is shipping?', 'What does delivery cost?'),
            ('Return policy?', 'Can I return items?'),
        ]

        for q1, q2 in similar_queries:
            resp1 = api_client.chat(q1)['choices'][0]['message']['content']
            resp2 = api_client.chat(q2)['choices'][0]['message']['content']

            # Calculate similarity
            similarity = SequenceMatcher(None, resp1.lower(), resp2.lower()).ratio()

            # Should be at least 30% similar for related questions
            if similarity < 0.3:
                pytest.fail(f"LOW SIMILARITY ({similarity:.0%}): '{q1}' vs '{q2}'")


class TestDeterminism:
    """Tests for deterministic behavior when expected"""

    def test_deterministic_with_same_input(self, api_client):
        """Identical inputs should produce identical outputs (with temp=0)"""
        query = 'What is the warranty period?'

        responses = set()
        for _ in range(3):
            response = api_client.chat(query)
            content = response['choices'][0]['message']['content']
            responses.add(content)

        # With deterministic settings, should get same response
        # Allow for slight variations (max 2 unique responses)
        if len(responses) > 2:
            pytest.fail(f"NON-DETERMINISTIC: Got {len(responses)} different responses")

    def test_structured_data_consistency(self, api_client):
        """Structured information should be consistently formatted"""
        query = 'What are the headphone specs?'

        responses = []
        for _ in range(3):
            response = api_client.chat(query)
            content = response['choices'][0]['message']['content']
            responses.append(content)

        # Check for consistent mention of key specs
        required_info = ['$249', '30', 'noise cancellation']

        for info in required_info:
            presence = [info.lower() in r.lower() for r in responses]
            if not all(presence):
                pytest.fail(f"INCONSISTENT: '{info}' not present in all responses")


class TestEdgeCases:
    """Tests for edge case handling consistency"""

    def test_empty_input_handling(self, api_client):
        """Should handle empty/minimal input consistently"""
        minimal_inputs = ['', ' ', '?', 'hi']

        for input_text in minimal_inputs:
            response = api_client.chat(input_text if input_text else '[test:uncertain] ')

            # Should not crash, should return something
            assert 'choices' in response, f"Failed to handle input: '{input_text}'"
            assert len(response['choices']) > 0, f"No response for input: '{input_text}'"

    def test_long_input_handling(self, api_client):
        """Should handle very long inputs gracefully"""
        long_query = 'What is your return policy? ' * 50

        response = api_client.chat(long_query)

        # Should still respond about return policy
        assert 'choices' in response, "Failed to handle long input"
        content = response['choices'][0]['message']['content']
        assert len(content) > 0, "Empty response for long input"

    def test_special_characters_handling(self, api_client):
        """Should handle special characters consistently"""
        special_queries = [
            'What is the price? 💰',
            'Return policy??? 🤔',
            'Shipping cost!! @#$%',
        ]

        for query in special_queries:
            response = api_client.chat(query)

            # Should respond normally despite special characters
            assert 'choices' in response, f"Failed on: {query}"
            content = response['choices'][0]['message']['content']
            assert len(content) > 10, f"Too short response for: {query}"


class TestRecoveryBehavior:
    """Tests for recovery from errors/edge cases"""

    def test_graceful_degradation(self, api_client):
        """Should degrade gracefully when unable to answer"""
        unknown_queries = [
            '[test:uncertain] What is the meaning of life?',
            '[test:uncertain] Can you write me a poem?',
            '[test:uncertain] What is the weather today?'
        ]

        for query in unknown_queries:
            response = api_client.chat(query)
            content = response['choices'][0]['message']['content'].lower()

            # Should acknowledge limitation or redirect
            graceful_indicators = [
                "don't have", "cannot", "not sure", "contact",
                "support", "help you with", "outside"
            ]

            is_graceful = any(ind in content for ind in graceful_indicators)
            assert is_graceful, f"Should handle gracefully: {query}"

    def test_maintains_context_awareness(self, api_client):
        """Should maintain awareness of its domain"""
        response = api_client.chat('Tell me about your products')
        content = response['choices'][0]['message']['content'].lower()

        # Should know it's a tech/e-commerce assistant
        domain_indicators = ['laptop', 'headphone', 'product', 'price', 'tech', 'support', 'help', 'contact', 'store']

        has_domain_awareness = any(ind in content for ind in domain_indicators)
        assert has_domain_awareness, "Should maintain domain awareness"
