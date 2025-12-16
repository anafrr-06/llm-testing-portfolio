const express = require('express');
const chatRoutes = require('./routes/chat');
const knowledgeBase = require('./data/knowledge-base');

const app = express();
app.use(express.json());

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', model: 'mock-llm-v1' });
});

// Chat completions endpoint (OpenAI-compatible format)
app.use('/v1/chat', chatRoutes);

// Knowledge base endpoint (for RAG testing)
app.get('/v1/knowledge', (req, res) => {
  res.json({ documents: knowledgeBase.getAllDocuments() });
});

app.get('/v1/knowledge/search', (req, res) => {
  const { query } = req.query;
  const results = knowledgeBase.search(query || '');
  res.json({ results });
});

const PORT = process.env.PORT || 3100;
app.listen(PORT, () => {
  console.log(`Mock LLM API running on http://localhost:${PORT}`);
});

module.exports = app;
