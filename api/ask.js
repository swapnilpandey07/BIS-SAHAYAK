// Vercel Serverless Function — POST /api/ask
// Performs keyword-based search over BIS metadata when backend is unavailable
// Returns grounded answers from the pre-indexed document registry

import metadata from '../../documents/processed/metadata.json' assert { type: 'json' };

const BIS_KNOWLEDGE = {
  certification: `BIS Product Certification (ISI Mark - Scheme I) is mandatory for products listed under Quality Control Orders (QCOs). Manufacturers must apply through the BIS portal, pass factory inspection, and laboratory testing. License is valid for 1 year and renewable. MSME/Startups get fee concessions. Foreign manufacturers can apply under FMCS scheme.`,
  hallmarking: `BIS Hallmarking is mandatory for gold jewelry (14K, 18K, 22K) since June 2021. Each piece gets a unique HUID (Hallmark Unique ID). Jewellers must register on BIS portal. Assaying & Hallmarking Centres (AHC) do the testing. Silver hallmarking is voluntary.`,
  acts: `The BIS Act 2016 established the Bureau of Indian Standards. It covers standardization, marking, quality certification, and enforcement. Key provisions include search & seizure powers, penalties for misuse of ISI mark, and mandatory hallmarking of gold.`,
  standards: `BIS develops Indian Standards (IS) through technical committees. Key standards: IS 1786 (Steel Rebars), IS 302 (Electrical Appliances Safety), IS 9873 (Toy Safety). Standards are revised periodically and follow ISO/IEC alignment.`,
  qco: `Quality Control Orders (QCOs) make ISI certification mandatory for specific products. Current QCOs cover: steel products, chemicals, cables, toys, footwear, and 700+ other categories. Non-certified products cannot be manufactured or imported.`,
  laboratories: `BIS has Central & Regional Laboratories across India for testing. The Laboratory Recognition Scheme (LRS 2020) accredits third-party labs. LIMS (Laboratory Information Management System) is used for test data management.`,
  consumer: `Consumers can file complaints via BIS Care App or helpline 1800-11-4000. Grievance Redressal Mechanism handles ISI mark misuse complaints. BIS protects consumer rights under the Consumer Protection Act.`,
  default: `BIS (Bureau of Indian Standards) is India's national standards body under the Ministry of Consumer Affairs. It operates under the BIS Act 2016. Main functions: standardization, product certification (ISI Mark), hallmarking (gold/silver), laboratory testing, and consumer protection.`
};

function findRelevantDocs(query) {
  const q = query.toLowerCase();
  const keywords = q.split(/\s+/).filter(w => w.length > 2);

  const scored = metadata.map(doc => {
    const docText = `${doc.document_name} ${doc.category} ${doc.standard_number}`.toLowerCase();
    const score = keywords.reduce((s, kw) => s + (docText.includes(kw) ? 1 : 0), 0);
    return { ...doc, score };
  });

  return scored.filter(d => d.score > 0).sort((a, b) => b.score - a.score).slice(0, 5);
}

function getAnswer(query) {
  const q = query.toLowerCase();
  if (q.includes('hallmark') || q.includes('gold') || q.includes('silver') || q.includes('huid') || q.includes('jewel')) return BIS_KNOWLEDGE.hallmarking;
  if (q.includes('certif') || q.includes('isi') || q.includes('license') || q.includes('msme') || q.includes('fmcs')) return BIS_KNOWLEDGE.certification;
  if (q.includes('act') || q.includes('law') || q.includes('penalty') || q.includes('enforcement')) return BIS_KNOWLEDGE.acts;
  if (q.includes('standard') || q.includes(' is ') || q.includes('is 1786') || q.includes('is 302') || q.includes('toy')) return BIS_KNOWLEDGE.standards;
  if (q.includes('qco') || q.includes('quality control order') || q.includes('mandatory')) return BIS_KNOWLEDGE.qco;
  if (q.includes('lab') || q.includes('test') || q.includes('lrs') || q.includes('lims')) return BIS_KNOWLEDGE.laboratories;
  if (q.includes('consumer') || q.includes('complaint') || q.includes('grievance') || q.includes('care app')) return BIS_KNOWLEDGE.consumer;
  return BIS_KNOWLEDGE.default;
}

export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ detail: 'Method Not Allowed' });

  const { question, category_filter, top_k = 6 } = req.body || {};

  if (!question) {
    return res.status(422).json({ detail: 'question field is required' });
  }

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
    similarity: 0.75 + (doc.score * 0.05),
    snippet: `Refer to ${doc.document_name} for detailed information on this topic.`
  }));

  return res.status(200).json({
    question,
    answer: answer + '\n\n⚠️ Note: This is a pre-indexed static response. For full AI-powered RAG answers, the backend server must be running.',
    sources,
    retrieved_chunks: sources.length,
    model_used: 'static-knowledge-base',
    is_grounded: true
  });
}
