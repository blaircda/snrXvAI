from dotenv import load_dotenv
import time, random
from google import genai
from google.genai import _interactions_errors as gerr

load_dotenv()
client = genai.Client()

# define some error classes
class GenerationError(Exception): 
    """Paper generation failed"""
class TransientError(GenerationError):
    """Temporary failure: retry"""
class ConfigError(GenerationError):    
    """Gave wrong input to model calls: do not retry"""
class OutputError(GenerationError):
    """Output returned is unusable"""

# define a retrying function - may not need
def with_retries(f, max_attempts = 2):
    if max_attempts < 1:
        raise ValueError("Invalid max_attempts")
    base = 1
    for k in range(max_attempts):
        wait = base*2**k + random.random()
        try:
            return f()
        except TransientError:
            if k+1 < max_attempts:
                time.sleep(wait)
            else:
                raise

def call_gemini(model, sys_input, txt_input, max_output_tokens=12000):
    """
    Wraps a simple prompt of a Gemini model
    """
    options = model.get("options", {}) 
    thinking_level = options.get("thinking_level", "medium")

    try:
        interaction = client.interactions.create(
            model=model["name"],
            system_instruction = sys_input,
            input=txt_input,
            generation_config={
                "thinking_level": thinking_level,
                "thinking_summaries": None,
                "max_output_tokens": max_output_tokens,
            },
            stream=False
        )
    except (gerr.BadRequestError, gerr.AuthenticationError, gerr.NotFoundError, gerr.PermissionDeniedError) as e:
        # 400, 401, 403, 404
        raise ConfigError(f"Gemini {type(e).__name__}: {e}") from e
    except (gerr.ConflictError, gerr.RateLimitError, gerr.InternalServerError, gerr.APIConnectionError)  as e:
        # 409, 429, 5xx, connection errors
        raise Transient(f"Gemini {type(e).__name__}: {e}") from e
    except gerr.APIError as e:
        # anything else
        raise GenerationError(f"Gemini {type(e).__name__}: {e}") from e

    status = interaction.status
    thought_tokens = interaction.usage.total_thought_tokens
    output_tokens = interaction.usage.total_output_tokens

    if status != "completed":
        # to do: log failure interactions
        # interaction.to_dict()
        #print(interaction.to_json())
        raise OutputError(f"Gemini status {status}, thought tokens {thought_tokens}, total tokens {output_tokens}")
        
    response = {
        "id": interaction.id,
        "status": status,
        "output": interaction.output_text,
        "thought_tokens": thought_tokens,
        "output_tokens": output_tokens
    }

    return response

sys_prompt = "Your job is to generate a fictitious hep-th article based on the given title. Output only complete LaTeX source and nothing else."


MODELS = [
    {"name": "gemini-323.8-flash", "provider": "gemini", "author": "Gemini 3.8 Flash (medium)", "options": {"thinking_level": "medium"} },
    {"name": "gemini-323.6-flash", "provider": "gemini", "author": "Gemini 3.6 Flash (medium)", "options": {"thinking_level": "medium"} }    
]

PROVIDERS = {
    "gemini": call_gemini,
 #   "anthropic": call_anthropic
}

title_list = [
    "The Solution of a Model for Spacetime Foam as Hyperplane Defects",
    "D-branes at the surface of the sun"
]

Npapers = 1

authors = random.sample(MODELS, Npapers)
titles = random.sample(title_list, Npapers) 

jobs = list(zip(authors, titles))

def process_paper(job):
    model, title = job
    adapter = PROVIDERS[model["provider"]] 
    r = adapter(model, sys_prompt, title)
    # to do: full compilation steps here later, for now just write to a tex file
    filename = str(int(time.time()))+".tex" # choose better filename
    with open("tex/"+filename,"w") as f:
        f.write(r["output"])

    # assuming the tex worked return the job and abstract 
    abstract = "An abstract was written" # extract from response - needs some thought
    return job, abstract

def run_processes(jobs):
    """
    Loops over all jobs
    """
    results = []
    failures = []
    retry_later = []
    for job in jobs:
        try:
            result = process_paper(job)
        except TransientError as e:
            retry_later.append( (job, e) )
        except GenerationError as e:
            failures.append( (job, e) )
        else:
            results.append(result)
            
    return results, failures, retry_later
        
results, failures, to_retry = run_processes(jobs)

if to_retry:
    time.sleep(10) # minutes for final production
    retry = [job for job,_ in retry_later]
    retry_results, retry_failures, retry_retry =  run_processes(retry)
    results.extend(retry_results)
    failures.extend(retry_failures+retry_retry)


if results: # replace with the actual write to the website
    print(f"Successful jobs: {results}")

if failures: # replace with a write to a log
    print (f"Failed solidly: {failures}")

if to_retry: # replace with a write to a log
    print (f"Failed despite retrying: {to_retry}")
