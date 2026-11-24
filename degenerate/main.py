from dotenv import load_dotenv
import time, json, argparse, sys, random
from pathlib import Path
from degenerate.registry import DEV_MODELS, get_model_registry, split_models_by_cost
from degenerate.generate_titles import generate_titles
from degenerate.pipeline import create_jobs, run_processes

load_dotenv()

def print_jobs(jobs):
    for job in jobs:
        print(json.dumps(job, indent=2))
        print()

def print_failed_jobs(jobs):
    for job in jobs:
        print(json.dumps(job, indent=2))
        #print(json.dumps(error))
        print()
        
def main(timestamp, paper_struct, Ntitles, models):
    """
    Run the paper generation pipeline 
    """
    Npapers = len(paper_struct)
    print(f"Generating {Ntitles} titles for {Npapers} papers.")
    titles = generate_titles(Ntitles)
    print(f"{'\n'.join(titles)}")
    print("*"*25)

    jobs = create_jobs(timestamp, models, titles, paper_struct)

    #print(f"Created {Npapers} jobs:")
    #print_jobs(jobs)

    results, failures, to_retry = run_processes(jobs)

    parse_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", timestamp)

    if to_retry:
        time.sleep(120) 
        retry_results, retry_failures, retry_retry =  run_processes(to_retry)
        results.extend(retry_results)
        failures.extend(retry_failures+retry_retry)

    if failures: # write failures to JSON
        print (f"Failed jobs ({len(failures)}/{Npapers}):\n")
        failures_save = { "date": parse_timestamp, "papers": failures}
        failures_dir = Path("failed")
        failures_dir.mkdir(parents=True, exist_ok=True)
        with open(failures_dir / 'errors.json', 'w', encoding='utf-8') as f:
            json.dump(failures_save, f, ensure_ascii=False, indent=2)
        print(f"Failed job listings saved to {failures_dir}/errors.json")
        #print_failed_jobs(failures)
        
    if results: # write successful jobs to JSON
        print(f"Successful jobs: ({len(results)}/{Npapers})")
        results_save = { "date": parse_timestamp, "papers": results}
        wdir = Path("degenerate")
        with open(wdir / 'listing.json', 'w', encoding='utf-8') as f:
            json.dump(results_save, f, ensure_ascii=False, indent=2)
        print(f"Successful job listing saved to {wdir}/listing.json")
        #print_jobs(results)
        return 0
    else:
        return 1

def schedule_settings(timestamp):
    """
    define scheduled behaviour
    """
    #day = timestamp.tm_wday
    # time invariant for now
    Npapers = 10
    Ncollabs = 3
    max_paper_authors = 2
    Ntitles = 10
    model_choice = "balanced"
    Ndear = 5

    return Npapers, Ncollabs, max_paper_authors, Ntitles, model_choice, Ndear

def plan_papers(Npapers, Ncollabs, max_paper_authors):
    """
    how many authors per paper

    returns a list whose length is Npapers and whose sum is the total number of authors
    """
    paper_authors = []
    for k in range(Npapers):
        if k < Ncollabs:
            paper_authors.append(random.randint(2, max_paper_authors))
        else:
            paper_authors.append(1)
    return paper_authors

def get_models(paper_struct, mode, Ndear):
    """
    Return different combos of models 
    """
    Npapers = len(paper_struct)
    models_needed =sum(paper_struct) 

    def populate(family, k):
        if k<=len(family):
            return random.sample(family, k)
        else:
            return random.choices(family, k=k)

    registry = get_model_registry("degenerate/models.csv", 2.0)
    models_free, models_cheap, models_dear = split_models_by_cost(registry, 0.2)
            
    if mode == "all": # all models 
        MODELS = populate(registry, models_needed)
    elif mode == "dev": # examples for testing
        MODELS = populate(DEV_MODELS, models_needed)
    elif mode == "free": # free models only
        MODELS  = populate(models_free, models_needed)
    elif mode == "cheap": # cheap non-free models only
        MODELS = populate(models_cheap, models_needed)
    elif mode == "balanced": # take a minimum number of dear models
        Ndear = min(Ndear, models_needed//2)
        MODELS = populate(models_dear, Ndear) + populate(models_free+models_cheap, models_needed - Ndear)

    return MODELS
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-N", "--Npapers", type=int, default=None)
    parser.add_argument("-C", "--Ncollabs", type=int, default=None)
    parser.add_argument("-A", "--max_paper_authors", type=int, default=None)
    parser.add_argument("-D", "--max_dear_models", type=int, default=None)
    parser.add_argument("-T", "--single_title", action="store_true") # set only 1 title
    parser.add_argument("-S", "--schedule", action="store_true") # apply scheduling logic, for remote automated runs
    parser.add_argument("-M", "--models", choices=["all", "dev", "free", "cheap", "balanced"], default=None)
    args = parser.parse_args()

    if args.schedule and (args.Npapers is not None or args.Ncollabs is not None or args.max_paper_authors is not None or args.max_dear_models is not None or args.single_title or args.models):
        parser.error("--schedule cannot be combined with other options")

    timestamp = time.gmtime()

    if args.schedule:
        Npapers, Ncollabs, max_paper_authors, Ntitles, model_choice, Ndear = schedule_settings(timestamp)
        
    else:
        Npapers = 3 if args.Npapers is None else args.Npapers
        Ncollabs = 0 if args.Ncollabs is None else args.Ncollabs
        max_paper_authors = 2 if args.max_paper_authors is None else args.max_paper_authors # max authors on a collaborative paper
        Ndear = 2 if args.max_dear_models is None else args.max_dear_models
        if max_paper_authors < 2:
            parser.error("--max_paper_authors must be >= 2")

        model_choice = "balanced" if args.models is None else args.models

        if args.single_title:
            Ntitles = 1
        else:
            Ntitles = Npapers
    
    paper_struct = plan_papers(Npapers, Ncollabs, max_paper_authors)
    MODELS = get_models(paper_struct, model_choice, Ndear) 
    for m in MODELS:
        print(m)
        print()
    print("Expected cost:", sum([m["run_cost"] for m in MODELS]))
    #if main(timestamp, paper_struct, Ntitles, MODELS): # main returns 1 if no papers produced
    #    sys.exit("No papers produced")
