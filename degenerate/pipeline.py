import time, random, traceback
from degenerate.errors import GenerationError, TransientError, ConfigError, OutputError 
from degenerate.registry import PROVIDERS
from degenerate.compile import make_paper, make_full_source, check_source
from degenerate.prompts import make_user_prompt, SYS_PROMPT

def create_jobs(timestamp, list_of_models, list_of_titles, paper_struct):
    """
    Assigns titles to models

    Parameters
    ------
    timestamp used to get YYMM part of paper id
    list_of_models list of dict
    list_of_titles list of str
    list paper_struct list of ints specifying number of authors per paper
    
    Returns
    ------
    list of dicts
        where each dict has keys
        job_id, title, stages
        and stages is a list of dicts with keys model, version for collaborative papers
    """    
    # if less titles than papers, make the title list longer by resampling from the original enough times
    if len(list_of_titles) < len(paper_struct):
        titles = list_of_titles + random.choices(list_of_titles, k = len(paper_struct) - len(list_of_titles))
    else:
        titles = list(list_of_titles)
    
    # record jobs as a list
    jobs = []
    # generate paper ids
    #YYMM = time.strftime("%y%m", timestamp)
    # assuming timestamp a string YYYY-MM-DD_HHMMSS
    YYMM = timestamp[2:4] + timestamp[5:7]

    XXXXX = random.randint(60000, 90000) # arXiv ids are up to ~40000 as of 2610 so start higher than that

    def format_id(X): # format to 5 digits if allowing any ids
        return "0"*(5-len(str(X)))+str(X)

    # assign models to papers
    # try to avoid having the same model twice on a collaboration
    pool = list(list_of_models) 
    paper_authors = []
    for nauthors in paper_struct:
        authors = []
        for k in range(nauthors):
            cands = [x for x in pool if x not in authors]
            if cands:
                pick = random.choice(cands)
                authors.append(pick)
            else:
                print("Unable to avoid duplicate models on a collaboration")
                pick = random.choice(pool)
            pool.remove(pick) 
        paper_authors.append(authors)
        
    random.shuffle(paper_authors)
    for models, title in zip(paper_authors, titles):
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


def compute_cost(model, usage):
    mil = 1000000.
    input_cost, output_cost = model.get("input_cost"), model.get("output_cost")
    input_tokens, output_tokens = usage["input_tokens"], usage["output_tokens"]
    if all(x is not None for x in (input_tokens, output_tokens, input_cost, output_cost)):
        cost = input_tokens*input_cost/mil + output_tokens*output_cost/mil
    else:
        cost = None
    usage["computed_cost"] = cost
    return usage

def process_paper(job):
    """
    Process a single job
    """
    stages, title, job_id = job["stages"], job["title"], job["job_id"]

    paper_authors = []
    source = ""
    try:
        for i, stage in enumerate(stages):
            model = stage["model"]
            adapter = PROVIDERS[model["provider"]]
            # make the prompt
            prompt = make_user_prompt(stage["version"], title, source)
            # send the prompt to the adapter
            r = adapter(model, SYS_PROMPT, prompt, call_id = f"{job_id}_{i}")
            stage["usage"] = compute_cost(model, r["usage"])
            # check for empty output
            if not (r["output"] or "").strip():
                raise OutputError(f"Empty output for {job['job_id']} with model {model['name']}")
            # check the source at this stage
            source = check_source(r["output"], job['job_id'])
            # get name of the model with effort for the pdf
            display_name = model["display_name"]
            if model.get("options", {}).get("effort") is not None:
                display_name += " ("+model["options"]["effort"]+")"
            paper_authors.append(display_name)
    except GenerationError as e:
        stage["error"] = True
        if e.usage is not None:
            stage["usage"] = compute_cost(model, e.usage)
        raise
        
    # here could try except to send a source with invalid commands back to the model
    full_source, abstract = make_full_source(source, title, paper_authors, job_id)

    # here could try except to send a source which does not compile back to the model
    make_paper(full_source, job_id)
    
    # assuming the tex worked return the job and abstract 
    job["abstract"] = abstract

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
