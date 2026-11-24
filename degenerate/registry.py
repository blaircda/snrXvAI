import csv
from degenerate.adapters.adapter_dev import call_example
from degenerate.adapters.adapter_anthropic import call_anthropic
from degenerate.adapters.adapter_gemini import call_gemini
from degenerate.adapters.adapter_openai import call_openai
from degenerate.adapters.adapter_openrouter import call_openrouter

DEV_MODELS = [
    {"name": "example", "provider": "dev", "display_name": "Example Author (good)", "options": {"variant": "good"} },
    #{"name": "example", "provider": "dev", "display_name": "Example Author (invalid LaTeX)", "options": {"variant": "bad_latex"} },
    #{"name": "example", "provider": "dev", "display_name": "Example Author (forbidden LaTeX)", "options": {"variant": "bad_input"} },
    #{"name": "example", "provider": "dev", "display_name": "Example Author (bad compile)", "options": {"variant": "bad_compile"} },
    #{"name": "example", "provider": "dev", "display_name": "Example Author (bad markdown)", "options": {"variant": "bad_markdown"} }    
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
                    registry.append(  primary | secondary | {"run_cost": cost} )
    return registry

def filter_by_cost(registry, lower, upper):
    return [m for m in registry if (m["run_cost"]>=lower) and (m["run_cost"]<upper)]
    
def filter_by_provider(registry, provider):
    return [m for m in registry if (m["provider"]==provider)]

def split_models_by_cost(registry, split):
    free = [m for m in registry if (m["run_cost"]==0.0)]
    cheap = [m for m in registry if (m["run_cost"]>0.0) & (m["run_cost"]<split)]
    dear = [m for m in registry if (m["run_cost"]>=split)]
    return free, cheap, dear
    
PROVIDERS = {
    "dev": call_example,
    "anthropic": call_anthropic,
    "gemini": call_gemini,
    "openai": call_openai,
    "openrouter": call_openrouter
}
