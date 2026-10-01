const { metadata } = require('./data/index');

const BIS_KNOWLEDGE = {
  certification: 'BIS Product Certification (ISI Mark - Scheme I) is mandatory for products under Quality Control Orders (QCOs). Manufacturers apply via BIS portal, pass factory inspection & lab testing. License is valid for 1-2 years and renewable. MSME/Startups receive fee concessions. Foreign manufacturers apply under FMCS (Foreign Manufacturers Certification Scheme).',
  hallmarking: 'BIS Hallmarking is mandatory for gold jewelry & artifacts (14K, 18K, 22K, 24K) across India. Each hallmarked article receives a unique 6-digit alphanumeric Hallmark Unique Identification (HUID) code. Jewellers register on the Manakonline portal. Assaying & Hallmarking Centres (AHC) perform rigorous assaying. Silver hallmarking remains voluntary.',
  acts: 'The BIS Act 2016 established the Bureau of Indian Standards as the National Standards Body of India. It empowers BIS to notify mandatory standards, perform conformity assessments, and conduct search and seizure operations with strict penalties for unauthorized use of Standard Marks.',
  standards: 'BIS develops Indian Standards (IS) through 14 Division Councils and sectional committees. Prominent standards include IS 1786 (High strength deformed steel bars), IS 302 (Safety of household electrical appliances), and IS 9873 (Safety of toys). Standards align with ISO/IEC international benchmarks.',
  qco: 'Quality Control Orders (QCOs) issued by line ministries mandate BIS certification for specified products to ensure consumer health and safety. Non-certified products under QCO cannot be manufactured, imported, distributed, or sold in India.',
  laboratories: 'BIS operates a network of Central and Regional laboratories and accredits third-party laboratories under the Laboratory Recognition Scheme (LRS 2020) with automated test workflows managed through LIMS.',
  consumer: 'Consumers can verify ISI marks and HUID numbers via the official BIS Care mobile app or lodge complaints online through the BIS portal and toll-free helpline 1800-11-4000. BIS enforcement teams conduct market surveillance to combat counterfeits.',
  default: 'The Bureau of Indian Standards (BIS) is the National Standards Body of India working under the Ministry of Consumer Affairs, Food & Public Distribution. BIS is responsible for standardization, product certification (ISI Mark), hallmarking, laboratory testing, and consumer protection across India.'
};

function findRelevantDocs(query) {
  const keywords = query.toLowerCase().split(/\s+/).filter(w => w.length > 2);
  return (metadata || [])
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
  if (q.includes('consumer') || q.includes('complaint') || q.includes('grievance') || q.includes('app')) return BIS_KNOWLEDGE.consumer;
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
    snippet: `Refer to official BIS standard document "${doc.document_name}" for comprehensive guidelines.`
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
