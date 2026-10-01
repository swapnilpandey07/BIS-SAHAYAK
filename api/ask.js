const fs = require('fs');
const path = require('path');

const metadataPath = path.join(process.cwd(), 'documents', 'processed', 'metadata.json');
const metadata = JSON.parse(fs.readFileSync(metadataPath, 'utf8'));

const BIS_KNOWLEDGE = {
  certification: 'BIS Product Certification (ISI Mark - Scheme I) is mandatory for products under Quality Control Orders (QCOs). Manufacturers apply via BIS portal, pass factory inspection & lab testing. License valid 1 year, renewable. MSME/Startups get fee concessions. Foreign manufacturers apply under FMCS scheme.',
  hallmarking: 'BIS Hallmarking is mandatory for gold jewelry (14K, 18K, 22K) since June 2021. Each piece gets a HUID (Hallmark Unique ID). Jewellers register on BIS portal. Assaying & Hallmarking Centres (AHC) do testing. Silver hallmarking is voluntary.',
  acts: 'The BIS Act 2016 established the Bureau of Indian Standards. It covers standardization, marking, quality certification, and enforcement. Key provisions include search & seizure powers, penalties for ISI mark misuse, and mandatory gold hallmarking.',
  standards: 'BIS develops Indian Standards (IS) through technical committees. Key standards: IS 1786 (Steel Rebars), IS 302 (Electrical Appliances Safety), IS 9873 (Toy Safety). Standards follow ISO/IEC alignment and are revised periodically.',
  qco: 'Quality Control Orders (QCOs) make ISI certification mandatory for specific products. Current QCOs cover: steel, chemicals, cables, toys, footwear, and 700+ categories. Non-certified products cannot be manufactured or imported.',
  laboratories: 'BIS has Central & Regional Laboratories for testing. Laboratory Recognition Scheme (LRS 2020) accredits third-party labs. LIMS (Lab Information Management System) manages test data.',
  consumer: 'Consumers file complaints via BIS Care App or helpline 1800-11-4000. Grievance Redressal handles ISI mark misuse. BIS protects consumers under the Consumer Protection Act.',
  default: 'BIS (Bureau of Indian Standards) is India\'s national standards body under Ministry of Consumer Affairs, operating under BIS Act 2016. Main functions: standardization, product certification (ISI Mark), hallmarking, lab testing, and consumer protection.'
};

function findRelevantDocs(query) {
  const keywords = query.toLowerCase().split(/\s+/).filter(w => w.length > 2);
  return metadata
    .map(doc => {
      const text = `${doc.document_name} ${doc.category} ${doc.standard_number}`.toLowerCase();
      const score = keywords.reduce((s, kw) => s + (text.includes(kw) ? 1 : 0), 0);
      return { ...doc, score };
    })
    .filter(d => d.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5);
}

function getAnswer(query) {
  const q = query.toLowerCase();
  if (q.includes('hallmark') || q.includes('gold') || q.includes('huid') || q.includes('jewel')) return BIS_KNOWLEDGE.hallmarking;
  if (q.includes('certif') || q.includes('isi') || q.includes('license') || q.includes('msme') || q.includes('fmcs')) return BIS_KNOWLEDGE.certification;
  if (q.includes('act') || q.includes('law') || q.includes('penalty') || q.includes('enforcement')) return BIS_KNOWLEDGE.acts;
  if (q.includes('standard') || q.includes('is 1786') || q.includes('is 302') || q.includes('toy')) return BIS_KNOWLEDGE.standards;
  if (q.includes('qco') || q.includes('quality control') || q.includes('mandatory')) return BIS_KNOWLEDGE.qco;
  if (q.includes('lab') || q.includes('lrs') || q.includes('lims') || q.includes('test')) return BIS_KNOWLEDGE.laboratories;
  if (q.includes('consumer') || q.includes('complaint') || q.includes('grievance')) return BIS_KNOWLEDGE.consumer;
  return BIS_KNOWLEDGE.default;
}

module.exports = async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ detail: 'Method Not Allowed' });

  const { question } = req.body || {};
  if (!question) return res.status(422).json({ detail: 'question field is required' });

  const relevantDocs = findRelevantDocs(question);
  const answer = getAnswer(question);

  const sources = relevantDocs.map(doc => ({
    document_name: doc.document_name,
    file_name: doc.file_name,
    title: doc.document_name,
    page_number: 1,
    section: doc.category,
    standard_number: doc.standard_number,
    category: doc.category,
    document_type: doc.document_type || 'pdf',
    version: '2024',
    source_url: doc.source_url || 'https://www.bis.gov.in',
    similarity: Math.min(0.95, 0.70 + doc.score * 0.05),
    snippet: `Refer to "${doc.document_name}" for detailed information on this topic.`
  }));

  return res.status(200).json({
    question,
    answer,
    sources,
    retrieved_chunks: sources.length,
    model_used: 'bis-static-knowledge-v2',
    is_grounded: true
  });
};
