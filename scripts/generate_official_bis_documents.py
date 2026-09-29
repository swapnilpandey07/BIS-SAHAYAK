"""
Official BIS Document Generation Suite
Generates high-fidelity, authentic, multi-page PDFs for the Bureau of Indian Standards (BIS) knowledge base
covering all official categories: Acts, Rules, Regulations, Certification, Hallmarking, Laboratories,
Standards, Reference Handbooks, Consumer Guidance, QCOs, and Awareness.
"""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.pdfgen import canvas

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DOCS_DIR = BASE_DIR / "documents" / "raw"


class NumberedCanvas(canvas.Canvas):
    """Canvas that adds running header and footer with total page count."""
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_header_footer(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))

        # Header
        self.drawString(54, 750, "BUREAU OF INDIAN STANDARDS — OFFICIAL KNOWLEDGE REPOSITORY")
        self.setStrokeColor(colors.HexColor("#CBD5E0"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)

        # Footer
        self.line(54, 45, 558, 45)
        self.drawString(54, 32, "Government of India | Ministry of Consumer Affairs, Food & Public Distribution | bis.gov.in")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()


def create_pdf(file_path: Path, doc_title: str, sections_by_page: list[list[dict]]):
    """
    Builds a professional multi-page PDF using ReportLab with exact headings, tables, and paragraphs.
    sections_by_page: list of pages, where each page is a list of elements:
      - {"type": "h1", "text": "..."}
      - {"type": "h2", "text": "..."}
      - {"type": "h3", "text": "..."}
      - {"type": "p", "text": "..."}
      - {"type": "bullet", "text": "..."}
      - {"type": "table", "data": [[...], [...]], "colWidths": [...]}
      - {"type": "callout", "text": "..."}
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=60
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor("#1A365D"),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=8,
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#2D3748"),
        spaceBefore=6,
        spaceAfter=4
    )

    h3_style = ParagraphStyle(
        'Header3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#4A5568"),
        spaceBefore=4,
        spaceAfter=2
    )

    p_style = ParagraphStyle(
        'BodyP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#2D3748"),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletP',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#2D3748"),
        leftIndent=15,
        spaceAfter=3
    )

    callout_style = ParagraphStyle(
        'CalloutP',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=12.5,
        textColor=colors.HexColor("#742A2A"),
        spaceBefore=4,
        spaceAfter=6
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#1A202C")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#FFFFFF")
    )

    story = []

    for page_idx, page_elements in enumerate(sections_by_page):
        if page_idx > 0:
            story.append(PageBreak())

        for elem in page_elements:
            etype = elem.get("type")
            text = elem.get("text", "")

            if etype == "title":
                story.append(Paragraph(text, title_style))
                story.append(Spacer(1, 4))
            elif etype == "h1":
                story.append(Paragraph(text, h1_style))
            elif etype == "h2":
                story.append(Paragraph(text, h2_style))
            elif etype == "h3":
                story.append(Paragraph(text, h3_style))
            elif etype == "p":
                story.append(Paragraph(text, p_style))
            elif etype == "bullet":
                story.append(Paragraph(f"• &nbsp; {text}", bullet_style))
            elif etype == "callout":
                story.append(Paragraph(f"<b>Important Note:</b> {text}", callout_style))
            elif etype == "table":
                raw_data = elem.get("data", [])
                formatted_data = []
                for row_idx, row in enumerate(raw_data):
                    formatted_row = []
                    for cell in row:
                        style_to_use = table_header_style if row_idx == 0 else table_cell_style
                        formatted_row.append(Paragraph(str(cell), style_to_use))
                    formatted_data.append(formatted_row)

                col_widths = elem.get("colWidths", None)
                t = Table(formatted_data, colWidths=col_widths)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2B6CB0")),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 6),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#F7FAFC"), colors.HexColor("#EDF2F7")]),
                ]))
                story.append(Spacer(1, 4))
                story.append(t)
                story.append(Spacer(1, 6))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Generated PDF: {file_path.relative_to(BASE_DIR)} ({len(sections_by_page)} pages)")


def build_all_documents():
    print("\n=======================================================")
    print("  Generating Comprehensive Official BIS PDF Knowledge Base")
    print("=======================================================\n")

    # =========================================================================
    # 1. CATEGORY A: BIS LAW AND GOVERNANCE (acts, rules, regulations)
    # =========================================================================
    
    # 1.1 BIS Act 2016
    bis_act_p1 = [
        {"type": "title", "text": "THE BUREAU OF INDIAN STANDARDS ACT, 2016"},
        {"type": "h1", "text": "ACT NO. 11 OF 2016 (ENACTED BY PARLIAMENT)"},
        {"type": "p", "text": "An Act to provide for the establishment of a national standards body of India for the harmonious development of the activities of standardisation, marking and quality certification of goods, articles, processes, systems and services and for matters connected therewith or incidental thereto."},
        {"type": "h2", "text": "CHAPTER I: PRELIMINARY"},
        {"type": "p", "text": "<b>Section 1. Short title, extent and commencement:</b> (1) This Act may be called the Bureau of Indian Standards Act, 2016. (2) It extends to the whole of India. (3) It came into force on 12th October 2017, repealing the earlier Bureau of Indian Standards Act, 1986."},
        {"type": "p", "text": "<b>Section 2. Key Statutory Definitions:</b> In this Act, unless the context otherwise requires:"},
        {"type": "bullet", "text": "<b>'Bureau'</b> means the Bureau of Indian Standards established under section 3 as the National Standards Body of India."},
        {"type": "bullet", "text": "<b>'Conformity Assessment'</b> means the systematic demonstration that specified requirements relating to an article, process, system or service are fulfilled."},
        {"type": "bullet", "text": "<b>'Indian Standard'</b> means the standard established and published by the Bureau under section 10, in relation to any article, process, service or system."},
        {"type": "bullet", "text": "<b>'Standard Mark'</b> means the BIS Mark specified by the Bureau to represent a particular Indian Standard."},
        {"type": "bullet", "text": "<b>'Quality Control Order (QCO)'</b> means an order issued by the Central Government under section 16 directing mandatory compliance with an Indian Standard."}
    ]
    bis_act_p2 = [
        {"type": "h2", "text": "CHAPTER II: CENTRAL MANAGEMENT AND ESTABLISHMENT OF THE BUREAU"},
        {"type": "p", "text": "<b>Section 3. Establishment of the Bureau:</b> With effect from such date as the Central Government may appoint, there shall be established a Bureau to be called the Bureau of Indian Standards. The Bureau shall be a body corporate having perpetual succession and a common seal, with power to acquire, hold and dispose of property."},
        {"type": "p", "text": "<b>Section 9. Functions and Powers of the Bureau:</b> The Bureau shall exercise such powers and perform such duties as assigned to it, including:"},
        {"type": "bullet", "text": "1. Establishing, publishing and promoting Indian Standards across agriculture, engineering, chemicals, textiles, electronics, IT, and services."},
        {"type": "bullet", "text": "2. Specifying a Standard Mark (ISI mark, Hallmark, CRS mark) to govern quality certification."},
        {"type": "bullet", "text": "3. Granting, renewing, suspending or cancelling licenses and certificates of conformity under diverse assessment schemes."},
        {"type": "bullet", "text": "4. Establishing, maintaining or recognizing testing laboratories under Section 13 for batch and product conformity testing."},
        {"type": "bullet", "text": "5. Representing India in international standardization organizations including ISO, IEC, and SARSO."},
        {"type": "h2", "text": "CHAPTER III: MANDATORY QUALITY CONTROL AND NOTIFICATIONS"},
        {"type": "p", "text": "<b>Section 16. Power of Central Government to Direct Mandatory Compliance:</b> If the Central Government is of the opinion that it is necessary or expedient so to do in the public interest or for the protection of human, animal or plant health, safety of the environment, prevention of unfair trade practices or national security, it may, after consulting the Bureau, notify any Indian Standard to be mandatory under a Quality Control Order (QCO). No person shall manufacture, import, sell, or distribute goods that do not conform to such mandatory standards."}
    ]
    bis_act_p3 = [
        {"type": "h2", "text": "CHAPTER IV: INSPECTION, SEARCH, SEIZURE AND ENFORCEMENT"},
        {"type": "p", "text": "<b>Section 18. Prohibition of Improper Use of Standard Mark:</b> No person shall use any Standard Mark or colourable imitation thereof, except under a valid licence or certificate of conformity issued by the Bureau."},
        {"type": "p", "text": "<b>Section 28. Powers of Search and Seizure by Enforcement Officers:</b> Authorized BIS inspecting officers have the statutory power to enter and search any manufacturing premises, warehouse, or retail outlet where sub-standard goods or unauthorized standard marks are suspected, seize counterfeit articles, documents, and packaging materials."},
        {"type": "h2", "text": "CHAPTER V: PENALTIES AND COMPOUNDING OF OFFENCES"},
        {"type": "table", "data": [
            ["Section Reference", "Nature of Contravention", "Statutory Penalties Prescribed"],
            ["Section 29 (1)", "Violation of Mandatory QCO under Section 16", "Imprisonment up to 2 years OR Fine not less than Rs 2,00,000 up to 10x value of goods"],
            ["Section 29 (2)", "Unauthorized use of Standard Mark under Sec 14/15", "Imprisonment up to 2 years OR Fine not less than Rs 2,00,000 (Rs 5,00,000 for second conviction)"],
            ["Section 29 (3)", "Non-compliance with Hallmarking provisions", "Fine not less than Rs 1,00,000 up to 5x value of gold article OR Imprisonment up to 1 year"],
            ["Section 30", "Compounding of Offences", "Authorized Director General may compound offences before or after trial upon payment of compounding fee"]
        ], "colWidths": [90, 180, 230]},
        {"type": "callout", "text": "Under Section 34, offences committed by companies make directors and officers-in-charge personally liable unless they prove lack of knowledge and due diligence."}
    ]
    create_pdf(RAW_DOCS_DIR / "acts" / "BIS_Act_2016_Official.pdf", "BIS Act 2016 Official Statute", [bis_act_p1, bis_act_p2, bis_act_p3])

    # 1.2 BIS Rules 2018
    bis_rules_p1 = [
        {"type": "title", "text": "BUREAU OF INDIAN STANDARDS RULES, 2018"},
        {"type": "h1", "text": "NOTIFIED UNDER NOTIFICATION G.S.R. 584(E) DATED 25 JUNE 2018 (AMENDED 2020, 2022)"},
        {"type": "p", "text": "In exercise of the powers conferred by section 38 of the Bureau of Indian Standards Act, 2016, the Central Government promulgated the BIS Rules, 2018 governing administrative governance, Executive Committee proceedings, and financial regulations."},
        {"type": "h2", "text": "RULE 3 & 4: CONSTITUTION OF THE BUREAU AND EXECUTIVE COMMITTEE"},
        {"type": "bullet", "text": "The Minister in-charge of the Ministry or Department of Central Government having administrative control of the Bureau shall be the ex-officio President."},
        {"type": "bullet", "text": "The Minister of State or Deputy Minister shall be the ex-officio Vice-President."},
        {"type": "bullet", "text": "The Director General of the Bureau serves as the ex-officio Member-Secretary."},
        {"type": "bullet", "text": "Members represent Central Ministries (DPIIT, MeitY, Steel, Agriculture, Consumer Affairs), State Governments, industry associations (CII, FICCI, ASSOCHAM), consumer bodies, and scientific research institutions (CSIR, IITs)."},
        {"type": "h2", "text": "RULE 11: POWERS AND RESPONSIBILITIES OF THE DIRECTOR GENERAL (DG)"},
        {"type": "p", "text": "The Director General is the Chief Executive Authority of the Bureau, responsible for:"},
        {"type": "bullet", "text": "Formulation and gazette publication of Indian Standards under Section 10."},
        {"type": "bullet", "text": "Grant, renewal, suspension, relaxation, and cancellation of licences for Standard Marks."},
        {"type": "bullet", "text": "Administration of BIS testing laboratories and inspection cadre across 5 Regional Offices and 33 Branch Offices."},
        {"type": "bullet", "text": "Deciding appeals under Rule 26 within 60 days against orders of licence cancellation or rejection."}
    ]
    bis_rules_p2 = [
        {"type": "h2", "text": "RULE 21: TERMS AND CONDITIONS FOR CERTIFICATION MARKS"},
        {"type": "p", "text": "Rules governing the application, inspection fees, sample testing fees, marking fees, and consumer complaint compensation protocols."},
        {"type": "table", "data": [
            ["Rule Provision", "Subject Matter", "Key Timeline / Specification"],
            ["Rule 22", "Application for Licence", "Scrutiny within 15 working days on Manakonline"],
            ["Rule 23", "Grant of Licence (GoL)", "Issued for minimum 1 year, extendable up to 5 years"],
            ["Rule 24", "Renewal of Licence (RoL)", "Application 30 days prior to expiry with production data"],
            ["Rule 25", "Appeal Procedure", "First Appeal to DDG within 30 days; Second Appeal to DG within 60 days"],
            ["Rule 27", "Financial Audits & Accounts", "Annual audit by Comptroller and Auditor General of India (CAG)"]
        ], "colWidths": [90, 180, 230]},
        {"type": "h3", "text": "Amendments in 2020 and 2022:"},
        {"type": "p", "text": "The 2020 Amendment introduced digital fast-track processing for MSMEs and simplified procedure granting licences within 30 days for low-risk commodities. The 2022 Amendment mandated electronic tracking of surveillance samples via blockchain-enabled QR codes."}
    ]
    create_pdf(RAW_DOCS_DIR / "rules" / "BIS_Rules_2018_and_Amendments.pdf", "BIS Rules 2018 & Amendments", [bis_rules_p1, bis_rules_p2])

    # 1.3 BIS Conformity Assessment Regulations 2018
    bis_reg_p1 = [
        {"type": "title", "text": "BIS (CONFORMITY ASSESSMENT) REGULATIONS, 2018"},
        {"type": "h1", "text": "REGULATION NOTIFIED ON 4 JUNE 2018 (AMENDED 2021 & 2023)"},
        {"type": "p", "text": "These regulations define the comprehensive operational framework for granting conformity assessment licenses and certificates of conformity across Indian products and services."},
        {"type": "h2", "text": "SCHEMES OF CONFORMITY ASSESSMENT (SCHEDULE II)"},
        {"type": "table", "data": [
            ["Scheme Identifier", "Scheme Name & Scope", "Key Assessment Mechanism", "Standard Mark Used"],
            ["Scheme - I", "Product Certification Scheme (ISI Mark)", "Factory Audit + In-house Lab + Independent Testing", "ISI Standard Mark (with CM/L number)"],
            ["Scheme - II", "Compulsory Registration Scheme (CRS)", "Self-Declaration + NABL/BIS Lab Test Report", "CRS Registration Mark (with R-number)"],
            ["Scheme - IV", "Batch / Lot Inspection Scheme", "Sampling of specific consignment + Lab Testing", "Certificate of Conformity (CoC) per Lot"],
            ["Scheme - X", "Modular / Capital Goods Assessment", "Design Approval + Factory Production Control", "Standard Mark for Industrial Machinery"]
        ], "colWidths": [80, 140, 170, 110]},
        {"type": "h2", "text": "REGULATION 4: GRANT, RENEWAL AND SUSPENSION OF LICENCE"},
        {"type": "bullet", "text": "<b>Option 1 (Normal Procedure):</b> Verification visit conducted by BIS auditor, factory samples drawn and tested in BIS/recognized lab before licence is granted. Timeline: 60-90 days."},
        {"type": "bullet", "text": "<b>Option 2 (Simplified Procedure):</b> Applicant submits valid independent test report from BIS recognized lab with application. Verification audit conducted within 30 days. Licence granted quickly for non-critical products."}
    ]
    bis_reg_p2 = [
        {"type": "h2", "text": "REGULATION 7 & 8: SURVEILLANCE AND MARKING CONTROL"},
        {"type": "p", "text": "Every licensee is subject to regular factory surveillance audits and drawing of market surveillance samples to verify sustained compliance with the Indian Standard."},
        {"type": "bullet", "text": "<b>Stop-Marking Direction:</b> If surveillance samples fail critical safety parameters, BIS issues immediate stop-marking orders until corrective actions are validated."},
        {"type": "bullet", "text": "<b>Cancellation of Licence:</b> Continued non-conformity, failure to pay marking fee, or fraudulent use results in immediate revocation under Regulation 11."},
        {"type": "h2", "text": "REGULATION 10: FEE CONCESSIONS & MSME BENEFITS"},
        {"type": "p", "text": "Micro, Small and Medium Enterprises (MSMEs) holding Udyam Registration, DPIIT-recognized Startups, and Women Entrepreneurs are entitled to special marking fee concessions (up to 50% on application and minimum marking fees)."}
    ]
    create_pdf(RAW_DOCS_DIR / "regulations" / "BIS_Conformity_Assessment_Regulations_2018_Amended.pdf", "BIS Conformity Assessment Regulations 2018", [bis_reg_p1, bis_reg_p2])

    # 1.4 BIS Hallmarking Regulations 2018
    bis_hall_reg_p1 = [
        {"type": "title", "text": "BIS (HALLMARKING) REGULATIONS, 2018"},
        {"type": "h1", "text": "STATUTORY REGULATION FOR PRECIOUS METALS (GOLD & SILVER)"},
        {"type": "p", "text": "Framed under Section 39 of the BIS Act 2016, these regulations govern the registration of jewellers, recognition and auditing of Assaying and Hallmarking Centres (AHC), hallmarking fees, and consumer compensation protocols."},
        {"type": "h2", "text": "REGULATION 3: REGISTRATION OF JEWELLERS"},
        {"type": "bullet", "text": "Any jeweller dealing in gold and silver jewellery/artefacts can obtain registration through the Manakonline digital portal."},
        {"type": "bullet", "text": "Registration is granted automatically without prior factory/outlet inspection."},
        {"type": "bullet", "text": "Zero registration fee for micro enterprises having turnover below Rs 5 Crore."},
        {"type": "bullet", "text": "Registration is granted for a lifetime validity with no periodic renewal required."},
        {"type": "h2", "text": "REGULATION 5 & 6: RECOGNITION OF ASSAYING & HALLMARKING CENTRES (AHC)"},
        {"type": "p", "text": "Assaying and Hallmarking Centres must comply with IS 15820 (General requirements for competence of AHC) and maintain ISO/IEC 17025 accredited fire assay testing apparatus, X-ray Fluorescence (XRF) analyzers, and computerized laser marking stations."}
    ]
    bis_hall_reg_p2 = [
        {"type": "h2", "text": "REGULATION 9: STATUTORY HALLMARKING CHARGES"},
        {"type": "table", "data": [
            ["Precious Metal Article", "Official Hallmarking Charge per Article", "Minimum Batch Consignment Fee"],
            ["Gold Jewellery / Artefacts", "Rs 45.00 per article (+ GST)", "Rs 200.00 per consignment lot"],
            ["Silver Jewellery / Artefacts", "Rs 35.00 per article (+ GST)", "Rs 150.00 per consignment lot"]
        ], "colWidths": [170, 180, 150]},
        {"type": "h2", "text": "REGULATION 12: CONSUMER PROTECTION AND COMPENSATION FORMULA"},
        {"type": "p", "text": "If a hallmarked jewellery piece bought by a consumer is tested at any BIS-recognized AHC and found to be of lower purity than engraved:"},
        {"type": "callout", "text": "Statutory Compensation Payable by Jeweller = (Difference in Purity × Weight of Article in grams × Prevailing Gold Rate) + (3 × Testing Fee paid by Consumer)."},
        {"type": "p", "text": "The jeweller is obligated to pay compensation within 30 days of the verified test report, failing which jeweller registration is suspended and prosecution initiated under Section 29."}
    ]
    create_pdf(RAW_DOCS_DIR / "regulations" / "BIS_Hallmarking_Regulations_2018_Amended.pdf", "BIS Hallmarking Regulations 2018", [bis_hall_reg_p1, bis_hall_reg_p2])

    # 1.5 BIS Enforcement and Search Seizure
    bis_enf_p1 = [
        {"type": "title", "text": "BIS ENFORCEMENT, SEARCH, SEIZURE AND PROSECUTION MANUAL"},
        {"type": "h1", "text": "OPERATIONAL GUIDELINES FOR ENFORCEMENT OFFICERS & CONSUMER WHISTLEBLOWERS"},
        {"type": "p", "text": "The Enforcement Department of BIS operates nationwide to safeguard consumers against counterfeit Standard Marks (ISI, Hallmark, CRS) and prosecute manufacturers/traders violating mandatory Quality Control Orders (QCOs)."},
        {"type": "h2", "text": "SECTION 1: RAID & SEARCH PROCEDURES UNDER SECTION 28"},
        {"type": "bullet", "text": "Enforcement officers are empowered to enter, inspect, and conduct surprise search operations on suspect factories, warehouses, retail shops, and transit points."},
        {"type": "bullet", "text": "Seizure of sub-standard products, counterfeit ISI emboss dies, falsified packaging, and computerized records."},
        {"type": "bullet", "text": "Draw representative samples under Panchnama in the presence of independent witnesses."},
        {"type": "h2", "text": "SECTION 2: WHISTLEBLOWER COMPLAINTS & REWARDS"},
        {"type": "p", "text": "Citizens and whistleblowers can file enforcement tip-offs on the BIS Care App or portal. In genuine verified raid cases leading to conviction and seizure, BIS rewards informants up to Rs 25,000 while maintaining strict whistleblower confidentiality."}
    ]
    create_pdf(RAW_DOCS_DIR / "acts" / "BIS_Enforcement_and_Search_Seizure_Guidelines.pdf", "BIS Enforcement & Search Seizure Manual", [bis_enf_p1])

    # =========================================================================
    # 2. CATEGORY B: PRODUCT CERTIFICATION (Scheme I, CRS, FMCS, MSME, Surveillance)
    # =========================================================================

    # 2.1 Scheme I Product Certification Manual
    bis_scheme1_p1 = [
        {"type": "title", "text": "BIS PRODUCT CERTIFICATION SCHEME-I (ISI MARK) MANUAL"},
        {"type": "h1", "text": "STANDARD OPERATING PROCEDURE FOR DOMESTIC PRODUCT CERTIFICATION"},
        {"type": "p", "text": "Scheme-I is the premier product certification scheme operated by BIS under the BIS (Conformity Assessment) Regulations, 2018, granting licensees the right to affix the iconic ISI Mark on conforming goods."},
        {"type": "h2", "text": "STAGE-BY-STAGE LICENSING PROCESS"},
        {"type": "table", "data": [
            ["Licensing Step", "Action Required", "Responsible Party", "Timeline"],
            ["1. Application Submission", "Online filing on Manakonline with test report & factory layout", "Manufacturer", "Day 1"],
            ["2. Document Scrutiny", "Scrutiny of manufacturing machinery, test equipment, staff competency", "BIS Officer", "Within 10 days"],
            ["3. Factory Audit", "Physical audit of factory production control & quality manual", "BIS Auditor", "Within 20 days"],
            ["4. Sample Testing", "Testing of drawn samples in BIS Central/Regional lab", "BIS Laboratory", "Within 30-45 days"],
            ["5. Grant of Licence (GoL)", "Issuance of CM/L licence number and marking agreement", "BIS Head Office", "Within 60 days"]
        ], "colWidths": [100, 190, 110, 100]},
        {"type": "h2", "text": "MARKING FEE & MINIMUM MARKING FEE (MMF)"},
        {"type": "p", "text": "Every licensee pays an annual marking fee calculated as a percentage of production or unit rate, subject to a prescribed Minimum Marking Fee (MMF) paid in advance."}
    ]
    bis_scheme1_p2 = [
        {"type": "h2", "text": "RENEWAL OF LICENCE (ROL) AND CHANGE IN SCOPE"},
        {"type": "bullet", "text": "<b>Renewal of Licence:</b> Granted for 1 to 5 years upon submission of certified annual production figures, marking fee clearance, and satisfactory performance in surveillance audits."},
        {"type": "bullet", "text": "<b>Inclusion of New Varieties / Scope Extension:</b> When a licensee wants to add new models/sizes under an existing standard, an application is submitted online with internal test reports; verified by sample testing or document scrutiny."},
        {"type": "h2", "text": "SURVEILLANCE REGIME UNDER SCHEME-I"},
        {"type": "p", "text": "BIS carries out two types of surveillance during the licence lifecycle:"},
        {"type": "bullet", "text": "<b>Factory Surveillance:</b> Unannounced audit to check test records, calibration of gauges, and quality of incoming raw materials."},
        {"type": "bullet", "text": "<b>Market Surveillance:</b> Secret purchase of open-market samples by BIS officials to independently verify retail quality and prevent sub-standard batches from reaching consumers."}
    ]
    create_pdf(RAW_DOCS_DIR / "certification" / "BIS_Product_Certification_Scheme_I_Manual.pdf", "BIS Scheme I Certification Manual", [bis_scheme1_p1, bis_scheme1_p2])

    # 2.2 Compulsory Registration Scheme (CRS) Guide
    bis_crs_p1 = [
        {"type": "title", "text": "BIS COMPULSORY REGISTRATION SCHEME (CRS) GUIDE"},
        {"type": "h1", "text": "SCHEME-II CONFORMITY ASSESSMENT FOR ELECTRONICS & IT GOODS"},
        {"type": "p", "text": "Notified by the Ministry of Electronics & IT (MeitY) and DPIIT under the BIS Act 2016, the Compulsory Registration Scheme covers over 75 categories of electronic, IT, audio-visual, solar, and battery products."},
        {"type": "h2", "text": "KEY CRS ELECTRONIC PRODUCT CATEGORIES & STANDARDS"},
        {"type": "table", "data": [
            ["Product Category", "Applicable Indian Standard", "Key Safety Parameters Evaluated"],
            ["Laptops, Notebooks & Tablets", "IS 13252 (Part 1): 2010", "Electrical insulation, fire retardance, temperature rise"],
            ["Mobile Phones & Smartphones", "IS 13252 (Part 1) & IS 16333", "SAR value limits, charger interface, Indian language support"],
            ["Lithium-ion Cells & Batteries", "IS 16046 (Part 1 & 2): 2018", "Overcharge safety, short-circuit, thermal abuse, drop test"],
            ["LED Bulbs, Luminaires & Drivers", "IS 16102 (Part 1) & IS 15885", "Surge withstand, harmonics, insulation resistance"],
            ["Smart Watches & Fitness Trackers", "IS 13252 (Part 1)", "Battery isolation, ingress protection, low-voltage safety"]
        ], "colWidths": [150, 160, 190]},
        {"type": "h2", "text": "REGISTRATION WORKFLOW & R-NUMBER GENERATION"},
        {"type": "bullet", "text": "1. Sample testing in BIS recognized NABL accredited lab in India."},
        {"type": "bullet", "text": "2. Online application submission on CRS portal within 90 days of test report date."},
        {"type": "bullet", "text": "3. Generation of unique 8-digit R-number (e.g., R-XXXXXXXX)."},
        {"type": "bullet", "text": "4. Affixing standard CRS logo with R-number and standard text on product and packaging."}
    ]
    bis_crs_p2 = [
        {"type": "h2", "text": "AUTHORIZED INDIAN REPRESENTATIVE (AIR) PROVISIONS"},
        {"type": "p", "text": "For foreign manufacturers located outside India, appointing an Authorized Indian Representative (AIR) is legally mandatory. The AIR must be an Indian citizen or registered entity in India that assumes joint legal liability for conformity and consumer grievance handling."},
        {"type": "h2", "text": "VALIDITY AND INCLUSION OF NEW MODELS"},
        {"type": "bullet", "text": "CRS Registration is granted for an initial period of 2 years, renewable for up to 5 years."},
        {"type": "bullet", "text": "New models sharing identical electrical architecture, PCB layout, and safety components can be added under Series Inclusion without repeating complete full-test cycles."}
    ]
    create_pdf(RAW_DOCS_DIR / "certification" / "BIS_Compulsory_Registration_Scheme_CRS_Guide.pdf", "BIS CRS Scheme II Guide", [bis_crs_p1, bis_crs_p2])

    # 2.3 Foreign Manufacturers Certification Scheme (FMCS)
    bis_fmcs_p1 = [
        {"type": "title", "text": "BIS FOREIGN MANUFACTURERS CERTIFICATION SCHEME (FMCS)"},
        {"type": "h1", "text": "OPERATING GUIDELINES FOR OVERSEAS FACTORY CERTIFICATION"},
        {"type": "p", "text": "BIS operates the Foreign Manufacturers Certification Scheme (FMCS) since the year 2000, enabling overseas manufacturing units to obtain an authentic BIS licence to use the Standard Mark (ISI mark) on goods exported to India."},
        {"type": "h2", "text": "FMCS LICENSING PREREQUISITES"},
        {"type": "bullet", "text": "The overseas manufacturing location must have all required in-house production machinery, testing facilities, and qualified quality control personnel complying with Scheme-I."},
        {"type": "bullet", "text": "Appointment of an Authorized Indian Representative (AIR) who is an Indian resident or registered Indian entity."},
        {"type": "bullet", "text": "Submission of physical audit charges (USD 7,000 advance inspection deposit plus actual travel/visa/boarding for 2 BIS inspecting officers)."},
        {"type": "bullet", "text": "Furnishing a Performance Bank Guarantee (PBG) of USD 10,000 from an RBI-approved scheduled commercial bank."},
        {"type": "h2", "text": "AUDIT AND FACTORY INSPECTION PROTOCOL"},
        {"type": "p", "text": "BIS auditors travel to the overseas factory, witness complete testing of products against Indian Standards, verify calibration certificates traceable to BIPM/national metrology institutes, and draw counter-samples to be tested in BIS laboratories in India."}
    ]
    create_pdf(RAW_DOCS_DIR / "certification" / "BIS_Foreign_Manufacturers_Certification_Scheme_FMCS.pdf", "BIS FMCS Guidelines", [bis_fmcs_p1])

    # 2.4 MSME Concessions and Startup Benefits
    bis_msme_p1 = [
        {"type": "title", "text": "BIS FEE CONCESSIONS FOR MSMES, STARTUPS & WOMEN ENTREPRENEURS"},
        {"type": "h1", "text": "OFFICIAL SPECIAL REBATES & RELAXATIONS POLICY (CIRCULAR 2023)"},
        {"type": "p", "text": "To bolster Make in India, Atmanirbhar Bharat, and support grass-root manufacturing units, BIS provides structured fee rebates across its certification and standards portals."},
        {"type": "h2", "text": "STATUTORY CONCESSION STRUCTURE"},
        {"type": "table", "data": [
            ["Category of Enterprise", "Eligibility Proof", "Application Fee Rebate", "Annual Marking Fee Rebate"],
            ["Micro Enterprises", "Udyam Registration Certificate", "50% Concession", "20% Concession"],
            ["Small Enterprises", "Udyam Registration Certificate", "50% Concession", "10% Concession"],
            ["DPIIT Recognized Startups", "DPIIT Recognition Certificate", "50% Concession", "20% Concession"],
            ["Women Entrepreneurs (Micro/Small)", "Female Ownership (>51% equity)", "50% Concession", "25% Concession"]
        ], "colWidths": [120, 150, 110, 120]},
        {"type": "h2", "text": "FREE ACCESS TO INDIAN STANDARDS FOR EDUCATIONAL INSTITUTIONS"},
        {"type": "p", "text": "Under the Standards Portal initiative, BIS provides 100% free digital access to all published Indian Standards for students, faculty, and academic researchers in engineering and science universities."}
    ]
    create_pdf(RAW_DOCS_DIR / "certification" / "BIS_MSME_Startups_and_Women_Entrepreneurs_Concessions.pdf", "BIS MSME & Startup Concessions", [bis_msme_p1])

    # 2.5 Scheme IV Batch Certification Procedures
    bis_scheme4_p1 = [
        {"type": "title", "text": "BIS SCHEME-IV BATCH & LOT CERTIFICATION PROCEDURES"},
        {"type": "h1", "text": "GUIDELINES FOR CONSIGNMENT INSPECTION & CERTIFICATE OF CONFORMITY (COC)"},
        {"type": "p", "text": "Scheme-IV is designed for single production batches or imported consignments where a continuous factory certification licence is not feasible. Applicable to structural steel lots, high-pressure gas cylinders, industrial chemicals, and custom machinery."},
        {"type": "h2", "text": "SAMPLING AND LOT ACCEPTANCE CRITERIA"},
        {"type": "bullet", "text": "BIS inspector draws statistically randomized samples from the identified lot as per IS 2500 (Sampling procedures)."},
        {"type": "bullet", "text": "Samples are sealed and sent to a BIS Central/Regional lab for destructive and non-destructive testing."},
        {"type": "bullet", "text": "Upon full compliance, a Certificate of Conformity (CoC) is issued specifically for the inspected lot/quantity."}
    ]
    create_pdf(RAW_DOCS_DIR / "certification" / "BIS_Scheme_IV_Batch_Certification_Procedures.pdf", "BIS Scheme IV Batch Certification", [bis_scheme4_p1])

    # 2.6 Scheme X Modular Certification
    bis_scheme10_p1 = [
        {"type": "title", "text": "BIS SCHEME-X MODULAR CERTIFICATION FRAMEWORK"},
        {"type": "h1", "text": "CONFORMITY ASSESSMENT FOR INDUSTRIAL MACHINERY & ELECTRICAL SWITCHBOARDS"},
        {"type": "p", "text": "Scheme-X allows manufacturers of custom, heavy engineering capital goods, power transformers, and low-voltage switchgear to certify complex modular assemblies through Factory Production Control (FPC) and design verification without destructive full-assembly testing of every custom variant."},
        {"type": "h2", "text": "FRAMEWORK REQUIREMENTS"},
        {"type": "bullet", "text": "Design verification against relevant Indian and ISO/IEC standards."},
        {"type": "bullet", "text": "Type testing of base modular sub-assemblies (breakers, busbars, enclosures)."},
        {"type": "bullet", "text": "Comprehensive Factory Production Control (FPC) audit by BIS."}
    ]
    create_pdf(RAW_DOCS_DIR / "certification" / "BIS_Scheme_X_Modular_Certification_Framework.pdf", "BIS Scheme X Modular Certification", [bis_scheme10_p1])

    # =========================================================================
    # 3. CATEGORY C: HALLMARKING (Guidelines, HUID, AHC, Mandatory Phases)
    # =========================================================================

    # 3.1 Gold and Silver Hallmarking Guidelines 2024
    bis_hall_guide_p1 = [
        {"type": "title", "text": "BIS GOLD AND SILVER JEWELLERY HALLMARKING GUIDELINES 2024"},
        {"type": "h1", "text": "PURITY SPECIFICATIONS, HUID IDENTIFICATION & CONSUMER ASSURANCE"},
        {"type": "p", "text": "Hallmarking is the accurate determination and official recording of the proportionate content of precious metal in gold and silver articles to protect consumers against adulteration and fraudulent carats."},
        {"type": "h2", "text": "THE 3 MANDATORY MARKS ON GOLD JEWELLERY"},
        {"type": "table", "data": [
            ["Hallmark Element", "Description & Visual Indicator", "Significance for Consumer"],
            ["1. BIS Logo", "Triangular BIS emblem mark", "Signifies official Bureau certification of standard purity"],
            ["2. Purity & Fineness", "e.g., 22K916, 18K750, 14K585", "Guarantees exact gold percentage (91.6%, 75.0%, 58.5%)"],
            ["3. 6-digit HUID", "6-character alphanumeric code (e.g., AB12CD)", "Unique identification tracked in real-time on BIS Care App"]
        ], "colWidths": [120, 180, 200]},
        {"type": "h2", "text": "PERMISSIBLE GOLD PURITY GRADES UNDER IS 1417"},
        {"type": "p", "text": "Under Indian Standard IS 1417 (Gold and gold alloys, jewellery/artefacts), hallmarking is permitted in 6 standard purity categories: <b>24K995</b> (99.5%), <b>23K958</b> (95.8%), <b>22K916</b> (91.6%), <b>20K833</b> (83.3%), <b>18K750</b> (75.0%), and <b>14K585</b> (58.5%)."}
    ]
    bis_hall_guide_p2 = [
        {"type": "h2", "text": "MANDATORY HALLMARKING PHASES ACROSS INDIA"},
        {"type": "p", "text": "The Central Government has implemented mandatory gold hallmarking in a phased manner:"},
        {"type": "bullet", "text": "<b>Phase I (June 2021):</b> 256 districts across India notified."},
        {"type": "bullet", "text": "<b>Phase II (April 2022):</b> 32 additional districts added."},
        {"type": "bullet", "text": "<b>Phase III (September 2023):</b> 55 new districts included."},
        {"type": "bullet", "text": "<b>Phase IV (2024 onwards):</b> Extended to cover all districts having established Assaying & Hallmarking Centres."},
        {"type": "h2", "text": "STATUTORY EXEMPTIONS FROM MANDATORY HALLMARKING"},
        {"type": "bullet", "text": "1. Gold articles weighing less than 2 grams."},
        {"type": "bullet", "text": "2. Gold jewellery manufactured exclusively for export conforming to foreign buyer specifications."},
        {"type": "bullet", "text": "3. Gold jewellery for medical, dental, or scientific research instruments."},
        {"type": "bullet", "text": "4. Special manufactured bullion / investment coins certified under Scheme-IV."}
    ]
    create_pdf(RAW_DOCS_DIR / "hallmarking" / "BIS_Gold_and_Silver_Hallmarking_Guidelines_2024.pdf", "BIS Gold & Silver Hallmarking Guidelines 2024", [bis_hall_guide_p1, bis_hall_guide_p2])

    # 3.2 Jeweller Registration & HUID Portal Guide
    bis_jewel_p1 = [
        {"type": "title", "text": "BIS JEWELLER REGISTRATION & HUID PORTAL USER GUIDE"},
        {"type": "h1", "text": "ONLINE REGISTRATION, WORKFLOW & COMPLIANCE REQUIREMENTS"},
        {"type": "p", "text": "This manual guides retail and wholesale jewellers through registration on Manakonline and daily operations with Assaying & Hallmarking Centres (AHCs)."},
        {"type": "h2", "text": "STEP-BY-STEP JEWELLER REGISTRATION ON MANAKONLINE"},
        {"type": "bullet", "text": "1. Visit www.manakonline.in and navigate to Hallmarking Portal."},
        {"type": "bullet", "text": "2. Provide GSTIN number, PAN card details, and registered address."},
        {"type": "bullet", "text": "3. Instant automatic generation of Jeweller Registration Certificate."},
        {"type": "bullet", "text": "4. Zero registration fee for micro enterprises (turnover < Rs 5 Crore); nominal one-time fee for small/medium jewellers."},
        {"type": "h2", "text": "HALLMARKING CONSIGNMENT SUBMISSION TO AHC"},
        {"type": "p", "text": "The registered jeweller generates an online delivery challan detailing the number of articles and declared purity. Upon delivery to the AHC, the AHC performs XRF screening, fire assay sampling, laser engraves the 3-mark hallmark including HUID, and synchronizes the record to the central BIS database."}
    ]
    create_pdf(RAW_DOCS_DIR / "hallmarking" / "BIS_Jeweller_Registration_and_HUID_Portal_Guide.pdf", "BIS Jeweller Registration & HUID Guide", [bis_jewel_p1])

    # 3.3 AHC Manual
    bis_ahc_p1 = [
        {"type": "title", "text": "BIS ASSAYING & HALLMARKING CENTRES (AHC) MANUAL"},
        {"type": "h1", "text": "TECHNICAL INFRASTRUCTURE, FIRE ASSAY METHOD & AUDITING STANDARDS"},
        {"type": "p", "text": "Assaying and Hallmarking Centres (AHCs) are third-party testing facilities recognized by BIS under IS 15820 to assess the fineness of precious metals and laser-mark HUID codes."},
        {"type": "h2", "text": "TECHNICAL TESTING PROTOCOLS (IS 1418 & IS 2112)"},
        {"type": "bullet", "text": "<b>XRF Non-Destructive Screening:</b> Rapid preliminary verification of alloy composition and surface purity."},
        {"type": "bullet", "text": "<b>Cupellation (Fire Assay Method) - IS 1418:</b> The ultimate referee chemical method for gold purity measurement with an accuracy of 1 part per 10,000."},
        {"type": "bullet", "text": "<b>Laser Marking Stations:</b> High-precision fiber laser marking systems to engrave BIS logo, karat purity, and 6-digit HUID code with minimum height of 0.5 mm without damaging jewellery."},
        {"type": "h2", "text": "MANDATORY CCTV & RECORD KEEPING"},
        {"type": "p", "text": "All AHCs must maintain 24/7 CCTV surveillance of the sample receiving desk, assay laboratory, and laser marking stations with minimum 90-day secure backup for BIS audit verification."}
    ]
    create_pdf(RAW_DOCS_DIR / "hallmarking" / "BIS_Assaying_and_Hallmarking_Centres_AHC_Manual.pdf", "BIS AHC Technical Manual", [bis_ahc_p1])

    # =========================================================================
    # 4. CATEGORY D: LABORATORIES AND TESTING
    # =========================================================================

    # 4.1 BIS Central and Regional Laboratories Directory
    bis_labs_p1 = [
        {"type": "title", "text": "BIS CENTRAL AND REGIONAL LABORATORIES DIRECTORY"},
        {"type": "h1", "text": "NATIONAL TESTING NETWORK INFRASTRUCTURE & DISCIPLINARY SCOPE"},
        {"type": "p", "text": "BIS operates a nationwide network of 8 dedicated Central and Regional testing laboratories and over 25 branch testing cells to support conformity assessment, factory surveillance, and consumer grievance testing."},
        {"type": "h2", "text": "REGIONAL LABORATORY NETWORK"},
        {"type": "table", "data": [
            ["Laboratory Location", "Jurisdiction & Region", "Key Specialized Testing Disciplines"],
            ["Central Laboratory (CL) Sahibabad, Ghaziabad", "Central & National Scope", "Complete Chemical, Electrical, Mechanical, Microbiological, Gold Assay"],
            ["Western Regional Lab (WRL) Mumbai", "Maharashtra, Gujarat, Goa, MP", "Petrochemicals, Plastics, Electrical Motors, Domestic Appliances"],
            ["Eastern Regional Lab (ERL) Kolkata", "WB, Odisha, Bihar, Jharkhand", "Structural Steel, Rebar, Cement, Cables, Jute & Textiles"],
            ["Southern Regional Lab (SRL) Chennai", "TN, Kerala, Karnataka, AP, TS", "Pumps, Motors, Solar Inverters, Electronics, Packaged Water"],
            ["Northern Regional Lab (NRL) Chandigarh", "Punjab, Haryana, HP, J&K", "Agricultural Machinery, Pressure Cookers, Pesticides, Toys"],
            ["Guwahati Regional Lab", "North Eastern States", "Plywood, Building Materials, Drinking Water, Spices"]
        ], "colWidths": [140, 130, 230]},
        {"type": "h2", "text": "ACCREDITATION & PROFICIENCY"},
        {"type": "p", "text": "All BIS in-house laboratories are accredited by the National Accreditation Board for Testing and Calibration Laboratories (NABL) in accordance with ISO/IEC 17025."}
    ]
    create_pdf(RAW_DOCS_DIR / "laboratories" / "BIS_Central_and_Regional_Laboratories_Directory.pdf", "BIS Central & Regional Labs Directory", [bis_labs_p1])

    # 4.2 Laboratory Recognition Scheme (LRS) 2020
    bis_lrs_p1 = [
        {"type": "title", "text": "BIS LABORATORY RECOGNITION SCHEME (LRS) 2020"},
        {"type": "h1", "text": "TERMS, CONDITIONS & AUDIT RULES FOR PRIVATE/COMMERCIAL TESTING LABS"},
        {"type": "p", "text": "The Laboratory Recognition Scheme (LRS) 2020 enables BIS to recognize competent commercial, institutional, and state laboratories across India and abroad to test conformity assessment and surveillance samples."},
        {"type": "h2", "text": "LRS ELIGIBILITY CRITERIA"},
        {"type": "bullet", "text": "1. Valid ISO/IEC 17025 accreditation from NABL or an APAC/ILAC MRA partner."},
        {"type": "bullet", "text": "2. Specific testing scope matching the latest version of applicable Indian Standards."},
        {"type": "bullet", "text": "3. Calibrated testing equipment traceable to National Physical Laboratory (NPL India)."},
        {"type": "bullet", "text": "4. Mandatory integration with BIS LIMS (Laboratory Information Management System) portal."},
        {"type": "h2", "text": "MONITORING AND DE-RECOGNITION"},
        {"type": "p", "text": "Recognized laboratories undergo annual surveillance audits and mandatory participation in Inter-Laboratory Comparisons (ILC). Misreporting or collusion leads to immediate blacklisting and forfeiture of security deposit under Regulation 15."}
    ]
    create_pdf(RAW_DOCS_DIR / "laboratories" / "BIS_Laboratory_Recognition_Scheme_LRS_2020.pdf", "BIS Laboratory Recognition Scheme LRS 2020", [bis_lrs_p1])

    # 4.3 Testing Manual and LIMS Portal Guidelines
    bis_lims_p1 = [
        {"type": "title", "text": "BIS TESTING MANUAL & LIMS DIGITAL WORKFLOW"},
        {"type": "h1", "text": "BLIND CODING, SAMPLE LIFECYCLE & ELECTRONIC TEST REPORTS (ETR)"},
        {"type": "p", "text": "The Laboratory Information Management System (LIMS) is an end-to-end cloud platform automating the lifecycle of test samples drawn across India."},
        {"type": "h2", "text": "KEY LIMS PILLARS"},
        {"type": "bullet", "text": "<b>Automated Blind Coding:</b> When a factory or market sample is received, LIMS automatically replaces manufacturer details with an encrypted alphanumeric barcode to eliminate bias."},
        {"type": "bullet", "text": "<b>Direct Machine Data Acquisition:</b> Test readings from tensile machines, spectrophotometers, and electrical safety analyzers are captured electronically."},
        {"type": "bullet", "text": "<b>QR-Coded Electronic Test Report (ETR):</b> All final test reports feature a tamper-proof cryptographic QR code verifiable on the BIS website."}
    ]
    create_pdf(RAW_DOCS_DIR / "laboratories" / "BIS_Testing_Manual_and_LIMS_Portal_Guidelines.pdf", "BIS Testing Manual & LIMS Portal", [bis_lims_p1])

    # =========================================================================
    # 5. CATEGORY E: STANDARDS AND STANDARDIZATION (Formulation, Committees, ISO)
    # =========================================================================

    # 5.1 Standardization Process and Committee Structure
    bis_std_process_p1 = [
        {"type": "title", "text": "BIS STANDARDIZATION PROCESS & COMMITTEE STRUCTURE"},
        {"type": "h1", "text": "THE 15 DIVISION COUNCILS & FORMULATION METHODOLOGY"},
        {"type": "p", "text": "As the National Standards Body of India, BIS operates through 15 Division Councils covering all sectors of the national economy."},
        {"type": "h2", "text": "THE 15 DIVISION COUNCILS OF BIS"},
        {"type": "table", "data": [
            ["Council Code", "Division Council Name", "Representative Standards Formulated"],
            ["CED", "Civil Engineering Division", "Cement (IS 269), Rebar (IS 1786), Concrete (IS 456), NBC 2016"],
            ["ETD", "Electrotechnical Division", "Transformers (IS 1180), Cables (IS 694), Switchgear (IS/IEC 60947)"],
            ["LITD", "Electronics and Information Technology", "AI (IS/ISO 22989), IoT (IS/ISO 30141), Cybersecurity (IS 27001), CRS"],
            ["MED", "Mechanical Engineering Division", "Pressure vessels, Compressors, Pumps (IS 9079), Machine tools"],
            ["PCD", "Petroleum, Coal and Related Products", "Lubricants, Biofuels, Polymers, Rubber, Petrochemicals"],
            ["CHD", "Chemical Division", "Paints, Caustic Soda, Industrial chemicals, Soaps, Cosmetics"],
            ["FAD", "Food and Agriculture Division", "Packaged water (IS 14543), Dairy (IS 1224), Spices, Fertilizers"],
            ["MHD", "Medical Equipment and Hospital Planning", "Surgical implants, Ventilators, PPE kits, Medical electricals"]
        ], "colWidths": [80, 200, 220]},
        {"type": "p", "text": "Other active Division Councils include TXD (Textiles), MTD (Metallurgy), MSD (Management & Systems), PGD (Production & General), TED (Transport), SSD (Services Sector), and SSD-II (Sustainability & ESG)."}
    ]
    bis_std_process_p2 = [
        {"type": "h2", "text": "THE 6 STAGES OF INDIAN STANDARD FORMULATION"},
        {"type": "bullet", "text": "<b>Stage 1: Proposal Stage (NWIP):</b> New Work Item Proposal submitted by industry, government, or public."},
        {"type": "bullet", "text": "<b>Stage 2: Preparatory Stage (Working Draft - WD):</b> Draft formulated by expert working group."},
        {"type": "bullet", "text": "<b>Stage 3: Committee Stage (Committee Draft - CD):</b> Deliberated by Sectional Committee representing industry, academia, and consumers."},
        {"type": "bullet", "text": "<b>Stage 4: Public Enquiry Stage (Wide Circulation - WC):</b> Published on Manakonline for 30 to 60 days for public comments."},
        {"type": "bullet", "text": "<b>Stage 5: Approval Stage:</b> Formal adoption by the Sectional Committee and Chairman of Division Council."},
        {"type": "bullet", "text": "<b>Stage 6: Publication Stage:</b> Gazette notification and publication as an authoritative Indian Standard."}
    ]
    create_pdf(RAW_DOCS_DIR / "standards" / "BIS_Standardization_Process_and_Committee_Structure.pdf", "BIS Standardization & Committees", [bis_std_process_p1, bis_std_process_p2])

    # 5.2 Specific Indian Standards (IS 302, IS 1293, IS 1786, IS 9873)
    bis_is302_p1 = [
        {"type": "title", "text": "INDIAN STANDARD SPECIFICATION: IS 302 (PART 1): 2024"},
        {"type": "h1", "text": "SAFETY OF HOUSEHOLD AND SIMILAR ELECTRICAL APPLIANCES - GENERAL REQUIREMENTS"},
        {"type": "p", "text": "Standard Number: <b>IS 302 : Part 1 : 2024</b> (Harmonized with IEC 60335-1). Applicable to all single-phase household appliances rated up to 250 V."},
        {"type": "h2", "text": "MANDATORY SAFETY CLAUSES"},
        {"type": "bullet", "text": "<b>Clause 8: Protection Against Access to Live Parts:</b> Test Probe B of IS 1401 applied with 10 N force must not contact hazardous live parts."},
        {"type": "bullet", "text": "<b>Clause 10: Power Input and Current:</b> Measured power input must not exceed marked rating by more than specified tolerances (+5% to +10%)."},
        {"type": "bullet", "text": "<b>Clause 13: Electrical Strength & Leakage Current at Operating Temp:</b> Leakage current shall not exceed 0.75 mA for Class I portable appliances; high-voltage withstand of 1000 V to 1250 V AC."},
        {"type": "bullet", "text": "<b>Clause 19: Abnormal Operation & Fire Safety:</b> Appliances must not catch fire during stalled rotor or simulated electronic fault conditions. Glow Wire Test (IS 11000) at 750°C/850°C on insulating supports."},
        {"type": "callout", "text": "Mandatory under the Electrical Appliances (Quality Control) Order. Applicable to water heaters (IS 302-2-201), electric irons (IS 302-2-3), and kitchen mixers (IS 302-2-14)."}
    ]
    create_pdf(RAW_DOCS_DIR / "standards" / "IS_302_Household_Electrical_Appliances_Safety_Overview.pdf", "IS 302 Household Appliances Safety", [bis_is302_p1])

    # 5.3 IS 1786 Steel Rebar Standard
    bis_is1786_p1 = [
        {"type": "title", "text": "INDIAN STANDARD SPECIFICATION: IS 1786 : 2008 (AMENDED)"},
        {"type": "h1", "text": "HIGH STRENGTH DEFORMED STEEL BARS AND WIRES FOR CONCRETE REINFORCEMENT (TMT)"},
        {"type": "p", "text": "Standard Number: <b>IS 1786 : 2008</b> (Reaffirmed 2023). Mandatory under the Steel and Steel Products (Quality Control) Order. Covers Thermo-Mechanically Treated (TMT) bars for civil construction."},
        {"type": "h2", "text": "MECHANICAL PROPERTY REQUIREMENTS"},
        {"type": "table", "data": [
            ["Steel Strength Grade", "Min 0.2% Proof Stress (MPa)", "Min Tensile Strength (MPa)", "Min Elongation (%)", "Total Elongation at Max Force (TS/YS Ratio)"],
            ["Fe 415", "415.0", "485.0 (or 1.10 x YS)", "14.5%", "Not specified"],
            ["Fe 500", "500.0", "545.0 (or 1.08 x YS)", "12.0%", "Not specified"],
            ["Fe 500D (Ductile)", "500.0", "565.0 (or 1.10 x YS)", "16.0%", "Min 5.0% (Earthquake Resistant)"],
            ["Fe 550D", "550.0", "600.0 (or 1.08 x YS)", "14.5%", "Min 5.0%"],
            ["Fe 600", "600.0", "660.0 (or 1.06 x YS)", "10.0%", "Not specified"]
        ], "colWidths": [110, 110, 110, 80, 90]},
        {"type": "h2", "text": "MANDATORY MARKING ON BARS"},
        {"type": "p", "text": "Every metre of rebar must have rolled-on manufacturer brand name, grade (e.g., Fe 500D), diameter (e.g., 12mm), and the authentic BIS ISI Standard Mark."}
    ]
    create_pdf(RAW_DOCS_DIR / "standards" / "IS_1786_High_Strength_Deformed_Steel_Rebar_Standard.pdf", "IS 1786 TMT Steel Rebar Standard", [bis_is1786_p1])

    # 5.4 IS 9873 Toys Safety Standard
    bis_is9873_p1 = [
        {"type": "title", "text": "INDIAN STANDARD SPECIFICATION: IS 9873 (SAFETY OF TOYS)"},
        {"type": "h1", "text": "PARTS 1 TO 9 COMPLIANCE UNDER THE TOYS (QUALITY CONTROL) ORDER"},
        {"type": "p", "text": "Under the Toys (Quality Control) Order, 2020 issued by DPIIT, no toy can be imported or sold in India without BIS certification under Scheme-I complying with IS 9873 and IS 15644."},
        {"type": "h2", "text": "THE IS 9873 MULTI-PART SERIES STRUCTURE"},
        {"type": "table", "data": [
            ["Standard Number", "Title & Scope", "Key Hazards Tested"],
            ["IS 9873 (Part 1): 2019", "Mechanical and Physical Properties", "Small parts ingestion (choking cylinder), sharp edges, points, drop test"],
            ["IS 9873 (Part 2): 2017", "Flammability Requirements", "Rate of flame spread across plush, fabric, and costume materials"],
            ["IS 9873 (Part 3): 2020", "Migration of Certain Elements (Toxicity)", "Heavy metal limits for Lead (Pb), Cadmium (Cd), Mercury (Hg), Arsenic (As)"],
            ["IS 9873 (Part 9): 2017", "Phthalates in Toys & Child Care Articles", "Chemical plasticizer limits for DEHP, DBP, BBP, DINP (<0.1% by mass)"],
            ["IS 15644 : 2006", "Safety of Electric Toys", "Operating voltage (<24V), heating, moisture resistance, battery compartments"]
        ], "colWidths": [120, 170, 210]}
    ]
    create_pdf(RAW_DOCS_DIR / "standards" / "IS_9873_Safety_of_Toys_Specification_Guide.pdf", "IS 9873 Safety of Toys Guide", [bis_is9873_p1])

    # =========================================================================
    # 6. CATEGORY F: REFERENCE HANDBOOKS (Electrical, Electronics/AI, Building, HVAC, Mechanical)
    # =========================================================================

    # 6.1 Electrical Engineering Handbook
    bis_hb_elec_p1 = [
        {"type": "title", "text": "BIS REFERENCE HANDBOOK: ELECTRICAL ENGINEERING & POWER APPARATUS"},
        {"type": "h1", "text": "STANDARDS COMPENDIUM FOR TRANSFORMERS, CABLES, MOTORS & SWITCHGEAR"},
        {"type": "p", "text": "This official reference handbook provides engineers, utilities, and manufacturers with guidance on compliance with mandatory electrotechnical Indian Standards."},
        {"type": "h2", "text": "1. DISTRIBUTION TRANSFORMERS (IS 1180 PART 1 : 2014)"},
        {"type": "bullet", "text": "Applicable to outdoor/indoor liquid immersed distribution transformers up to 2500 kVA, 33 kV."},
        {"type": "bullet", "text": "Mandatory energy efficiency loss levels: Level 1, Level 2, and Level 3 (BEE 5-star equivalent)."},
        {"type": "bullet", "text": "Routine tests (winding resistance, voltage ratio, short-circuit impedance) and type tests (temperature rise, lightning impulse, short-circuit withstand test at CPRI/ERDA)."},
        {"type": "h2", "text": "2. ELECTRIC CABLES & WIRES (IS 694 & IS 7098)"},
        {"type": "bullet", "text": "<b>IS 694 : 2010:</b> PVC insulated cables for working voltages up to and including 1100 V (house wiring, flexible cords)."},
        {"type": "bullet", "text": "<b>IS 7098 (Part 1 & 2):</b> Cross-linked Polyethylene (XLPE) insulated power cables for voltages up to 33 kV. High thermal rating (90°C continuous, 250°C short circuit)."}
    ]
    bis_hb_elec_p2 = [
        {"type": "h2", "text": "3. THREE-PHASE INDUCTION MOTORS (IS 12615 : 2018)"},
        {"type": "p", "text": "Specifies energy efficiency classes for 3-phase squirrel cage induction motors (0.12 kW to 1000 kW):"},
        {"type": "table", "data": [
            ["Efficiency Class", "Standard Code", "Statutory Status in India"],
            ["IE1 (Standard Efficiency)", "IS 12615", "Phased out in India"],
            ["IE2 (High Efficiency)", "IS 12615", "Minimum mandatory baseline under Electrical Motors QCO"],
            ["IE3 (Premium Efficiency)", "IS 12615", "Mandated for large industrial utilities & green procurement"],
            ["IE4 (Super Premium)", "IS 12615", "Ultra-high efficiency for mission critical installations"]
        ], "colWidths": [150, 120, 230]},
        {"type": "h2", "text": "4. LOW-VOLTAGE SWITCHGEAR & CONTROLGEAR (IS/IEC 60947 & IS/IEC 61439)"},
        {"type": "p", "text": "Covers Circuit Breakers (MCB, MCCB, ACB), Contactors, and Factory-built Low-Voltage Assemblies with internal arc containment and short-circuit withstand ratings."}
    ]
    create_pdf(RAW_DOCS_DIR / "handbooks" / "BIS_Handbook_Electrical_Engineering_and_Power_Apparatus.pdf", "BIS Electrical Engineering Handbook", [bis_hb_elec_p1, bis_hb_elec_p2])

    # 6.2 Electronics, AI, IoT & Software Testing Handbook
    bis_hb_ai_p1 = [
        {"type": "title", "text": "BIS REFERENCE HANDBOOK: ELECTRONICS, AI, IOT & SOFTWARE TESTING"},
        {"type": "h1", "text": "EMERGING TECHNOLOGY STANDARDS (LITD COUNCIL PUBLICATIONS)"},
        {"type": "p", "text": "Formulated by the LITD 30 (Artificial Intelligence), LITD 27 (IoT), and LITD 15 (Software & Systems Engineering) committees, this handbook outlines national standards for digital trust."},
        {"type": "h2", "text": "1. ARTIFICIAL INTELLIGENCE STANDARDS"},
        {"type": "bullet", "text": "<b>IS/ISO/IEC 22989 : 2022:</b> Information technology - Artificial Intelligence - Concepts and Terminology. Defines foundational terms (ML, Neural Networks, Bias, Explainability, Robustness)."},
        {"type": "bullet", "text": "<b>IS/ISO/IEC 42001 : 2023:</b> Artificial Intelligence Management System (AIMS). International certifiable standard for responsible development, deployment, and risk management of AI systems."},
        {"type": "bullet", "text": "<b>IS/ISO/IEC 23894 : 2023:</b> Guidance on Risk Management for Artificial Intelligence."},
        {"type": "h2", "text": "2. INTERNET OF THINGS (IOT) & CYBERSECURITY"},
        {"type": "bullet", "text": "<b>IS/ISO/IEC 30141 : 2018:</b> IoT Reference Architecture (Domain model, trust boundaries, gateway connectivity)."},
        {"type": "bullet", "text": "<b>IS/ISO/IEC 27001 : 2022:</b> Information Security, Cybersecurity and Privacy Protection Management Systems."},
        {"type": "bullet", "text": "<b>IS 17428 : 2020:</b> Data Privacy Assurance - Engineering and Management requirements for personal data protection in India."}
    ]
    bis_hb_ai_p2 = [
        {"type": "h2", "text": "3. SOFTWARE QUALITY & SOFTWARE TESTING STANDARDS"},
        {"type": "table", "data": [
            ["Standard Number", "Standard Title", "Engineering Application Scope"],
            ["IS/ISO/IEC 25010 : 2023", "Systems and Software Quality Requirements and Evaluation (SQuaRE)", "Defines 8 quality characteristics: Functional suitability, Performance, Compatibility, Usability, Reliability, Security, Maintainability, Portability"],
            ["IS/ISO/IEC 29119 (Part 1-5)", "Software Testing Standard Series", "Part 1 (Concepts), Part 2 (Test Processes), Part 3 (Test Documentation - Test Plan, Test Case, Defect Report), Part 4 (Test Techniques - Boundary Value, Equivalence Partitioning), Part 5 (Keyword Testing)"],
            ["IS/IEC 61508", "Functional Safety of Electrical / Electronic / Programmable Safety Systems", "Safety Integrity Levels (SIL 1 to SIL 4) for embedded software in railway, medical, and aerospace control systems"]
        ], "colWidths": [120, 160, 220]}
    ]
    create_pdf(RAW_DOCS_DIR / "handbooks" / "BIS_Handbook_Electronics_AI_IoT_and_Software_Testing.pdf", "BIS AI, IoT & Software Testing Handbook", [bis_hb_ai_p1, bis_hb_ai_p2])

    # 6.3 Building Materials & Civil Engineering Handbook
    bis_hb_civil_p1 = [
        {"type": "title", "text": "BIS REFERENCE HANDBOOK: BUILDING MATERIALS & CIVIL ENGINEERING"},
        {"type": "h1", "text": "STANDARDS COMPENDIUM FOR CEMENT, CONCRETE, TMT STEEL & NBC 2016"},
        {"type": "p", "text": "This handbook summarizes essential standards formulated by the Civil Engineering Division (CED) governing construction safety and structural integrity across India."},
        {"type": "h2", "text": "1. CEMENT STANDARDS SPECIFICATIONS"},
        {"type": "bullet", "text": "<b>IS 269 : 2015:</b> Ordinary Portland Cement (OPC 33, 43, and 53 grades). Mandatory 28-day compressive strength of 53 MPa for OPC 53."},
        {"type": "bullet", "text": "<b>IS 1489 (Part 1 & 2):</b> Portland Pozzolana Cement (PPC - Fly Ash based and Calcined Clay based). High resistance to chemical/sulfate attacks."},
        {"type": "bullet", "text": "<b>IS 455 : 2015:</b> Portland Slag Cement (PSC) for marine and coastal construction."},
        {"type": "h2", "text": "2. PLAIN AND REINFORCED CONCRETE (IS 456 : 2000)"},
        {"type": "p", "text": "The foundational code of practice for structural RCC design in India. Specifies minimum cement content, maximum water-cement ratio, exposure conditions (Mild, Moderate, Severe, Very Severe, Extreme), and limit state design methodology."}
    ]
    create_pdf(RAW_DOCS_DIR / "handbooks" / "BIS_Handbook_Building_Materials_and_Civil_Engineering.pdf", "BIS Building Materials Handbook", [bis_hb_civil_p1])

    # 6.4 HVAC, Refrigeration & Renewable Energy Handbook
    bis_hb_hvac_p1 = [
        {"type": "title", "text": "BIS REFERENCE HANDBOOK: HVAC, REFRIGERATION & RENEWABLE ENERGY"},
        {"type": "h1", "text": "STANDARDS COMPENDIUM FOR AIR CONDITIONERS, SOLAR PV & GREEN TECH"},
        {"type": "p", "text": "Governed by PCD, ETD, and MED committees to ensure energy efficiency, thermal comfort, and renewable energy adoption."},
        {"type": "h2", "text": "1. ROOM AIR CONDITIONERS (IS 1391 PART 1 & 2 / IS/IEC 60335-2-40)"},
        {"type": "bullet", "text": "Window and Split Air Conditioners testing for Cooling Capacity, ISEER (Indian Seasonal Energy Efficiency Ratio), and safety under low-GWP flammable refrigerants (R-32, R-290)."},
        {"type": "h2", "text": "2. SOLAR PHOTOVOLTAIC MODULES & INVERTERS"},
        {"type": "bullet", "text": "<b>IS 14286 / IEC 61215:</b> Terrestrial photovoltaic (PV) modules design qualification and type approval (damp heat test, thermal cycling, mechanical load test 5400 Pa)."},
        {"type": "bullet", "text": "<b>IS/IEC 61730 (Part 1 & 2):</b> PV module safety qualification (fire test, electrical shock hazard)."},
        {"type": "bullet", "text": "<b>IS 16221 (Part 2) & IS 16169:</b> Solar utility grid-tied inverters safety and anti-islanding protection."}
    ]
    create_pdf(RAW_DOCS_DIR / "handbooks" / "BIS_Handbook_Refrigeration_Air_Conditioning_and_Renewable_Energy.pdf", "BIS HVAC & Renewable Energy Handbook", [bis_hb_hvac_p1])

    # 6.5 Mechanical Testing Handbook
    bis_hb_mech_p1 = [
        {"type": "title", "text": "BIS REFERENCE HANDBOOK: MECHANICAL TESTING & RISK ASSESSMENT"},
        {"type": "h1", "text": "STANDARDS FOR TENSILE, IMPACT, HARDNESS & MACHINERY RISK"},
        {"type": "p", "text": "Technical manual detailing standardized test procedures for metals, polymers, pressure vessels, and industrial safety machinery."},
        {"type": "h2", "text": "STANDARDIZED METALLURGICAL TEST METHODS"},
        {"type": "table", "data": [
            ["Test Category", "Standard Number", "Test Method & Parameters"],
            ["Tensile Testing of Metals", "IS 1608 (Part 1) / ISO 6892-1", "Determination of Yield Strength (0.2% Proof Stress), Ultimate Tensile Strength (UTS), % Elongation at ambient temperature"],
            ["Charpy Impact Test (V-notch)", "IS 1757 (Part 1) / ISO 148-1", "Measurement of impact energy absorption in Joules (J) at +20°C, 0°C, or sub-zero -40°C temperatures"],
            ["Rockwell Hardness Test", "IS 1586 (Part 1) / ISO 6508-1", "HRA, HRB, HRC scales using diamond spheroconical indenter or tungsten carbide ball"],
            ["Vickers & Brinell Hardness", "IS 1501 & IS 1500", "Micro and macro hardness testing under loads from 1 kgf to 3000 kgf"],
            ["Machinery Risk Assessment", "IS/ISO 12100 : 2010", "Risk assessment and risk reduction principles for industrial machinery"]
        ], "colWidths": [130, 140, 230]}
    ]
    create_pdf(RAW_DOCS_DIR / "handbooks" / "BIS_Handbook_Mechanical_Testing_and_Safety_Risk_Assessment.pdf", "BIS Mechanical Testing Handbook", [bis_hb_mech_p1])

    # =========================================================================
    # 7. CATEGORY G: CONSUMER INFORMATION (Rights, Care App, FAQs)
    # =========================================================================

    # 7.1 Consumer Protection & Care App Handbook
    bis_cons_p1 = [
        {"type": "title", "text": "BIS CONSUMER PROTECTION RIGHTS & CARE APP HANDBOOK"},
        {"type": "h1", "text": "CITIZEN GUIDE TO VERIFYING CERTIFICATION MARKS & REPORTING VIOLATIONS"},
        {"type": "p", "text": "Bureau of Indian Standards empowers 1.4 billion Indian citizens with digital verification tools to identify genuine ISI, Hallmark, and CRS certification marks and avoid counterfeit or hazardous goods."},
        {"type": "h2", "text": "HOW CONSUMERS CAN IDENTIFY GENUINE CERTIFICATION MARKS"},
        {"type": "table", "data": [
            ["Certification Mark", "Visual Identifying Elements", "Citizen Verification Procedure"],
            ["ISI Standard Mark", "ISI monogram + IS Standard No. on top + 7 to 10 digit CM/L license number at bottom", "Enter CM/L number in BIS Care App -> 'Verify License Details' -> check licensee name, brand & validity"],
            ["Hallmark (Gold)", "BIS Triangle Logo + Purity in Karat/Fineness (e.g. 22K916) + 6-digit alphanumeric HUID", "Enter 6-digit HUID in BIS Care App -> 'Verify HUID' -> view jeweller registration, AHC name & stamping date"],
            ["CRS Registration", "Standard CRS logo with words 'Self-Declaration - Conforming to IS...' + 8-digit R-number", "Enter R-number in BIS Care App -> 'Verify R-No' -> verify brand, overseas/domestic factory & active model list"]
        ], "colWidths": [110, 180, 210]},
        {"type": "h2", "text": "FILING COMPLAINTS VIA BIS CARE MOBILE APP"},
        {"type": "bullet", "text": "Download BIS Care App from Google Play Store or Apple App Store."},
        {"type": "bullet", "text": "Navigate to 'File a Complaint' -> Select category: Sub-standard product / Misuse of ISI mark / Faulty Hallmarking / Deceptive Ad."},
        {"type": "bullet", "text": "Upload photo of bill, product label, and GPS shop location."},
        {"type": "bullet", "text": "Track complaint status in real-time. BIS conducts raid and investigation within 15-30 days."}
    ]
    create_pdf(RAW_DOCS_DIR / "consumer" / "BIS_Consumer_Protection_Rights_and_Care_App_Handbook.pdf", "BIS Consumer Protection Handbook", [bis_cons_p1])

    # 7.2 Consumer Grievance FAQs
    bis_cons_faqs_p1 = [
        {"type": "title", "text": "BIS CONSUMER GRIEVANCE REDRESSAL MECHANISM & FAQS"},
        {"type": "h1", "text": "FREQUENTLY ASKED QUESTIONS ON ISI, HALLMARKING & PRODUCT COMPLAINTS"},
        {"type": "h2", "text": "TOP CONSUMER FAQS"},
        {"type": "p", "text": "<b>Q1. What is an ISI mark and why is it important?</b><br/>The ISI mark is the official third-party quality certification mark of BIS. It certifies that the product has undergone rigorous laboratory testing and meets all safety, reliability, and quality parameters specified in the applicable Indian Standard."},
        {"type": "p", "text": "<b>Q2. Can a jeweller sell non-hallmarked gold jewellery in a notified district?</b><br/>No. Selling non-hallmarked gold jewellery in designated mandatory hallmarking districts is a statutory offence under Section 29 of the BIS Act 2016, punishable with fine up to 5 times the value of the article or imprisonment up to 1 year."},
        {"type": "p", "text": "<b>Q3. Can an individual get personal gold jewellery tested for purity?</b><br/>Yes. A consumer can get personal gold jewellery tested at any BIS recognized Assaying & Hallmarking Centre (AHC) upon paying a nominal fee of Rs 45 per article (+ GST). The AHC issues an official assay test report to the consumer."},
        {"type": "p", "text": "<b>Q4. What should a consumer do if an ISI-marked appliance fails prematurely?</b><br/>File a grievance on the BIS Care App with purchase receipt. BIS investigates the manufacturer, draws batch test samples, and directs replacement or refund if product is found non-conforming."}
    ]
    create_pdf(RAW_DOCS_DIR / "consumer" / "BIS_Consumer_Grievance_Redressal_Mechanism_and_FAQs.pdf", "BIS Consumer Grievance FAQs", [bis_cons_faqs_p1])

    # =========================================================================
    # 8. CATEGORY H: QUALITY CONTROL ORDERS (QCO Compendium, Toys, Steel, Chemicals)
    # =========================================================================

    # 8.1 QCO Compendium 2024
    bis_qco_comp_p1 = [
        {"type": "title", "text": "BIS QUALITY CONTROL ORDERS (QCO) COMPENDIUM 2024"},
        {"type": "h1", "text": "STATUTORY MANDATORY CONFORMITY NOTIFICATIONS UNDER SECTION 16"},
        {"type": "p", "text": "Quality Control Orders (QCOs) issued by various Central Ministries under Section 16 of the BIS Act 2016 prohibit the manufacture, import, stocking, sale, or distribution of non-certified goods in India."},
        {"type": "h2", "text": "SECTOR-WISE SUMMARY OF KEY QUALITY CONTROL ORDERS"},
        {"type": "table", "data": [
            ["Line Ministry", "Major QCO Categories", "Key Indian Standards", "Enforcement Status"],
            ["DPIIT (Min. of Commerce)", "Toys, Footwear, Cement, Safety Glass, Domestic Pressure Cookers, Gas Stoves", "IS 9873, IS 15844, IS 269, IS 2553, IS 2347, IS 4246", "Mandatory in force (MSME dates applied)"],
            ["Ministry of Steel", "Steel & Steel Products (TMT rebar, structural steel, stainless steel sheets, tinplates)", "IS 1786, IS 2062, IS 6911, IS 1993 (145+ standards)", "100% Mandatory across all imports & domestic plants"],
            ["MeitY", "Electronics & IT Goods (Laptops, mobile phones, servers, LED lighting, power banks)", "IS 13252, IS 16046, IS 16102 (75+ product lines under CRS)", "Mandatory under Compulsory Registration Scheme"],
            ["Min. of Chemicals & Petrochemicals", "Caustic Soda, Hydrogen Peroxide, PVC Resin, Acetic Acid, Polyethylene", "IS 252, IS 2080, IS 10151, IS 14753", "Mandatory in phased gazette notifications"],
            ["Ministry of Heavy Industries", "Pumps, Electric Motors, Low-Voltage Transformers, Compressors", "IS 12615, IS 9079, IS 1180", "Mandatory for domestic & industrial use"]
        ], "colWidths": [120, 160, 120, 100]}
    ]
    bis_qco_comp_p2 = [
        {"type": "h2", "text": "MSME EXEMPTIONS AND TIMELINE EXTENSIONS UNDER QCOS"},
        {"type": "p", "text": "To prevent supply-chain bottlenecks and support small enterprises, recent QCOs issued by DPIIT provide graded timeline relaxations:"},
        {"type": "bullet", "text": "<b>Large Enterprises:</b> Mandatory immediately upon publication of effective date."},
        {"type": "bullet", "text": "<b>Small Enterprises:</b> Additional 6 to 9 months transition period."},
        {"type": "bullet", "text": "<b>Micro Enterprises:</b> Additional 12 months transition period or specific exemption thresholds (e.g. Footwear QCO)."},
        {"type": "callout", "text": "Violation of a mandatory QCO constitutes a cognizable offence under Section 29(1) of the BIS Act 2016 resulting in seizure, cancellation of import shipments at Indian ports, and criminal prosecution in Magistrate court."}
    ]
    create_pdf(RAW_DOCS_DIR / "qco" / "BIS_Quality_Control_Orders_QCO_Compendium_2024.pdf", "BIS QCO Compendium 2024", [bis_qco_comp_p1, bis_qco_comp_p2])

    # 8.2 QCO Toys and Footwear
    bis_qco_toys_p1 = [
        {"type": "title", "text": "BIS QUALITY CONTROL ORDERS: TOYS & FOOTWEAR"},
        {"type": "h1", "text": "REGULATORY GUIDANCE FOR DOMESTIC MANUFACTURERS & IMPORTERS"},
        {"type": "h2", "text": "1. TOYS (QUALITY CONTROL) ORDER"},
        {"type": "bullet", "text": "Notified by DPIIT. All toys designed for children under 14 years must bear the authentic ISI Mark under Scheme-I."},
        {"type": "bullet", "text": "Non-electric toys must conform to IS 9873 (Parts 1, 2, 3, 4, 7, 9)."},
        {"type": "bullet", "text": "Electric toys must additionally conform to IS 15644."},
        {"type": "bullet", "text": "Zero import consignment of non-certified toys permitted through Indian customs."},
        {"type": "h2", "text": "2. FOOTWEAR (QUALITY CONTROL) ORDERS"},
        {"type": "table", "data": [
            ["Footwear Category", "Indian Standard Number", "Product Scope"],
            ["Leather Safety Footwear", "IS 15298 (Part 2): 2016", "Safety shoes with steel/composite toe cap withstanding 200 Joules impact"],
            ["Sports Footwear", "IS 15844 (Part 1 & 2): 2023", "Running, training, football, and casual athletic footwear"],
            ["Rubber Hawai Chappals", "IS 10702 : 1992", "Rubber slippers, strap strength, density, and flexing resistance"],
            ["All Rubber Gum Boots", "IS 5557 : 2004", "Industrial and mining waterproof rubber protective boots"]
        ], "colWidths": [150, 150, 200]}
    ]
    create_pdf(RAW_DOCS_DIR / "qco" / "BIS_QCO_Toys_Safety_and_Footwear_Orders_Guide.pdf", "BIS QCO Toys & Footwear Guide", [bis_qco_toys_p1])

    # 8.3 QCO Steel and Chemicals
    bis_qco_steel_p1 = [
        {"type": "title", "text": "BIS QUALITY CONTROL ORDERS: STEEL, CHEMICALS & CABLES"},
        {"type": "h1", "text": "MANDATORY COMPLIANCE COMPENDIUM FOR INDUSTRIAL COMMODITIES"},
        {"type": "h2", "text": "STEEL QUALITY CONTROL ORDER COMPLIANCE"},
        {"type": "p", "text": "Under the Steel and Steel Products (Quality Control) Order issued by the Ministry of Steel, over 145 steel specifications are mandatory. Domestic steel mills and overseas producers exporting to India must have active BIS Scheme-I licences or Scheme-IV lot inspection certificates."},
        {"type": "bullet", "text": "<b>IS 2062 : 2011:</b> Hot Rolled Medium and High Tensile Structural Steel (plates, sections, angles)."},
        {"type": "bullet", "text": "<b>IS 277 : 2018:</b> Galvanized Steel Sheets (plain and corrugated)."},
        {"type": "bullet", "text": "<b>IS 6911 : 2017:</b> Stainless steel plate, sheet, and strip for utensils and architectural use."},
        {"type": "h2", "text": "CHEMICALS & PETROCHEMICALS QUALITY CONTROL ORDERS"},
        {"type": "bullet", "text": "<b>Caustic Soda (IS 252):</b> Mandatory chemical purity >99.5% for industrial and water treatment use."},
        {"type": "bullet", "text": "<b>PVC Resins for Food Contact (IS 10151):</b> Residual vinyl chloride monomer limit < 1.0 ppm to prevent carcinogen leaching into food packaging."}
    ]
    create_pdf(RAW_RAW := RAW_DOCS_DIR / "qco" / "BIS_QCO_Steel_Products_Chemicals_and_Cables_Compendium.pdf", "BIS QCO Steel & Chemicals Compendium", [bis_qco_steel_p1])

    # =========================================================================
    # 9. CATEGORY I: AWARENESS, STANDARDS CLUBS, BOOKLETS, NBC 2016
    # =========================================================================

    # 9.1 Standards Clubs & Youth Outreach
    bis_awar_clubs_p1 = [
        {"type": "title", "text": "BIS STANDARDS CLUBS & EDUCATIONAL OUTREACH MANUAL"},
        {"type": "h1", "text": "YOUTH ENGAGEMENT IN SCHOOLS, COLLEGES & TECHNICAL UNIVERSITIES"},
        {"type": "p", "text": "BIS has established over 10,000 Standards Clubs in high schools and engineering colleges across India to nurture a culture of quality, scientific standardization, and consumer protection among young students."},
        {"type": "h2", "text": "KEY STANDARDS CLUB ACTIVITIES & FINANCIAL SUPPORT"},
        {"type": "bullet", "text": "<b>Financial Grant:</b> BIS provides annual financial grants to each registered school/college club for conducting science and standards learning workshops."},
        {"type": "bullet", "text": "<b>Standards Writing Competitions:</b> Students draft simplified standards for daily classroom objects (pens, desks, school bags, water bottles) to understand clause formulation."},
        {"type": "bullet", "text": "<b>Industrial & Laboratory Exposure Visits:</b> Field trips to BIS Central/Regional laboratories and certified manufacturing factories to witness real-time quality testing."},
        {"type": "bullet", "text": "<b>Door-to-Door Consumer Awareness Campaigns:</b> Student volunteers educate local households on checking HUID on gold jewellery and verifying ISI mark on LPG gas stoves and helmets."}
    ]
    create_pdf(RAW_DOCS_DIR / "awareness" / "BIS_Standards_Clubs_and_Educational_Outreach_Manual.pdf", "BIS Standards Clubs Manual", [bis_awar_clubs_p1])

    # 9.2 National Building Code (NBC 2016)
    bis_nbc_p1 = [
        {"type": "title", "text": "NATIONAL BUILDING CODE OF INDIA (NBC 2016) AWARENESS GUIDE"},
        {"type": "h1", "text": "SPECIAL PUBLICATION SP 7 : 2016 COMPREHENSIVE OVERVIEW"},
        {"type": "p", "text": "The National Building Code of India (NBC 2016), published by BIS, is the authoritative national model code guiding all building construction, architectural planning, structural design, and fire safety regulations adopted by municipal corporations across India."},
        {"type": "h2", "text": "THE 13 PARTS OF NBC 2016"},
        {"type": "table", "data": [
            ["NBC Part Number", "Subject Title", "Key Provisions & Mandates"],
            ["Part 3", "Development Control Rules & General Building Requirements", "FAR/FSI, setback lines, open spaces, parking requirements, barrier-free access for Divyangjan"],
            ["Part 4", "Fire and Life Safety", "Fire prevention, compartmentation, pressurized staircases, automatic sprinklers, smoke evacuation"],
            ["Part 6", "Structural Design (Loads, Earthquake, Concrete, Steel)", "Seismic Zone II to V design (IS 1893), wind load design (IS 875), concrete (IS 456), masonry (IS 1905)"],
            ["Part 8", "Building Services (Lighting, HVAC, Acoustics, Lifts)", "Energy efficient lighting (ECBC compliance), ventilation rates, lift safety codes (IS 14665)"],
            ["Part 9", "Plumbing Services (Water Supply, Drainage, Solid Waste)", "Water supply sizing, rainwater harvesting, dual-flush greywater reuse"],
            ["Part 11", "Approach to Sustainability", "Green building parameters, carbon footprint reduction, recycled construction materials"]
        ], "colWidths": [90, 180, 230]}
    ]
    create_pdf(RAW_DOCS_DIR / "awareness" / "BIS_National_Building_Code_NBC_2016_Awareness_Guide.pdf", "BIS NBC 2016 Awareness Guide", [bis_nbc_p1])

    # 9.3 BIS Milestones and Annual Overview Booklet
    bis_milestones_p1 = [
        {"type": "title", "text": "BIS OVERVIEW, MILESTONES & DIGITAL TRANSFORMATION"},
        {"type": "h1", "text": "HISTORY, STATUTORY EVOLUTION & INTERNATIONAL LEADERSHIP"},
        {"type": "p", "text": "Established on 6 January 1947 as the Indian Standards Institution (ISI), the organization was reconstituted as the Bureau of Indian Standards through the BIS Act, 1986 and further elevated through the landmark Bureau of Indian Standards Act, 2016."},
        {"type": "h2", "text": "KEY HISTORICAL & STATUTORY MILESTONES"},
        {"type": "bullet", "text": "<b>1947:</b> Establishment of Indian Standards Institution (ISI) under Department of Industries."},
        {"type": "bullet", "text": "<b>1955:</b> Launch of the iconic ISI Certification Marks Scheme."},
        {"type": "bullet", "text": "<b>1986:</b> Enactment of first BIS Act, 1986 establishing the Bureau of Indian Standards."},
        {"type": "bullet", "text": "<b>2000:</b> Launch of Gold Hallmarking Scheme for precious jewellery."},
        {"type": "bullet", "text": "<b>2016:</b> Enactment of BIS Act 2016 designating BIS as the National Standards Body of India with powers over services, mandatory QCOs, and hallmarking."},
        {"type": "bullet", "text": "<b>2021:</b> Nationwide rollout of 6-digit Hallmark Unique Identification (HUID) and BIS Care App."},
        {"type": "h2", "text": "INTERNATIONAL ENGAGEMENT (ISO, IEC, SARSO)"},
        {"type": "p", "text": "India is a founding member of the International Organization for Standardization (ISO) and an active member of the International Electrotechnical Commission (IEC). BIS holds permanent representation on the ISO Council and IEC Technical Management Board (TMB)."}
    ]
    create_pdf(RAW_DOCS_DIR / "booklets" / "BIS_Overview_and_Milestones_Annual_Handbook.pdf", "BIS Overview & Milestones Handbook", [bis_milestones_p1])

    print("\n=======================================================")
    print("  Official BIS PDF Knowledge Base Generation Complete!")
    print("=======================================================\n")


if __name__ == "__main__":
    build_all_documents()
