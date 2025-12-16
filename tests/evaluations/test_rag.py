"""
RAG (Retrieval Augmented Generation) Tests

Tests for knowledge base retrieval and grounded responses.
"""
import pytest


class TestKnowledgeBaseRetrieval:
    """Test knowledge base search functionality"""

    def test_search_returns_relevant_documents(self, api_client):
        """Search should return relevant documents"""
        result = api_client.search_knowledge('return')

        assert 'results' in result
        assert len(result['results']) > 0, "Should find documents about returns"

        # Check that return policy document is in results
        titles = [doc['title'] for doc in result['results']]
        assert any('return' in t.lower() for t in titles), \
            "Should find return-related documents"

    def test_search_filters_by_category(self, api_client):
        """Search should find documents in specific categories"""
        result = api_client.search_knowledge('policy')

        assert len(result['results']) > 0
        categories = [doc['category'] for doc in result['results']]
        assert 'policies' in categories, "Should find policy documents"

    def test_product_search(self, api_client):
        """Should find product documents"""
        result = api_client.search_knowledge('laptop')

        assert len(result['results']) > 0
        content = ' '.join([doc['content'] for doc in result['results']])
        assert 'Laptop Pro X1' in content, "Should find laptop product"

    def test_empty_search_returns_empty(self, api_client):
        """Empty search should return empty results"""
        result = api_client.search_knowledge('xyznonexistent123')

        assert 'results' in result
        assert len(result['results']) == 0, "Should return empty for non-matching query"


class TestGroundedResponses:
    """Test that responses are grounded in knowledge base"""

    def test_return_response_matches_knowledge(self, api_client, knowledge_base):
        """Return policy response should match knowledge base"""
        response = api_client.chat('What is your return policy?')
        content = response['choices'][0]['message']['content']

        kb = knowledge_base['return_policy']

        # Verify key facts from knowledge base
        assert str(kb['days']) in content, "Should mention correct return days"
        assert 'refund' in content.lower(), "Should mention refunds"

    def test_shipping_response_matches_knowledge(self, api_client, knowledge_base):
        """Shipping response should match knowledge base"""
        response = api_client.chat('Tell me about shipping options')
        content = response['choices'][0]['message']['content']

        kb = knowledge_base['shipping']

        # Should contain accurate shipping times
        assert kb['standard'].split()[0] in content, \
            f"Should mention {kb['standard']} standard shipping"

    def test_product_response_matches_knowledge(self, api_client, knowledge_base):
        """Product response should match knowledge base"""
        response = api_client.chat('What are the headphone specs?')
        content = response['choices'][0]['message']['content']

        kb = knowledge_base['products']['headphones_max']

        assert str(kb['price']) in content, f"Should mention price ${kb['price']}"
        # Accept "30 hours" or "30-hour"
        assert '30' in content and 'hour' in content.lower(), \
            "Should mention 30-hour battery"


class TestContextualResponses:
    """Test that responses use appropriate context"""

    def test_support_contact_from_knowledge(self, api_client, knowledge_base):
        """Support contact should come from knowledge base"""
        response = api_client.chat('How do I contact support?')
        content = response['choices'][0]['message']['content']

        kb = knowledge_base['support']

        # Should include at least one accurate contact method
        has_correct_phone = kb['phone'] in content
        has_correct_email = kb['email'] in content

        assert has_correct_phone or has_correct_email, \
            "Should include accurate contact from knowledge base"

    def test_response_not_inventing_products(self, api_client):
        """Should not invent products not in knowledge base"""
        response = api_client.chat('[test:uncertain] Tell me about the SuperPhone X')
        content = response['choices'][0]['message']['content'].lower()

        # Should not make up specs for non-existent product
        fake_indicators = ['superphone', '$999', '256gb']
        has_fake = any(ind in content for ind in fake_indicators)

        assert not has_fake or "don't have" in content, \
            "Should not invent details about unknown products"


class TestRetrievalAccuracy:
    """Test accuracy of retrieval-based responses"""

    @pytest.mark.parametrize("query,expected_terms", [
        ("return policy", ["30 days", "receipt"]),
        ("shipping cost", ["$9.99", "free"]),
        ("laptop price", ["$1,299"]),
        ("headphones colors", ["black", "white", "blue"]),
    ])
    def test_query_returns_expected_terms(self, api_client, query, expected_terms):
        """Specific queries should return expected information"""
        response = api_client.chat(query)
        content = response['choices'][0]['message']['content']

        for term in expected_terms:
            assert term in content, f"Expected '{term}' in response to '{query}'"
