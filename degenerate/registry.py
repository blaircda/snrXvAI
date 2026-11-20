from degenerate.adapters.adapter_dev import call_example
from degenerate.adapters.adapter_gemini import call_gemini
from degenerate.adapters.adapter_anthropic import call_anthropic

DEV_MODELS = [
    {"name": "example", "provider": "dev", "display_name": "Example Author (good)", "options": {"variant": "good"} },
    {"name": "example", "provider": "dev", "display_name": "Example Author (invalid LaTeX)", "options": {"variant": "bad_latex"} },
    {"name": "example", "provider": "dev", "display_name": "Example Author (bad compile)", "options": {"variant": "bad_compile"} },
    {"name": "example", "provider": "dev", "display_name": "Example Author (bad markdown)", "options": {"variant": "bad_markdown"} }    
]

GEMINI_MODELS = [
    {"name": "gemini-3.8-flash", "provider": "gemini", "display_name": "Gemini 3.8 Flash (medium)", "options": {"thinking_level": "medium"} },
    {"name": "gemini-3.6-flash", "provider": "gemini", "display_name": "Gemini 3.6 Flash (medium)", "options": {"thinking_level": "medium"} },
]

ANTHROPIC_MODELS = [
    {"name": "claude-haiku-5-5", "provider": "anthropic", "display_name": "Claude Haiku 5.5 (low)", "options": {"effort": "low"} },
]


MODELS = ANTHROPIC_MODELS# + DEV_MODELS + GEMINI_MODELS

PROVIDERS = {
    "dev": call_example,
    "gemini": call_gemini,
    "anthropic": call_anthropic
}
