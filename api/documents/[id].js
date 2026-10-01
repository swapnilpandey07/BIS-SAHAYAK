// Vercel Serverless Function — GET /api/documents/[id]
// Returns details for a specific BIS document by document_id or document_name

import metadata from '../../../documents/processed/metadata.json' assert { type: 'json' };

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const { id } = req.query;
  const decodedId = decodeURIComponent(id);

  const doc = metadata.find(
    d => d.document_id === decodedId || d.document_name === decodedId
  );

  if (!doc) {
    return res.status(404).json({ detail: 'Document not found in registry' });
  }

  return res.status(200).json({
    document: doc,
    total_chunks: doc.chunks_count || 0,
    chunks: []
  });
}
