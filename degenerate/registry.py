import csv
from degenerate.adapters.adapter_dev import call_example
from degenerate.adapters.adapter_anthropic import call_anthropic
from degenerate.adapters.adapter_gemini import call_gemini
from degenerate.adapters.adapter_openai import call_openai
from degenerate.adapters.adapter_openrouter import call_openrouter

DEV_MODELS = [
    {"name": "example_good", "provider": "dev", "display_name": "Example Author (good)", "input_cost":1, "output_cost":1},
    {"name": "example_bad_latex", "provider": "dev", "display_name": "Example Author (invalid LaTeX)", "input_cost":1,"output_cost":1},
    {"name": "example_bad_input", "provider": "dev", "display_name": "Example Author (forbidden LaTeX)", "input_cost":1,"output_cost":1},
    {"name": "example_bad_compile", "provider": "dev", "display_name": "Example Author (bad compile)", "input_cost":1,"output_cost":1},
    {"name": "example_bad_markdown", "provider": "dev", "display_name": "Example Author (bad markdown)", "input_cost":1,"output_cost":1} 
    #{"name": "gemini-3.5-flash-lite", "provider": "gemini", "display_name": "Gemini 3.5 Flash Lite 10 output tokens", "options": {"max_output_tokens": 10}, "input_cost":0.3,"output_cost":2.5 },
    #{"name": "gemini-3.5-flash-lite", "provider": "gemini", "display_name": "Gemini 3.5 Flash Lite 10000 output tokens", "options": {"max_output_tokens": 10000}, "input_cost":0.3, "output_cost":2.5 },
    #{"name": "nvidia/nemotron-3.5-super-vl:free", "provider": "openrouter", "display_name": "Nvidia Nemotron 10 output tokens", "options": {"max_output_tokens": 10} },
    #{"name": "claude-haiku-5-5", "provider": "anthropic", "display_name": "Claude Haiku 10 output tokens", "options": {"max_output_tokens": 10} },
    #{"name": "claude-haiku-5-5", "provider": "anthropic", "display_name": "Claude Haiku 2000 output tokens", "options": {"max_output_tokens": 2000} },
    #{"name": "gpt-6-luna", "provider": "openai", "display_name": "GPT-6 Luna 10 output tokens", "options": {"max_output_tokens": 100} },
    #{"name": "nvidia/nemotron-3.5-super-vl:free", "provider": "openrouter", "display_name": "Nvidia Nemotron 10 output tokens", "options": {"max_output_tokens": 10} },
]

def get_model_registry(file, cost_cutoff):
    registry = []
    primary_fields = ["name", "provider", "display_name"]
    input_tokens = 500
    mil = 1000000.0
    with open(file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            input_cost = float(row["input_cost"])
            output_cost = float(row["output_cost"])
            max_out = int(row["max_output_tokens"])
            cost = input_tokens*input_cost/mil + max_out*output_cost/mil
            if cost < cost_cutoff:
                if row["efforts"] != "":
                    efforts = row["efforts"].split(",")
                    efforts = [e.strip() for e in efforts]
                else:
                    efforts = [None]
                for effort in efforts:   
                    primary = {k:v for k,v in row.items() if k in primary_fields}
                    secondary = { "options": { "effort":effort, "max_output_tokens": max_out} }
                    costs = {"input_cost": input_cost, "output_cost": output_cost, "expected_cost": cost}
                    registry.append(  primary | secondary | costs )
    return registry

def filter_by_cost(registry, lower, upper):
    return [m for m in registry if (m["expected_cost"]>=lower) and (m["expected_cost"]<upper)]
    
def filter_by_provider(registry, provider):
    return [m for m in registry if (m["provider"]==provider)]

def split_models_by_cost(registry, split):
    free = [m for m in registry if (m["expected_cost"]==0.0)]
    cheap = [m for m in registry if (m["expected_cost"]>0.0) & (m["expected_cost"]<split)]
    dear = [m for m in registry if (m["expected_cost"]>=split)]
    return free, cheap, dear
    
PROVIDERS = {
    "dev": call_example,
    "anthropic": call_anthropic,
    "gemini": call_gemini,
    "openai": call_openai,
    "openrouter": call_openrouter
}
