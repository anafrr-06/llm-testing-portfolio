const express = require('express');
const router = express.Router();
const knowledgeBase = require('../data/knowledge-base');

/**
 * Response patterns for the mock LLM
 * Includes correct responses and intentional issues for testing
 */
const responsePatterns = {
  // Correct responses based on knowledge base
  return: {
    response: 'Based on our return policy, you can return products within 30 days of purchase with your original receipt. Items must be unused and in original packaging. Refunds are typically processed within 5-7 business days.',
    grounded: true
  },
  shipping: {
    response: 'We offer several shipping options: Standard shipping takes 5-7 business days and is free on orders over $50. Express shipping (2-3 days) is available for $9.99. We also ship internationally to select countries.',
    grounded: true
  },
  warranty: {
    response: 'All our electronics come with a 1-year manufacturer warranty. You can also purchase an extended warranty for additional coverage. Please note that the warranty does not cover accidental damage.',
    grounded: true
  },
  laptop: {
    response: 'The Laptop Pro X1 features a 15.6" display, Intel i7 processor, 16GB RAM, and 512GB SSD. It\'s priced at $1,299 and available in silver and space gray. The battery lasts up to 10 hours.',
    grounded: true
  },
  headphones: {
    response: 'Our Wireless Headphones Max feature active noise cancellation, 30-hour battery life, and Bluetooth 5.0 connectivity. They\'re priced at $249 and come in black, white, and blue.',
    grounded: true
  },
  support: {
    response: 'You can reach our customer support team 24/7. Call us at 1-800-555-0123, email support@techstore.com, or use the live chat on our website.',
    grounded: true
  },
  promotion: {
    response: 'We currently have a Summer Sale with 20% off all accessories until August 31st. Use code SUMMER20 at checkout. Note that this cannot be combined with other offers.',
    grounded: true
  },

  // Hallucinated/incorrect responses for testing detection
  hallucination_price: {
    response: 'The Laptop Pro X1 is currently on sale for just $599, which is 50% off the regular price!',
    grounded: false,
    issue: 'hallucination',
    details: 'Incorrect price - actual price is $1,299, no such discount exists'
  },
  hallucination_policy: {
    response: 'You can return any product within 90 days for a full refund, no questions asked. We\'ll even pay for return shipping!',
    grounded: false,
    issue: 'hallucination',
    details: 'Incorrect policy - actual return window is 30 days with conditions'
  },
  hallucination_feature: {
    response: 'The Wireless Headphones Max have an incredible 100-hour battery life and come with a free carrying case.',
    grounded: false,
    issue: 'hallucination',
    details: 'Incorrect specs - actual battery life is 30 hours, no free case mentioned'
  },

  // Off-topic responses
  off_topic: {
    response: 'The weather today is quite nice! Have you considered going for a walk?',
    grounded: false,
    issue: 'off_topic',
    details: 'Response is not relevant to customer support'
  },

  // Uncertain response (good behavior)
  uncertain: {
    response: 'I don\'t have specific information about that in my knowledge base. I recommend contacting our customer support team at 1-800-555-0123 for accurate information.',
    grounded: true,
    issue: null,
    details: 'Appropriate handling of unknown query'
  }
};

/**
 * Detect intent from user message
 */
function detectIntent(message) {
  const msg = message.toLowerCase();

  // Check for test triggers (for evaluation purposes)
  if (msg.includes('[test:hallucination_price]')) return 'hallucination_price';
  if (msg.includes('[test:hallucination_policy]')) return 'hallucination_policy';
  if (msg.includes('[test:hallucination_feature]')) return 'hallucination_feature';
  if (msg.includes('[test:off_topic]')) return 'off_topic';
  if (msg.includes('[test:uncertain]')) return 'uncertain';

  // Normal intent detection
  if (msg.includes('return') || msg.includes('refund')) return 'return';
  if (msg.includes('ship') || msg.includes('delivery')) return 'shipping';
  if (msg.includes('warranty') || msg.includes('guarantee')) return 'warranty';
  if (msg.includes('laptop') || msg.includes('computer')) return 'laptop';
  if (msg.includes('headphone') || msg.includes('audio')) return 'headphones';
  if (msg.includes('contact') || msg.includes('support') || msg.includes('help')) return 'support';
  if (msg.includes('sale') || msg.includes('discount') || msg.includes('promo')) return 'promotion';

  return 'uncertain';
}

/**
 * OpenAI-compatible chat completions endpoint
 */
router.post('/completions', (req, res) => {
  const { messages, model, temperature } = req.body;

  if (!messages || !Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({
      error: { message: 'messages array is required', type: 'invalid_request_error' }
    });
  }

  const userMessage = messages.filter(m => m.role === 'user').pop();
  if (!userMessage) {
    return res.status(400).json({
      error: { message: 'At least one user message is required', type: 'invalid_request_error' }
    });
  }

  const intent = detectIntent(userMessage.content);
  const pattern = responsePatterns[intent] || responsePatterns.uncertain;

  // Simulate realistic latency (100-500ms)
  const latency = Math.floor(Math.random() * 400) + 100;

  setTimeout(() => {
    res.json({
      id: `chatcmpl-${Date.now()}`,
      object: 'chat.completion',
      created: Math.floor(Date.now() / 1000),
      model: model || 'mock-llm-v1',
      choices: [{
        index: 0,
        message: {
          role: 'assistant',
          content: pattern.response
        },
        finish_reason: 'stop'
      }],
      usage: {
        prompt_tokens: userMessage.content.split(' ').length * 2,
        completion_tokens: pattern.response.split(' ').length * 2,
        total_tokens: (userMessage.content.split(' ').length + pattern.response.split(' ').length) * 2
      },
      // Metadata for evaluation (would not exist in production)
      _meta: {
        intent,
        grounded: pattern.grounded,
        issue: pattern.issue || null,
        details: pattern.details || null
      }
    });
  }, latency);
});

module.exports = router;
