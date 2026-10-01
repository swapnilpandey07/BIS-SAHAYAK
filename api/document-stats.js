// Vercel Serverless Function — GET /api/document-stats
// Returns live stats computed from the indexed BIS document metadata

import metadata from '../documents/processed/metadata.json' assert { type: 'json' };

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();

  const categories = {};
  const document_types = {};

  for (const doc of metadata) {
    const cat = doc.category || 'general';
    categories[cat] = (categories[cat] || 0) + 1;
    const dtype = doc.document_type || 'pdf';
    document_types[dtype] = (document_types[dtype] || 0) + 1;
  }

  const totalChunks = metadata.reduce((sum, d) => sum + (d.chunks_count || 0), 0);

  return res.status(200).json({
    total_documents: metadata.length,
    total_chunks: totalChunks,
    categories,
    document_types,
    latest_ingestion_date: '2026-01-10T00:00:00',
    failed_documents: [],
    duplicate_documents_skipped: 0
  });
}
