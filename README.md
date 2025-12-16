# LLM Testing Portfolio

Testing framework for AI/LLM applications demonstrating prompt evaluation, hallucination detection, and response quality assurance.

## Test Coverage

| Category | Description |
|----------|-------------|
| **Hallucination Detection** | Verify LLM doesn't generate false information |
| **Response Relevance** | Ensure responses are on-topic and helpful |
| **RAG Evaluation** | Test retrieval-augmented generation accuracy |
| **Grounding Verification** | Validate responses match knowledge base |
| **Latency Testing** | Monitor response time performance |

## Architecture

```
├── api/                    # Mock LLM API (OpenAI-compatible)
│   └── src/
│       ├── routes/chat.js  # Chat completions endpoint
│       └── data/           # Simulated knowledge base
├── tests/
│   ├── promptfoo/          # Promptfoo evaluation configs
│   └── evaluations/        # Python test suite
└── reports/                # Test results
```

## Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Start mock API
npm start

# Run all tests
npm run test:prompts    # Promptfoo evaluations
npm run test:eval       # Python tests
```

## Mock LLM API

The mock API simulates an e-commerce customer support AI with:
- Correct responses grounded in knowledge base
- Intentional hallucinations for testing detection
- Off-topic responses for relevance testing
- Configurable latency

### Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /v1/chat/completions` | OpenAI-compatible chat |
| `GET /v1/knowledge/search` | Knowledge base search |
| `GET /health` | Health check |

## Test Types

### 1. Promptfoo Evaluations

Declarative tests in `promptfooconfig.yaml`:

```yaml
tests:
  - vars:
      query: 'What is your return policy?'
    assert:
      - type: contains
        value: '30 days'
      - type: not-contains
        value: '90 days'  # Detect hallucination
```

### 2. Python Evaluation Tests

Programmatic tests with pytest:

```python
def test_laptop_price_correct(api_client, knowledge_base):
    response = api_client.chat('What is the laptop price?')
    content = response['choices'][0]['message']['content']

    correct_price = knowledge_base['products']['laptop']['price']
    assert f'${correct_price}' in content
```

## Evaluation Metrics

- **Hallucination Rate**: % of responses with false information
- **Relevance Score**: % of on-topic responses
- **Grounding Accuracy**: % matching knowledge base
- **Response Latency**: p95 response time

## CI/CD

GitHub Actions runs on every push:
1. Start mock LLM API
2. Run Promptfoo evaluations
3. Run Python test suite
4. Upload results as artifacts

## Adapting for Production

Replace mock provider in `promptfooconfig.yaml`:

```yaml
providers:
  # OpenAI
  - openai:gpt-4

  # Local with Ollama
  - ollama:llama2

  # Anthropic
  - anthropic:claude-3-sonnet
```
