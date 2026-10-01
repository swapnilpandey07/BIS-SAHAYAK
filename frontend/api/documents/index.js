const { metadata } = require('../data/index');

module.exports = function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();

  const { category, document_type } = req.query || {};

  let filtered = metadata;
  if (category) filtered = filtered.filter(d => d.category?.toLowerCase() === category.toLowerCase());
  if (document_type) filtered = filtered.filter(d => (d.document_type || 'pdf').toLowerCase() === document_type.toLowerCase());

  return res.status(200).json({
    count: filtered.length,
    total: metadata.length,
    documents: filtered
  });
};
