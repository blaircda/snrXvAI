from degenerate.adapter_gemini import call_gemini

MODELS = [
    {"name": "gemini-3.8-flash", "provider": "gemini", "author": "Gemini 3.8 Flash (medium)", "options": {"thinking_level": "medium"} },
    {"name": "gemini-3.6-flash", "provider": "gemini", "author": "Gemini 3.6 Flash (medium)", "options": {"thinking_level": "medium"} }    
]

PROVIDERS = {
    "gemini": call_gemini,
 #   "anthropic": call_anthropic
}
