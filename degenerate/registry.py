from degenerate.adapters.adapter_dev import call_example
from degenerate.adapters.adapter_anthropic import call_anthropic
from degenerate.adapters.adapter_gemini import call_gemini
from degenerate.adapters.adapter_openai import call_openai
from degenerate.adapters.adapter_openrouter import call_openrouter

DEV_MODELS = [
    {"name": "example", "provider": "dev", "display_name": "Example Author (good)", "options": {"variant": "good"} },
    {"name": "example", "provider": "dev", "display_name": "Example Author (invalid LaTeX)", "options": {"variant": "bad_latex"} },
    {"name": "example", "provider": "dev", "display_name": "Example Author (bad compile)", "options": {"variant": "bad_compile"} },
    {"name": "example", "provider": "dev", "display_name": "Example Author (bad markdown)", "options": {"variant": "bad_markdown"} }    
]

GEMINI_MODELS = [
    {"name": "gemini-3.5-flash-lite", "provider": "gemini", "display_name": "Gemini 3.5 Flash Lite (low)", "options": {"thinking_level": "low", "max_output_tokens": 40000} },
    {"name": "gemini-3.8-flash", "provider": "gemini", "display_name": "Gemini 3.8 Flash (medium)", "options": {"thinking_level": "medium", "max_output_tokens": 40000} },
    {"name": "gemini-3.6-flash", "provider": "gemini", "display_name": "Gemini 3.6 Flash (medium)", "options": {"thinking_level": "medium", "max_output_tokens": 40000} },
    {"name": "gemini-4-argon", "provider": "gemini", "display_name": "Gemini 4 Argon (high)", "options": {"thinking_level": "high", "max_output_tokens": 40000} },

]

ANTHROPIC_MODELS = [
    {"name": "claude-haiku-5-5", "provider": "anthropic", "display_name": "Claude Haiku 5.5 (low)", "options": {"effort": "low",  "max_output_tokens": 25000} },
    {"name": "claude-haiku-5-5", "provider": "anthropic", "display_name": "Claude Haiku 5.5 (medium)", "options": {"effort": "medium",  "max_output_tokens": 25000} },
    {"name": "claude-opus-5-5", "provider": "anthropic", "display_name": "Claude Opus 5.5 (high)", "options": {"effort": "high",  "max_output_tokens": 40000} },
]

OPEN_API_MODELS = [
    {"name": "gpt-6-luna", "provider": "openai", "display_name": "GPT 6 Luna (low)", "options": {"effort": "low", "max_output_tokens": 25000} },
    {"name": "gpt-6-luna", "provider": "openai", "display_name": "GPT 6 Luna (high)", "options": {"effort": "high", "max_output_tokens": 25000} },
    {"name": "gpt-6.1-terra", "provider": "openai", "display_name": "GPT 6.1 Terra (medium)", "options": {"effort": "medium", "max_output_tokens": 25000} },
]

OPENROUTER_MODELS = [
    {"name": "particle-ai/particle-1:free", "provider": "openrouter", "display_name": "Particle 1 (free)", "options": {"effort": "medium", "max_output_tokens": 50000}},
    {"name": "baidu/ernie-5.5-flash-preview:free", "provider": "openrouter", "display_name": "Ernie 5.5 (free)", "options": {"effort": "medium", "max_output_tokens": 50000}},
    {"name": "google/gemma-4-26b-a4b-it:free", "provider": "openrouter", "display_name": "Google Gemma 4 26B A4B (free)", "options": {"effort": "medium", "max_output_tokens": 50000}},
    {"name": "google/gemma-4-31b-it:free", "provider": "openrouter", "display_name": "Google: Gemma 4 31B (free)", "options": {"effort": "medium", "max_output_tokens": 50000}},
    {"name": "nvidia/nemotron-3.5-super-vl:free", "provider": "openrouter", "display_name": "NVIDIA: Nemotron 3.5 Super VL (free)", "options": {"effort": "medium", "max_output_tokens": 50000}},
    {"name": "nvidia/nemotron-3-ultra-550b-a55b:free", "provider": "openrouter", "display_name": "NVIDIA: Nemotron 3 Ultra (free)", "options": {"effort": "medium", "max_output_tokens": 50000}},
    {"name": "inclusionai/ling-3.2-flash:free", "provider": "openrouter", "display_name": "inclusionAI: Ling 3.2 Flash (free)", "options": {"effort": "low", "max_output_tokens": 50000}},
    {"name": "recursive/flint-v1.0:free", "provider": "openrouter", "display_name": "Recursive: Flint (free)", "options": {"effort": "medium", "max_output_tokens": 50000}},    
]   

MODELS = OPENROUTER_MODELS+ OPEN_API_MODELS+ ANTHROPIC_MODELS + GEMINI_MODELS

PROVIDERS = {
    "dev": call_example,
    "anthropic": call_anthropic,
    "gemini": call_gemini,
    "openai": call_openai,
    "openrouter": call_openrouter
}
