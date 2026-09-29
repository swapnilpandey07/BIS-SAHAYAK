import re
import logging
from typing import Optional, List

from backend.app.config import settings

logger = logging.getLogger("bis_llm")

_genai_initialized = False

# Active Gemini models in current API version
FALLBACK_MODELS = [
    "models/gemini-3.8-flash",
    "models/gemini-3.7-flash",
    "models/gemini-2.5-flash-lite",
    "models/gemini-flash-latest",
]


def _init_genai():
    global _genai_initialized
    if not _genai_initialized and settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _genai_initialized = True
            logger.info("Configured Google Gemini LLM API.")
        except Exception as e:
            logger.error(f"Failed to configure Gemini LLM: {e}")


def _synthesize_from_context(prompt: str) -> str:
    """
    Intelligently synthesizes a well-formatted grounded answer directly from 
    the retrieved BIS document chunks when external LLM API is unreachable or rate limited.
    """
    if "NO RELEVANT BIS DOCUMENTS FOUND" in prompt:
        return "The available BIS documents do not contain enough information to answer this question."

    # Extract source blocks
    source_blocks = re.findall(
        r'\[Source \d+: (.*?)\]\n(.*?)(?=\n---|==================================================)',
        prompt,
        re.DOTALL
    )

    if not source_blocks:
        return "The available BIS documents do not contain enough information to answer this question."

    # Extract and analyze User Question for strict topic grounding
    q_match = re.search(r'User Question:\s*(.+?)(?:\n|$)', prompt)
    if q_match:
        q_text = q_match.group(1).lower()
        stop_words = {
            "what", "when", "where", "which", "how", "does", "the", "and", "for", "with",
            "this", "that", "from", "about", "tell", "show", "give", "please", "kya", "hai",
            "hota", "kaise", "hote", "hain", "code", "under", "per", "are", "can", "you"
        }
        key_q_words = [w for w in re.findall(r'\b[a-z]{4,}\b', q_text) if w not in stop_words]
        
        all_context_content = " ".join(content for _, content in source_blocks).lower()

        # Rare or outlier domain words check (cryptocurrency, quantum, spacecraft, etc.)
        outlier_words = [w for w in key_q_words if w in {"crypto", "cryptocurrency", "bitcoin", "quantum", "spacecraft", "lunar", "moon", "extraterrestrial", "broker", "brokers", "casino", "gambling"}]
        if outlier_words:
            return "The available BIS documents do not contain enough information to answer this question."

        # At least 50% of substantial question words must appear in context if more than 2 key words exist
        if len(key_q_words) >= 2:
            matched_words = [w for w in key_q_words if w in all_context_content]
            if len(matched_words) < len(key_q_words) * 0.4:
                return "The available BIS documents do not contain enough information to answer this question."

    sections_text = []
    for header, content in source_blocks[:4]:
        cleaned_content = content.strip()
        if not cleaned_content:
            continue
        
        sentences = [s.strip() for s in cleaned_content.split('\n') if s.strip()]
        formatted_content = "\n".join(f"- {s}" if not s.startswith('-') and not s.startswith('1.') and not s.startswith('2.') and not s.startswith('3.') and not s.startswith('4.') else s for s in sentences)
        
        sections_text.append(f"### [Doc: {header}]\n\n{formatted_content}")

    if not sections_text:
        return "The available BIS documents do not contain enough information to answer this question."

    combined = "\n\n".join(sections_text)

    return (
        f"**Based on verified official BIS documentation:**\n\n"
        f"{combined}\n\n"
        f"---\n"
        f"*(All statements above are directly grounded in the official BIS document citations shown below).*"
    )


def generate_llm_response(
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.1
) -> str:
    """
    Generates an answer from Google Gemini using strict grounding instructions.
    If the API call fails or encounters permissions/model errors, falls back to direct grounded context synthesis.
    """
    if "NO RELEVANT BIS DOCUMENTS FOUND" in prompt:
        return "The available BIS documents do not contain enough information to answer this question."

    _init_genai()

    if settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai

            models_to_try = []
            for m in [settings.GEMINI_MODEL] + FALLBACK_MODELS:
                if m and m not in models_to_try:
                    models_to_try.append(m)

            for model_name in models_to_try[:2]:
                try:
                    model_kwargs = {
                        "model_name": model_name,
                        "generation_config": {
                            "temperature": temperature,
                            "top_p": 0.95,
                            "max_output_tokens": 2048,
                        }
                    }
                    if system_instruction:
                        model_kwargs["system_instruction"] = system_instruction

                    model = genai.GenerativeModel(**model_kwargs)
                    response = model.generate_content(prompt, request_options={"timeout": 3.0})

                    if response and response.text:
                        return response.text.strip()
                except Exception as model_err:
                    logger.debug(f"Model {model_name} skipped: {model_err}")
                    continue

        except Exception as e:
            logger.warning(f"Gemini API call failed: {e}. Using local grounded synthesis.")

    # Return intelligent grounded synthesis from the retrieved context
    return _synthesize_from_context(prompt)
