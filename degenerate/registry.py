from degenerate.adapter_gemini import call_gemini
from degenerate.adapter_dev import call_example

MODELS = [
    #{"name": "gemini-3.8-flash", "provider": "gemini", "display_name": "Gemini 3.8 Flash (medium)", "options": {"thinking_level": "medium"} },
    #{"name": "gemini-3.6-flash", "provider": "gemini", "display_name": "Gemini 3.6 Flash (medium)", "options": {"thinking_level": "medium"} },
    {"name": "example", "provider": "dev", "display_name": "Example Author", "options": {"version": "good"} },
    {"name": "example", "provider": "dev", "display_name": "Example Author", "options": {"version": "bad"} }    
]

PROVIDERS = {
    "gemini": call_gemini,
    "dev": call_example
 #   "anthropic": call_anthropic
}
