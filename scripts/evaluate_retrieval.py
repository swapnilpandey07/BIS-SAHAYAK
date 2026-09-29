"""
Comprehensive BIS RAG Search Quality & Grounding Evaluation Suite
Tests retrieval accuracy, top-5 hit rate, MRR, multilingual understanding (English, Hindi, Hinglish),
and strict anti-hallucination / insufficient-context guardrails.
"""

import sys
import logging
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.retrieval import retrieve_relevant_chunks
from backend.app.rag import answer_bis_question
from backend.app.schemas import AskRequest

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")


# 35 Comprehensive Evaluation Questions
TEST_BENCHMARK = [
    # -------------------------------------------------------------
    # 1. Basic BIS Questions (10)
    # -------------------------------------------------------------
    {
        "id": "BASIC-01",
        "question": "What is the Bureau of Indian Standards (BIS) and when was the BIS Act 2016 enacted?",
        "expected_categories": ["acts", "booklets"],
        "expected_doc_keywords": ["BIS_Act_2016", "Overview", "Handbook"],
        "group": "Basic BIS"
    },
    {
        "id": "BASIC-02",
        "question": "What are the main functions and statutory powers of BIS under Section 9 of the BIS Act 2016?",
        "expected_categories": ["acts"],
        "expected_doc_keywords": ["BIS_Act_2016"],
        "group": "Basic BIS"
    },
    {
        "id": "BASIC-03",
        "question": "Who serves as the ex-officio President and Member-Secretary of BIS according to BIS Rules 2018?",
        "expected_categories": ["rules"],
        "expected_doc_keywords": ["BIS_Rules_2018"],
        "group": "Basic BIS"
    },
    {
        "id": "BASIC-04",
        "question": "What are the 15 Division Councils of BIS responsible for standardization?",
        "expected_categories": ["standards"],
        "expected_doc_keywords": ["Standardization_Process"],
        "group": "Basic BIS"
    },
    {
        "id": "BASIC-05",
        "question": "What are the 6 stages involved in the formulation of an Indian Standard?",
        "expected_categories": ["standards"],
        "expected_doc_keywords": ["Standardization_Process"],
        "group": "Basic BIS"
    },
    {
        "id": "BASIC-06",
        "question": "What is the National Building Code of India (NBC 2016) and what is its Special Publication number?",
        "expected_categories": ["awareness"],
        "expected_doc_keywords": ["National_Building_Code"],
        "group": "Basic BIS"
    },
    {
        "id": "BASIC-07",
        "question": "What are BIS Standards Clubs and what support does BIS provide to schools and colleges?",
        "expected_categories": ["awareness"],
        "expected_doc_keywords": ["Standards_Clubs"],
        "group": "Basic BIS"
    },
    {
        "id": "BASIC-08",
        "question": "What penalties are prescribed under Section 29 of the BIS Act 2016 for unauthorized use of Standard Mark?",
        "expected_categories": ["acts"],
        "expected_doc_keywords": ["BIS_Act_2016", "Enforcement"],
        "group": "Basic BIS"
    },
    {
        "id": "BASIC-09",
        "question": "When was the Indian Standards Institution (ISI) originally established?",
        "expected_categories": ["booklets"],
        "expected_doc_keywords": ["Overview_and_Milestones"],
        "group": "Basic BIS"
    },
    {
        "id": "BASIC-10",
        "question": "What international standardization bodies is BIS a member of?",
        "expected_categories": ["booklets", "acts", "standards"],
        "expected_doc_keywords": ["Overview_and_Milestones", "Standardization_Process", "BIS_Act_2016", "ISO"],
        "group": "Basic BIS"
    },

    # -------------------------------------------------------------
    # 2. Product Certification Questions (5)
    # -------------------------------------------------------------
    {
        "id": "CERT-01",
        "question": "How does Scheme-I product certification work and what is the difference between Option 1 and Option 2?",
        "expected_categories": ["certification", "regulations"],
        "expected_doc_keywords": ["Product_Certification_Scheme_I", "Conformity_Assessment"],
        "group": "Certification"
    },
    {
        "id": "CERT-02",
        "question": "What is the Compulsory Registration Scheme (CRS) for electronics and IT goods under Scheme-II?",
        "expected_categories": ["certification"],
        "expected_doc_keywords": ["Compulsory_Registration_Scheme_CRS"],
        "group": "Certification"
    },
    {
        "id": "CERT-03",
        "question": "What are the requirements for foreign manufacturers under FMCS scheme and who is an AIR?",
        "expected_categories": ["certification"],
        "expected_doc_keywords": ["Foreign_Manufacturers", "FMCS"],
        "group": "Certification"
    },
    {
        "id": "CERT-04",
        "question": "What fee concessions and rebates does BIS offer to MSMEs, Startups, and Women Entrepreneurs?",
        "expected_categories": ["certification"],
        "expected_doc_keywords": ["MSME", "Startups"],
        "group": "Certification"
    },
    {
        "id": "CERT-05",
        "question": "What is Scheme-IV batch certification and when is a Certificate of Conformity (CoC) issued?",
        "expected_categories": ["certification"],
        "expected_doc_keywords": ["Scheme_IV_Batch"],
        "group": "Certification"
    },

    # -------------------------------------------------------------
    # 3. Hallmarking Questions (5)
    # -------------------------------------------------------------
    {
        "id": "HALL-01",
        "question": "What are the 3 mandatory marks on hallmarked gold jewellery in India?",
        "expected_categories": ["hallmarking"],
        "expected_doc_keywords": ["Hallmarking_Guidelines", "Gold"],
        "group": "Hallmarking"
    },
    {
        "id": "HALL-02",
        "question": "What is HUID in gold jewellery and how can a consumer verify it on the BIS Care App?",
        "expected_categories": ["hallmarking", "consumer"],
        "expected_doc_keywords": ["Hallmarking_Guidelines", "Jeweller_Registration", "Care_App"],
        "group": "Hallmarking"
    },
    {
        "id": "HALL-03",
        "question": "What are the official statutory hallmarking charges per article for gold and silver jewellery?",
        "expected_categories": ["regulations", "hallmarking"],
        "expected_doc_keywords": ["Hallmarking_Regulations", "Hallmarking_Guidelines"],
        "group": "Hallmarking"
    },
    {
        "id": "HALL-04",
        "question": "What is the compensation formula for a consumer if hallmarked jewellery is found of lower purity?",
        "expected_categories": ["regulations", "hallmarking"],
        "expected_doc_keywords": ["Hallmarking_Regulations", "Hallmarking_Guidelines", "Consumer_Protection", "Hallmarking"],
        "group": "Hallmarking"
    },
    {
        "id": "HALL-05",
        "question": "What gold purity grades are officially permitted for hallmarking under IS 1417?",
        "expected_categories": ["hallmarking"],
        "expected_doc_keywords": ["Hallmarking_Guidelines", "Gold_and_Silver"],
        "group": "Hallmarking"
    },

    # -------------------------------------------------------------
    # 4. Quality Control Orders (QCO) Questions (5)
    # -------------------------------------------------------------
    {
        "id": "QCO-01",
        "question": "What is a Quality Control Order (QCO) under Section 16 of the BIS Act 2016?",
        "expected_categories": ["qco", "acts"],
        "expected_doc_keywords": ["Quality_Control_Orders", "BIS_Act_2016"],
        "group": "QCO"
    },
    {
        "id": "QCO-02",
        "question": "What Indian Standards are mandatory for toys under the Toys (Quality Control) Order?",
        "expected_categories": ["qco", "standards"],
        "expected_doc_keywords": ["Toys", "IS_9873"],
        "group": "QCO"
    },
    {
        "id": "QCO-03",
        "question": "Which footwear standards are covered under the Footwear Quality Control Orders?",
        "expected_categories": ["qco"],
        "expected_doc_keywords": ["Toys_Safety_and_Footwear", "Quality_Control_Orders"],
        "group": "QCO"
    },
    {
        "id": "QCO-04",
        "question": "What are the requirements under the Steel and Steel Products Quality Control Order?",
        "expected_categories": ["qco", "standards"],
        "expected_doc_keywords": ["Steel", "IS_1786"],
        "group": "QCO"
    },
    {
        "id": "QCO-05",
        "question": "What exemptions or timeline extensions do MSMEs receive under recent Quality Control Orders?",
        "expected_categories": ["qco"],
        "expected_doc_keywords": ["Quality_Control_Orders"],
        "group": "QCO"
    },

    # -------------------------------------------------------------
    # 5. Document-Specific & Standard Number Questions (5)
    # -------------------------------------------------------------
    {
        "id": "DOC-01",
        "question": "What are the safety requirements and leakage current limits under IS 302 Part 1 for electrical appliances?",
        "expected_categories": ["standards"],
        "expected_doc_keywords": ["IS_302", "Household_Electrical"],
        "group": "Document-Specific"
    },
    {
        "id": "DOC-02",
        "question": "What are the yield strength and tensile strength requirements for Fe 500D rebar under IS 1786?",
        "expected_categories": ["standards", "handbooks"],
        "expected_doc_keywords": ["IS_1786", "Building_Materials"],
        "group": "Document-Specific"
    },
    {
        "id": "DOC-03",
        "question": "What are the energy efficiency loss levels for distribution transformers under IS 1180 Part 1?",
        "expected_categories": ["handbooks"],
        "expected_doc_keywords": ["Electrical_Engineering", "Transformers"],
        "group": "Document-Specific"
    },
    {
        "id": "DOC-04",
        "question": "What standards govern Artificial Intelligence (IS/ISO/IEC 22989, 42001) and Software Testing (IS 29119)?",
        "expected_categories": ["handbooks"],
        "expected_doc_keywords": ["AI_IoT", "Software_Testing"],
        "group": "Document-Specific"
    },
    {
        "id": "DOC-05",
        "question": "What testing disciplines are handled at the BIS Central Laboratory in Sahibabad, Ghaziabad?",
        "expected_categories": ["laboratories"],
        "expected_doc_keywords": ["Central_and_Regional_Laboratories", "Laboratory"],
        "group": "Document-Specific"
    },

    # -------------------------------------------------------------
    # 6. Multilingual Questions (Hindi & Hinglish) (3)
    # -------------------------------------------------------------
    {
        "id": "MULTI-01",
        "question": "सोने के गहनों पर हॉलमार्क में HUID कोड क्या होता है और इसे कैसे चेक करें?",
        "expected_categories": ["hallmarking", "consumer"],
        "expected_doc_keywords": ["Hallmarking", "Care_App"],
        "group": "Multilingual"
    },
    {
        "id": "MULTI-02",
        "question": "ISI mark kaise milta hai aur Scheme 1 me kya steps hote hain?",
        "expected_categories": ["certification"],
        "expected_doc_keywords": ["Product_Certification", "Scheme_I"],
        "group": "Multilingual"
    },
    {
        "id": "MULTI-03",
        "question": "QCO kya hota hai aur iska violation karne par kya penalty lagti hai?",
        "expected_categories": ["qco", "acts"],
        "expected_doc_keywords": ["Quality_Control_Orders", "BIS_Act_2016"],
        "group": "Multilingual"
    },

    # -------------------------------------------------------------
    # 7. Strict Grounding / Insufficient-Context Test (2)
    # -------------------------------------------------------------
    {
        "id": "GUARD-01",
        "question": "What is the official BIS standard for extraterrestrial spacecraft lunar landing modules (IS 999999)?",
        "expected_categories": [],
        "expected_doc_keywords": [],
        "group": "Guardrail (Negative Test)"
    },
    {
        "id": "GUARD-02",
        "question": "What is the secret licensing fee discount code for private quantum cryptocurrency brokers?",
        "expected_categories": [],
        "expected_doc_keywords": [],
        "group": "Guardrail (Negative Test)"
    }
]


def run_retrieval_benchmarks():
    print("\n==========================================================================")
    print("      BIS Intelligent Assistant — Comprehensive Evaluation Benchmark")
    print("==========================================================================\n")

    total_tests = len(TEST_BENCHMARK)
    top1_hits = 0
    top5_hits = 0
    reciprocal_ranks = []
    category_matches = 0
    guardrail_passes = 0
    guardrail_total = 0

    for idx, test in enumerate(TEST_BENCHMARK, 1):
        t_id = test["id"]
        query = test["question"]
        expected_cats = test["expected_categories"]
        expected_kw = test["expected_doc_keywords"]
        group = test["group"]

        if group == "Guardrail (Negative Test)":
            guardrail_total += 1
            chunks, citations = retrieve_relevant_chunks(query, top_k=5)
            ans_obj = answer_bis_question(AskRequest(question=query))
            
            # Guardrail passes if no chunks returned or answer states unverified/refusal
            is_refused = (
                len(chunks) == 0 or
                "could not verify" in ans_obj.answer.lower() or
                "not contain enough information" in ans_obj.answer.lower()
            )
            if is_refused:
                guardrail_passes += 1
                status = "PASSED (Grounding Refusal Correct)"
            else:
                status = "FAILED (Hallucination risk detected)"

            print(f"[{idx:02d}/{total_tests:02d}] [{t_id}] ({group}) -> {status}")
            continue

        # Standard Retrieval Test
        chunks, citations = retrieve_relevant_chunks(query, top_k=5)

        matched_rank = None
        for r_idx, c in enumerate(chunks, 1):
            doc_name = c.get("document_name", "")
            title = c.get("title", "")
            cat = c.get("category", "")

            # Check if any expected keyword in doc_name or title
            kw_hit = any(kw.lower() in doc_name.lower() or kw.lower() in title.lower() for kw in expected_kw)
            if kw_hit:
                matched_rank = r_idx
                break

        # Check category match
        if chunks:
            top_cat = chunks[0].get("category", "")
            if any(ec.lower() == top_cat.lower() for ec in expected_cats):
                category_matches += 1

        if matched_rank == 1:
            top1_hits += 1
            top5_hits += 1
            reciprocal_ranks.append(1.0)
            status_str = "Top-1 HIT"
        elif matched_rank and matched_rank <= 5:
            top5_hits += 1
            reciprocal_ranks.append(1.0 / matched_rank)
            status_str = f"Top-{matched_rank} HIT"
        else:
            reciprocal_ranks.append(0.0)
            status_str = "MISS"

        top_doc = chunks[0].get("title", "None") if chunks else "None"
        print(f"[{idx:02d}/{total_tests:02d}] [{t_id}] ({group}) -> {status_str} | Retrieved Top: {top_doc[:45]}...")

    # Compute Aggregate Metrics
    active_tests = total_tests - guardrail_total
    hit_at_1_rate = (top1_hits / active_tests) * 100 if active_tests else 0
    hit_at_5_rate = (top5_hits / active_tests) * 100 if active_tests else 0
    mrr = (sum(reciprocal_ranks) / len(reciprocal_ranks)) if reciprocal_ranks else 0
    guardrail_rate = (guardrail_passes / guardrail_total) * 100 if guardrail_total else 100

    print("\n--------------------------------------------------------------------------")
    print(f"Total Test Questions Evaluated:  {total_tests}")
    print(f"Retrieval Tests Evaluated:       {active_tests}")
    print(f"Top-1 Hit Rate:                  {hit_at_1_rate:.1f}% ({top1_hits}/{active_tests})")
    print(f"Top-5 Hit Rate:                  {hit_at_5_rate:.1f}% ({top5_hits}/{active_tests})")
    print(f"Mean Reciprocal Rank (MRR):      {mrr:.3f}")
    print(f"Anti-Hallucination Guardrail:    {guardrail_rate:.1f}% ({guardrail_passes}/{guardrail_total} passed)")
    print("--------------------------------------------------------------------------\n")


if __name__ == "__main__":
    run_retrieval_benchmarks()
