const fs = require('fs');
const path = require('path');

const metadataPath = path.join(process.cwd(), 'documents', 'processed', 'metadata.json');
const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));

module.exports = function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  return res.status(200).json({
    status: 'healthy',
    version: '2.0.0',
    database_connected: false,
    gemini_configured: true,
    embedding_model: 'models/text-embedding-004',
    total_documents: metadata.length,
    total_chunks: metadata.reduce((s, d) => s + (d.chunks_count || 0), 0),
    note: 'Running in static mode on Vercel'
  });
};
