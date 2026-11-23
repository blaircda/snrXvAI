import time, random
from degenerate.errors import GenerationError, TransientError, ConfigError, OutputError 
from degenerate.registry import PROVIDERS
from degenerate.compile import make_paper, make_full_source, check_source
from degenerate.prompts import make_user_prompt, SYS_PROMPT

def create_jobs(list_of_models, list_of_titles, Npapers, Ncollab, max_paper_authors=2):
    """
    Assigns titles to models

    Parameters
    ------
    list_of_models list of dict
    list_of_titles list of str
    Npapers number of papers to build
    Ncollab number of collaborative papers
    max_paper_authors max number of models on a single paper
    
    Returns
    ------
    list of dicts
        where each dict has keys
        author_model, title, job_id
    """
    # restrict max_paper_authors to the number of available models
    if max_paper_authors > len(list_of_models):
        max_paper_authors = len(list_of_models)
        
    # get the titles we'll use
    # if passing only 1 title, then all will be given the same title
    if Npapers > len(list_of_titles):
        titles = random.choices(list_of_titles, k=Npapers)
    else:
        titles = random.sample(list_of_titles, Npapers)

    # assign flags to say which papers are collaborative
    if Ncollab < Npapers:
        flags = [True]*Ncollab + [False]*(Npapers - Ncollab)
        random.shuffle(flags)
    else:
        flags= [True]*Ncollab
    # if Ncollab > Npapers just take them all to be collaborative without raising

    # record jobs as a list
    jobs = []

    # generate paper ids
    YYMM = time.strftime("%y%m", time.localtime())
    XXXXX = random.randint(60000, 90000) # arXiv ids are up to ~40000 as of 2610 so start higher than that

    def format_id(X): # format to 5 digits if allowing any ids
        return "0"*(5-len(str(X)))+str(X)

    for title, is_collab in zip(titles, flags): 
        if is_collab:
            n_collabs = random.randint(2, max_collabs)
        else:
            n_collabs = 1
        models = random.sample(list_of_models, n_collabs)
        stages = [ {"model": models[0], "version": "initial"} ] + [{"model":m, "version": "revision"} for m in models[1:]]
        papername = YYMM+"."+format_id(XXXXX)
        job_info = {
            "job_id": papername,
            "title": title,
            "stages": stages
        }
        jobs.append(job_info)
        XXXXX = XXXXX + 1 
        
    return jobs

def process_paper(job):
    """
    Process a single job
    """
    stages, title, job_id = job["stages"], job["title"], job["job_id"]

    paper_authors = []
    output_tokens = 0
    thought_tokens = 0
    source = ""
    for stage in stages:
        model = stage["model"]
        adapter = PROVIDERS[model["provider"]]
        prompt = make_user_prompt(stage["version"], title, source)
        r = adapter(model, SYS_PROMPT, prompt)
        if not (r["output"] or "").strip():
            raise OutputError(f"Empty output for {job['job_id']} with model {model['name']}")
        source = check_source(r["output"], job['job_id'])
        output_tokens += r.get("output_tokens",0)
        thought_tokens += r.get("thought_tokens",0) 
        paper_authors.append(model["display_name"])

    # here could try except to send a source with invalid commands back to the model
    full_source, abstract = make_full_source(source, title, paper_authors, job_id)

    # here could try except to send a source which does not compile back to the model
    make_paper(full_source, job_id)
    
    # assuming the tex worked return the job and abstract 
    job["abstract"] = abstract
    job["output_tokens"] = output_tokens
    job["thought_tokens"] = thought_tokens
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
            job["error"] = str(e)
            retry_later.append(job)
            #retry_later.append( (job, str(e)) )
        except GenerationError as e:
            job["error"] = str(e)
            failures.append(job)
            #failures.append( (job, str(e)) )
       except Exception as e: # anything unanticipated
            job["error"] = f"Unexpected {type(e).__name__}: {e}"
            job["traceback"] = traceback.format_exc()
            print(f"Unexpected error in {job['job_id']}: {type(e).__name__}")
            failures.append(job)
        else:
            result.pop("error", None)
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
