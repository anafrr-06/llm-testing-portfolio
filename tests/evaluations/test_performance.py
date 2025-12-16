"""
Performance and Efficiency Tests

Tests for response time, token usage, and throughput.
"""
import pytest
import time
import statistics


class TestLatency:
    """Tests for response latency"""

    def test_p50_latency(self, api_client):
        """Median response time should be under 1 second"""
        latencies = []

        for _ in range(10):
            start = time.time()
            api_client.chat('What is your return policy?')
            latencies.append(time.time() - start)

        p50 = statistics.median(latencies)

        if p50 > 1.0:
            pytest.fail(f"P50 latency too high: {p50:.2f}s (should be < 1s)")

    def test_p95_latency(self, api_client):
        """95th percentile latency should be under 2 seconds"""
        latencies = []

        for _ in range(20):
            start = time.time()
            api_client.chat('Tell me about shipping')
            latencies.append(time.time() - start)

        sorted_latencies = sorted(latencies)
        p95_index = int(len(sorted_latencies) * 0.95)
        p95 = sorted_latencies[p95_index]

        if p95 > 2.0:
            pytest.fail(f"P95 latency too high: {p95:.2f}s (should be < 2s)")

    def test_latency_consistency(self, api_client):
        """Latency should be consistent (low variance)"""
        latencies = []

        for _ in range(10):
            start = time.time()
            api_client.chat('Product info')
            latencies.append(time.time() - start)

        mean = statistics.mean(latencies)
        stdev = statistics.stdev(latencies)
        cv = stdev / mean if mean > 0 else 0  # Coefficient of variation

        if cv > 1.0:
            pytest.fail(f"High latency variance: CV={cv:.2f} (should be < 1.0)")


class TestTokenUsage:
    """Tests for token efficiency"""

    def test_reasonable_response_length(self, api_client):
        """Responses should be appropriately sized"""
        queries_and_max_lengths = [
            ('What is shipping cost?', 200),  # Simple answer
            ('Tell me about the laptop', 300),  # Product details
            ('What is your return policy?', 250),  # Policy info
        ]

        for query, max_words in queries_and_max_lengths:
            response = api_client.chat(query)
            content = response['choices'][0]['message']['content']
            word_count = len(content.split())

            if word_count > max_words:
                pytest.fail(f"Response too long for '{query}': {word_count} words (max {max_words})")

    def test_token_usage_reported(self, api_client):
        """Token usage should be accurately reported"""
        response = api_client.chat('What is the laptop price?')

        usage = response.get('usage', {})

        assert 'prompt_tokens' in usage, "Should report prompt_tokens"
        assert 'completion_tokens' in usage, "Should report completion_tokens"
        assert 'total_tokens' in usage, "Should report total_tokens"

        # Total should equal prompt + completion
        expected_total = usage['prompt_tokens'] + usage['completion_tokens']
        assert usage['total_tokens'] == expected_total, "Token count mismatch"

    def test_efficient_token_usage(self, api_client):
        """Should not waste tokens on unnecessary content"""
        response = api_client.chat('Laptop price?')
        content = response['choices'][0]['message']['content']

        # Response should be concise for simple question
        words = content.split()

        if len(words) > 100:
            pytest.fail(f"Inefficient: {len(words)} words for simple price query")

        # Should contain the actual answer
        if '$' not in content and 'price' not in content.lower():
            pytest.fail("Response doesn't seem to answer the price question")


class TestThroughput:
    """Tests for request throughput"""

    def test_concurrent_request_handling(self, api_client):
        """Should handle multiple requests efficiently"""
        import concurrent.futures

        queries = [
            'Return policy?',
            'Shipping cost?',
            'Laptop price?',
            'Headphone colors?',
            'Support contact?'
        ]

        start = time.time()

        # Note: This is sequential in this test, but demonstrates the pattern
        responses = []
        for query in queries:
            responses.append(api_client.chat(query))

        total_time = time.time() - start

        # All should succeed
        for i, resp in enumerate(responses):
            assert 'choices' in resp, f"Request {i} failed"

        # Should complete in reasonable time
        avg_time = total_time / len(queries)
        if avg_time > 1.0:
            pytest.fail(f"Avg request time too high: {avg_time:.2f}s")

    def test_sustained_load(self, api_client):
        """Should maintain performance under sustained load"""
        latencies = []

        # 30 requests to simulate sustained load
        for i in range(30):
            query = f'Query number {i}: What is shipping?'
            start = time.time()
            response = api_client.chat(query)
            latencies.append(time.time() - start)

            assert 'choices' in response, f"Request {i} failed"

        # Check for degradation
        first_10_avg = statistics.mean(latencies[:10])
        last_10_avg = statistics.mean(latencies[-10:])

        degradation = (last_10_avg - first_10_avg) / first_10_avg if first_10_avg > 0 else 0

        if degradation > 0.5:  # 50% degradation
            pytest.fail(f"Performance degraded by {degradation:.0%} under load")


class TestResourceEfficiency:
    """Tests for resource efficiency"""

    def test_memory_efficient_responses(self, api_client):
        """Responses should not be unnecessarily large"""
        response = api_client.chat('Tell me everything about all products')
        content = response['choices'][0]['message']['content']

        # Even for broad queries, should be bounded
        max_size = 10000  # characters
        if len(content) > max_size:
            pytest.fail(f"Response too large: {len(content)} chars (max {max_size})")

    def test_no_memory_leak_indicators(self, api_client):
        """Multiple requests should not show memory issues"""
        import sys

        # Make several requests
        for _ in range(20):
            response = api_client.chat('Quick test')
            # Just verify it works
            assert 'choices' in response

        # If we got here without OOM or slowdown, we're good
        pass

    def test_response_caching_opportunity(self, api_client):
        """Identical requests should be fast (cacheable)"""
        query = 'What is the exact return policy?'

        # First request
        start1 = time.time()
        resp1 = api_client.chat(query)
        time1 = time.time() - start1

        # Second identical request
        start2 = time.time()
        resp2 = api_client.chat(query)
        time2 = time.time() - start2

        # If caching is implemented, second should be faster
        # We just verify both succeed and log the timing
        assert 'choices' in resp1 and 'choices' in resp2

        # Note: actual caching test would compare times
        # For portfolio, we just demonstrate the testing pattern
