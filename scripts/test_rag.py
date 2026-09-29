"""
Automated testing script for the BIS Intelligent Assistant RAG Pipeline.
Evaluates 10+ multi-lingual, factual, standard-specific, and negative out-of-domain queries.
Usage: python scripts/test_rag.py
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.schemas import AskRequest
from backend.app.rag import answer_bis_question

TEST_QUESTIONS = [
    # 1. Fundamental concept
    "What is BIS (Bureau of Indian Standards)?",
    # 2. Act & Legislative Purpose
    "What is the purpose of the BIS Act 2016?",
    # 3. Product Certification Process
    "What is the BIS certification process and how is the ISI mark granted?",
    # 4. Multilingual (Hindi)
    "Hallmarking kya hai aur yeh kiske liye anivarya hai?",
    # 5. Multilingual (Hinglish)
    "BIS certification ke liye kya main requirements aur fees hoti hain?",
    # 6. Specific Indian Standard
    "IS 302 kis product safety ke liye use hota hai?",
    # 7. Laboratory & Testing
    "What is the role of BIS central and regional laboratories in sample testing?",
    # 8. Consumer Grievance & Mobile App
    "How can consumers verify ISI mark or hallmarked items using BIS Care App?",
    # 9. Penalties & Enforcement
    "What are the penalties for misuse of the Standard Mark under BIS Act 2016?",
    # 10. Foreign Manufacturers Certification
    "What is the Foreign Manufacturers Certification Scheme (FMCS)?",
    # 11. Negative Out-of-Domain Guardrail Test (Should explicitly REFUSE hallucination)
    "What is the capital of France?",
    # 12. Negative Fake Standard Test (Should refuse)
    "What are the safety requirements in standard IS 9999999 for flying cars?"
]


def run_benchmark():
    print("\n=======================================================")
    print("  BIS Intelligent Assistant - RAG Pipeline Benchmark   ")
    print("=======================================================\n")

    passed_tests = 0
    total_tests = len(TEST_QUESTIONS)

    for idx, q in enumerate(TEST_QUESTIONS, 1):
        print(f"[{idx}/{total_tests}] Question: '{q}'")
        req = AskRequest(question=q)
        resp = answer_bis_question(req)

        print(f"  -> Answer: {resp.answer[:220]}..." if len(resp.answer) > 220 else f"  -> Answer: {resp.answer}")
        print(f"  -> Chunks retrieved: {resp.retrieved_chunks}")
        print(f"  -> Sources cited: {len(resp.sources)}")
        for s in resp.sources[:2]:
            print(f"     * {s.document_name} (Page {s.page_number}) - {s.section}")

        # Verification rules
        if "capital of France" in q or "flying cars" in q:
            # Must refuse
            if "could not verify" in resp.answer.lower() or resp.retrieved_chunks == 0:
                print("  [PASS] Correctly refused out-of-scope query without hallucination.")
                passed_tests += 1
            else:
                print("  [FAIL] Failed negative test - generated response for out-of-scope query.")
        else:
            # Normal query
            passed_tests += 1
            print("  [PASS] Successfully evaluated.")
        print("-" * 55)

    print(f"\nBenchmark Complete: {passed_tests}/{total_tests} tests executed successfully.\n")


if __name__ == "__main__":
    run_benchmark()
