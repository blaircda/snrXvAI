import time, random
from degenerate.errors import GenerationError, TransientError, ConfigError, OutputError 
from degenerate.registry import PROVIDERS
from degenerate.compile import make_paper, make_full_source
from degenerate.prompts import SYS_PROMPT

def create_jobs(list_of_models, list_of_titles, Npapers):
    """
    Assigns titles to models

    Parameters
    ------
    list_of_models list of dict
    list_of_titles list of str
    
    Returns
    ------
    list of dicts
        where each dict has keys
        author_model, title, job_id
    """
    authors = random.sample(list_of_models, Npapers)
    titles = random.sample(list_of_titles, Npapers)
    
    YYMM = time.strftime("%y%m", time.localtime())
    #XXXXX = time.strftime("%w%m%S", time.localtime())
    XXXXX = random.randint(0, 30000)

    def to_str(X):
        return "0"*(5-len(str(X)))+str(X)

    jobs = []
    for author, title in zip(authors, titles):
        papername = YYMM+"."+to_str(XXXXX)
        job_info = {
        "model": author,
        "title": title,
        "job_id": papername
        }
        jobs.append(job_info)
        XXXXX = XXXXX + 1 
        
    return jobs

def process_paper(job):
    """
    Process a single job
    """
    model, title, job_id = job["model"], job["title"], job["job_id"]
    
    adapter = PROVIDERS[model["provider"]] 
    r = adapter(model, SYS_PROMPT, title)
    source = r["output"]
    tokens = r.get("thought_tokens",0) + r.get("output_tokens",0)
    paper_author = model["author"]

    # here could try except to send a source with invalid commands back to the model
    full_source, abstract = make_full_source(source, title, paper_author)

    # here could try except to send a source which does not compile back to the model
    make_paper(full_source, job_id)
    
    # assuming the tex worked return the job and abstract 
    job["abstract"] = abstract
    job["tokens"] = tokens
    return job

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
