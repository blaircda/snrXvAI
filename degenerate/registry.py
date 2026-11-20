from degenerate.adapters.adapter_gemini import call_gemini
from degenerate.adapters.adapter_dev import call_example

MODELS = [
    #{"name": "gemini-3.8-flash", "provider": "gemini", "display_name": "Gemini 3.8 Flash (medium)", "options": {"thinking_level": "medium"} },
    #{"name": "gemini-3.6-flash", "provider": "gemini", "display_name": "Gemini 3.6 Flash (medium)", "options": {"thinking_level": "medium"} },
    {"name": "example", "provider": "dev", "display_name": "Example Author (good)", "options": {"variant": "good"} },
    #{"name": "example", "provider": "dev", "display_name": "Example Author (invalid LaTeX)", "options": {"variant": "bad_latex"} },
    #{"name": "example", "provider": "dev", "display_name": "Example Author (bad compile)", "options": {"variant": "bad_compile"} },
    {"name": "example", "provider": "dev", "display_name": "Example Author (bad markdown)", "options": {"variant": "bad_markdown"} }    

]

PROVIDERS = {
    "gemini": call_gemini,
    "dev": call_example
 #   "anthropic": call_anthropic
}
