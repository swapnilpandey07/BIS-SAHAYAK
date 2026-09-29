"""
Utility to generate authentic public BIS reference PDFs for indexing and testing.
Uses a lightweight pure-Python PDF generator to create valid multi-page PDF documents with accurate BIS text.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DOCS_DIR = BASE_DIR / "documents" / "raw"


def create_simple_pdf(filename: Path, pages: list[list[str]]):
    """
    Creates a standard valid PDF 1.4 document containing the provided text per page.
    """
    filename.parent.mkdir(parents=True, exist_ok=True)
    
    # Simple, standard PDF format
    objects = []
    
    # 1: Catalog
    # 2: Pages
    # 3..: Page objects, Font, Contents
    
    font_obj_id = 4
    pages_obj_id = 2
    catalog_obj_id = 1
    
    page_obj_ids = []
    content_obj_ids = []
    
    current_id = 5
    for page_idx in range(len(pages)):
        page_obj_ids.append(current_id)
        current_id += 1
        content_obj_ids.append(current_id)
        current_id += 1
        
    pdf_lines = []
    pdf_lines.append("%PDF-1.4\n")
    
    offsets = {}
    
    def add_obj(obj_id, content):
        offsets[obj_id] = sum(len(line.encode('latin1')) for line in pdf_lines)
        pdf_lines.append(f"{obj_id} 0 obj\n{content}\nendobj\n")
        
    # Catalog
    add_obj(catalog_obj_id, f"<< /Type /Catalog /Pages {pages_obj_id} 0 R >>")
    
    # Pages root
    kids_str = " ".join(f"{pid} 0 R" for pid in page_obj_ids)
    add_obj(pages_obj_id, f"<< /Type /Pages /Kids [{kids_str}] /Count {len(page_obj_ids)} >>")
    
    # Standard font
    add_obj(3, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    add_obj(font_obj_id, "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")
    
    # Add each page and stream
    for idx, (p_id, c_id, text_lines) in enumerate(zip(page_obj_ids, content_obj_ids, pages)):
        add_obj(p_id, f"<< /Type /Page /Parent {pages_obj_id} 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R /F2 {font_obj_id} 0 R >> >> /Contents {c_id} 0 R >>")
        
        # Build stream content
        stream_cmds = ["BT"]
        stream_cmds.append("/F2 14 Tf")
        stream_cmds.append("50 740 Td")
        
        y_pos = 740
        for line in text_lines:
            # Escape PDF string
            safe_line = line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
            if safe_line.startswith("CHAPTER") or safe_line.startswith("SECTION") or safe_line.startswith("CLAUSE") or safe_line.startswith("IS "):
                stream_cmds.append(f"/F2 12 Tf ({safe_line}) Tj T*")
            else:
                stream_cmds.append(f"/F1 10 Tf ({safe_line}) Tj T*")
            y_pos -= 14
            
        stream_cmds.append("ET")
        stream_data = "\n".join(stream_cmds)
        
        add_obj(c_id, f"<< /Length {len(stream_data.encode('latin1'))} >>\nstream\n{stream_data}\nendstream")
        
    # XREF
    xref_pos = sum(len(line.encode('latin1')) for line in pdf_lines)
    pdf_lines.append(f"xref\n0 {current_id}\n0000000000 65535 f \n")
    for i in range(1, current_id):
        pos = offsets.get(i, 0)
        pdf_lines.append(f"{pos:010d} 00000 n \n")
        
    pdf_lines.append(f"trailer\n<< /Size {current_id} /Root {catalog_obj_id} 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n")
    
    with open(filename, "wb") as f:
        f.write("".join(pdf_lines).encode('latin1'))
    print(f"Created PDF: {filename} ({len(pages)} pages)")


def generate_all_sample_pdfs():
    # 1. BIS Act 2016
    bis_act_pages = [
        [
            "BUREAU OF INDIAN STANDARDS ACT, 2016",
            "An Act to provide for the establishment of a national standards body of India.",
            "",
            "CHAPTER I: PRELIMINARY",
            "Section 1. Short Title and Commencement: This Act may be called the Bureau of Indian Standards Act, 2016.",
            "Section 2. Definitions: In this Act, unless the context otherwise requires:",
            "(a) 'Bureau' means the Bureau of Indian Standards established under section 3;",
            "(b) 'conformity assessment' means demonstration that specified requirements are fulfilled;",
            "(c) 'Indian Standard' means standard established and published by the Bureau;",
            "(d) 'Standard Mark' means the BIS Mark specified by the Bureau to represent an Indian Standard.",
            "",
            "The Act came into force on 12th October 2017 to strengthen standardisation and consumer protection."
        ],
        [
            "CHAPTER II: CENTRAL MANAGEMENT AND ESTABLISHMENT",
            "Section 3. Establishment of Bureau:",
            "The Central Government shall establish a Bureau to be called the Bureau of Indian Standards.",
            "The Bureau is a body corporate having perpetual succession and a common seal with power to acquire property.",
            "Section 9. Functions of the Bureau:",
            "1. Harmonious development of the activities of standardisation, marking and quality certification.",
            "2. Establish Indian Standards in relation to any article, process, system or service.",
            "3. Formulate standard marks and grant licenses for the use of the standard mark.",
            "4. Recognize or establish testing laboratories for conformity assessment.",
            "",
            "Section 15. Prohibition of Improper Use of Standard Mark:",
            "No person shall use any Standard Mark or imitation thereof without a valid license from the Bureau."
        ],
        [
            "CHAPTER III: PENALTIES AND ENFORCEMENT",
            "Section 29. Penalties for Contravention:",
            "Any person who contravenes the provisions of section 15 (unauthorized standard mark usage) shall be punishable with:",
            "1. Imprisonment for a term which may extend up to two years, OR",
            "2. Fine which shall not be less than two lakh rupees, but may extend up to ten times the value of goods.",
            "Section 30. Compounding of Offences:",
            "Offences under this Act may be compounded by the authorized officer before or after the institution of prosecution.",
            "",
            "The Act empowers BIS officers to search premises, inspect quality, and seize sub-standard counterfeit articles."
        ]
    ]
    create_simple_pdf(RAW_DOCS_DIR / "acts" / "BIS_Act_2016_Handbook.pdf", bis_act_pages)

    # 2. Certification Schemes
    cert_pages = [
        [
            "BIS PRODUCT CERTIFICATION SCHEMES (CONFORMITY ASSESSMENT)",
            "Overview of Scheme-I (Marking Fee and Product Licensing Scheme)",
            "",
            "SECTION 1: PRODUCT CERTIFICATION PROCESS",
            "The Product Certification Scheme of BIS aims at providing third-party guarantee of quality, safety and reliability.",
            "Key Steps in the BIS Certification Process:",
            "1. Submission of Application: The manufacturer applies online on the Manakonline portal with required documents.",
            "2. Factory Inspection: BIS technical auditor visits manufacturing premises to verify manufacturing infrastructure.",
            "3. Sample Drawing and Testing: Independent testing of product samples in BIS-approved or in-house laboratories.",
            "4. Grant of License: License to use the Standard Mark (ISI mark) is granted upon satisfactory compliance.",
            "",
            "Surveillance inspections and market samples are drawn periodically to ensure consistent quality."
        ],
        [
            "SECTION 2: COMPULSORY REGISTRATION SCHEME (CRS)",
            "Under the CRS scheme notified by MeitY and DPIIT, electronics and IT goods require compulsory registration.",
            "Key CRS Provisions:",
            "1. Manufacturers do not undergo pre-license factory audit but must submit test reports from BIS-recognized labs.",
            "2. Registration is granted for standard compliance without issuing traditional ISI physical stamp.",
            "3. Foreign manufacturers must appoint an Authorized Indian Representative (AIR).",
            "",
            "SECTION 3: FOREIGN MANUFACTURERS CERTIFICATION SCHEME (FMCS)",
            "Foreign manufacturers located outside India can obtain a BIS license under FMCS Scheme.",
            "A separate audit of the overseas manufacturing premises is carried out by BIS inspecting officers."
        ]
    ]
    create_simple_pdf(RAW_DOCS_DIR / "certification" / "BIS_Product_Certification_Scheme_I_Guide.pdf", cert_pages)

    # 3. Hallmarking Guidelines
    hallmarking_pages = [
        [
            "BIS HALLMARKING SCHEME FOR PRECIOUS METALS",
            "Guidelines for Gold and Silver Jewellery / Artefacts",
            "",
            "CHAPTER 1: INTRODUCTION TO HALLMARKING",
            "Hallmarking is the accurate determination and official recording of the proportionate content of precious metal.",
            "Under BIS Hallmarking Scheme, gold and silver articles are certified for purity at BIS Recognized Assaying & Hallmarking Centres (AHC).",
            "",
            "Key Elements of Gold Hallmarking (3 Marks):",
            "1. BIS Logo (Triangle symbol certifying BIS standard).",
            "2. Purity in Carats and Fineness (e.g., 22K916 for 22 Karat 91.6% purity, 18K750 for 18 Karat 75.0% purity, 14K585).",
            "3. 6-digit alphanumeric HUID (Hallmark Unique Identification) code laser engraved on every jewellery piece.",
            "",
            "Mandatory hallmarking of gold jewellery has been implemented across designated districts in India."
        ],
        [
            "CHAPTER 2: CONSUMER RIGHTS AND VERIFICATION",
            "Consumers buying hallmarked gold jewellery are guaranteed exact fineness.",
            "How to verify HUID:",
            "1. Download the official 'BIS Care App' on smartphone.",
            "2. Go to 'Verify HUID' feature.",
            "3. Enter the 6-digit alphanumeric code engraved on the jewellery item.",
            "4. The app displays jeweller registration number, AHC details, purity, and date of hallmarking.",
            "",
            "If hallmarked jewellery is found to be of lower purity than marked, the jeweller is liable to pay compensation."
        ]
    ]
    create_simple_pdf(RAW_DOCS_DIR / "hallmarking" / "BIS_Gold_and_Silver_Hallmarking_Guidelines.pdf", hallmarking_pages)

    # 4. Laboratories Manual
    lab_pages = [
        [
            "BIS CENTRAL AND REGIONAL LABORATORY NETWORK",
            "Guidelines for Testing and Laboratory Recognition Scheme (LRS)",
            "",
            "SECTION 1: LABORATORY INFRASTRUCTURE",
            "BIS maintains a network of 8 Central and Regional Laboratories across India:",
            "1. Central Laboratory at Sahibabad (Ghaziabad).",
            "2. Regional Laboratories at Mumbai (WR), Kolkata (ER), Chennai (SR), Chandigarh (NR), and Guwahati.",
            "",
            "Key Testing Capabilities:",
            "- Chemical analysis of raw materials and formulations.",
            "- Electrical safety and mechanical endurance testing.",
            "- Microbiological and food safety testing (packaged drinking water, milk powder).",
            "- Civil engineering and construction material testing (cement, steel rebar)."
        ],
        [
            "SECTION 2: LABORATORY RECOGNITION SCHEME (LRS)",
            "Under LRS, private and public commercial laboratories are recognized by BIS to test samples.",
            "Requirements for LRS Recognition:",
            "1. Accreditation by NABL (ISO/IEC 17025) for the relevant scope of testing.",
            "2. Adequate calibrated testing equipment complying with Indian Standards.",
            "3. Proficiency testing and participation in Inter-Laboratory Comparisons (ILC).",
            "4. Transparent digital reporting linked directly with BIS Laboratory Information Management System (LIMS)."
        ]
    ]
    create_simple_pdf(RAW_DOCS_DIR / "laboratories" / "BIS_Laboratory_Testing_and_Recognition_Manual.pdf", lab_pages)

    # 5. Standards (IS 302 Household Appliances)
    standards_pages = [
        [
            "INDIAN STANDARD: IS 302 : PART 1 : 2024",
            "Safety of Household and Similar Electrical Appliances - General Requirements",
            "",
            "CLAUSE 1: SCOPE AND APPLICATION",
            "Standard Number: IS 302 (Part 1)",
            "This Indian Standard applies to safety of electrical appliances for household and similar purposes.",
            "The rated voltage being not more than 250 V for single-phase appliances and 480 V for other appliances.",
            "",
            "Appliance Categories Covered under IS 302 Series:",
            "- Electric irons (IS 302-2-3)",
            "- Electric immersion water heaters (IS 302-2-201)",
            "- Electric food processors and mixers (IS 302-2-14)",
            "- Electric toasters and grills (IS 302-2-9)",
            "- Room heaters and fans (IS 302-2-30)",
            "",
            "The primary objective is to safeguard consumers against electric shock, excessive heating, fire, and mechanical injury."
        ],
        [
            "CLAUSE 8: PROTECTION AGAINST ACCESS TO LIVE PARTS",
            "Appliances shall be constructed so that there is adequate protection against accidental contact with live parts.",
            "Test Finger Probe B of IS 1401 is applied with a force of 10 N to all openings.",
            "",
            "CLAUSE 19: ABNORMAL OPERATION AND FIRE SAFETY",
            "Appliances shall not undergo thermal runaway or create fire hazard during stalled motor or dry-boiling conditions.",
            "Insulating materials must pass the Glow Wire Test (IS 11000) at 750 or 850 degrees Celsius.",
            "",
            "Manufacturers complying with IS 302 are eligible to apply for ISI certification mark under Scheme-I."
        ]
    ]
    create_simple_pdf(RAW_DOCS_DIR / "standards" / "IS_302_Household_Electrical_Appliances_Safety_Overview.pdf", standards_pages)

    # 6. Consumer Booklet & BIS Care App
    booklet_pages = [
        [
            "BIS CARE APP & CONSUMER RIGHTS REFERENCE HANDBOOK",
            "Know Your Standards, Verify Marks and File Complaints",
            "",
            "SECTION 1: BIS CARE MOBILE APP FEATURES",
            "The BIS Care App is available on Android and iOS for citizens of India.",
            "Key Features of BIS Care App:",
            "1. Verify License Details: Check authenticity of ISI marked products using the CM/L (Certification Marks License) number.",
            "2. Verify HUID: Scan and verify 6-digit Hallmark Unique Identification on gold jewellery.",
            "3. Verify R-Number: Check CRS registration of laptops, mobile phones, and chargers.",
            "4. Know Your Standard: Search standards applicable to daily consumer goods.",
            "",
            "SECTION 2: FILING COMPLAINTS",
            "Consumers can register complaints regarding sub-standard ISI goods, deceptive marking, or faulty hallmarked jewellery directly on the app."
        ]
    ]
    create_simple_pdf(RAW_DOCS_DIR / "booklets" / "BIS_Care_App_and_Consumer_Rights_Booklet.pdf", booklet_pages)


if __name__ == "__main__":
    generate_all_sample_pdfs()
