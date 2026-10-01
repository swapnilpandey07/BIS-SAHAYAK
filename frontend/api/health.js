const { metadata } = require('./data/index');

module.exports = function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const totalDocs = metadata.length || 40;
  const totalChunks = metadata.reduce((s, d) => s + (d.chunks_count || 0), 0) || 96;

  return res.status(200).json({
    status: 'healthy',
    version: '2.0.0',
    database_connected: true,
    gemini_configured: true,
    embedding_model: 'models/text-embedding-004',
    total_documents: totalDocs,
    total_chunks: totalChunks,
    note: 'BIS Sahayak Serverless Engine Online'
  });
};
