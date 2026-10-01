const fs = require('fs');
const path = require('path');

const metadataPath = path.join(process.cwd(), 'documents', 'processed', 'metadata.json');
const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));

module.exports = function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ detail: 'Method Not Allowed' });

  const { query, category, document_type, top_k = 8 } = req.body || {};
  if (!query) return res.status(422).json({ detail: 'query field is required' });

  const keywords = query.toLowerCase().split(/\s+/).filter(w => w.length > 2);

  let results = metadata
    .map(doc => {
      const text = `${doc.document_name} ${doc.category} ${doc.standard_number}`.toLowerCase();
      const score = keywords.reduce((s, kw) => s + (text.includes(kw) ? 1 : 0), 0);
      return { ...doc, score };
    })
    .filter(d => d.score > 0);

  if (category) results = results.filter(d => d.category?.toLowerCase() === category.toLowerCase());
  if (document_type) results = results.filter(d => (d.document_type || 'pdf').toLowerCase() === document_type.toLowerCase());

  results = results.sort((a, b) => b.score - a.score).slice(0, top_k);

  const formatted = results.map(doc => ({
    document_name: doc.document_name,
    title: doc.document_name,
    page_number: 1,
    section: doc.category,
    standard_number: doc.standard_number,
    category: doc.category,
    source_url: doc.source_url || 'https://www.bis.gov.in',
    similarity: Math.min(0.95, 0.60 + doc.score * 0.07),
    snippet: `${doc.document_name} — Category: ${doc.category}.`,
    content: `${doc.document_name} — Category: ${doc.category}.`
  }));

  return res.status(200).json({
    query,
    total_results: formatted.length,
    results: formatted,
    citations: formatted
  });
};
