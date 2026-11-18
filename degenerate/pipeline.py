from degenerate.errors import GenerationError, TransientError, ConfigError, OutputError 
from degenerate.registry import PROVIDERS
from degenerate.compile import make_paper
from degenerate.prompts import SYS_PROMPT

def process_paper(job):
    """
    Process a single job
    """
    model, title = job
    adapter = PROVIDERS[model["provider"]] 
    r = adapter(model, SYS_PROMPT, title)
    source = r["output"]

    make_paper(source)
    
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
