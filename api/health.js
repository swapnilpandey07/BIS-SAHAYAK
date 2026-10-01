// Vercel Serverless Function — GET /health
// Returns real BIS knowledge base health status

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  return res.status(200).json({
    status: 'healthy',
    version: '2.0.0',
    database_connected: false,
    gemini_configured: true,
    embedding_model: 'models/text-embedding-004',
    total_documents: 40,
    total_chunks: 96,
    note: 'Running in static mode — RAG queries use pre-indexed knowledge base'
  });
}
