from dotenv import load_dotenv
import time, json, argparse, sys, random
from pathlib import Path
from degenerate.registry import DEV_MODELS, FREE_MODELS, PAID_MODELS 
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
        time.sleep(60) 
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
    define different behaviour for different weekdays
    """
    day = timestamp.tm_wday
    Npaid = None
    if day == 0: # Mondays
        Npapers, Ncollabs, max_paper_authors, Ntitles = 6, 1, 2, 6
        model_choice = "budget"
        Npaid = 1
    elif day == 1 or day == 3: # Tuesdays and Thursdays
        Npapers, Ncollabs, max_paper_authors, Ntitles = 4, 1, 2, 4
        model_choice = "free"
    elif day == 2: # Wednesdays
        Npapers, Ncollabs, max_paper_authors, Ntitles = 4, 1, 2, 1
        model_choice = "budget"
        Npaid = 2
    elif day == 4: # Fridays
        Npapers, Ncollabs, max_paper_authors, Ntitles = 4, 1, 2, 4
        model_choice = "budget"
        Npaid = 2
    else:
        raise SystemExit("Buen finde")

    return Npapers, Ncollabs, max_paper_authors, Ntitles, model_choice, Npaid

def plan_papers(Npapers, Ncollabs, max_paper_authors):
    """
    how many authors per paper

    returns a list whose length is Npapers and whose sum is the total number of authors
    """
    # assign flags to say which papers are collaborative
    if Ncollabs < Npapers:
        flags = [True]*Ncollabs + [False]*(Npapers - Ncollabs)
        random.shuffle(flags)
    else:
        flags= [True]*Ncollabs

    paper_authors = []
    for k in range(Npapers):
        if flags[k]:
            paper_authors.append(random.randint(2, max_paper_authors))
        else:
            paper_authors.append(1)
    return paper_authors

def get_models(paper_struct, mode, Npaid):
    """
    Return different combos of models 
    """
    Npapers = len(paper_struct)
    models_needed =sum(paper_struct) 
    #print(f"Assembling models for {paper_struct}")
    #print(f"{Npapers} papers, with {models_needed} authors")

    def populate(family, k):
        if k<=len(family):
            return random.sample(family, k)
        else:
            return random.choices(family, k=k)
            
    if mode == "all": # all models 
        MODELS = populate(PAID_MODELS + FREE_MODELS, models_needed)
    elif mode == "dev": # examples for testing
        MODELS = populate(DEV_MODELS, models_needed)
    elif mode == "free": # free models only
        MODELS  = populate(FREE_MODELS, models_needed)
    elif mode == "budget": # take a minimum number of paid models
        if Npaid <= models_needed:
            MODELS = populate(PAID_MODELS, Npaid) + populate(FREE_MODELS, models_needed - Npaid)
        else:
            MODELS = populate(PAID_MODELS, Npaid) 
    return MODELS
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-N", "--Npapers", type=int, default=None)
    parser.add_argument("-C", "--Ncollabs", type=int, default=None)
    parser.add_argument("-A", "--max_paper_authors", type=int, default=None)
    parser.add_argument("-P", "--paid", type=int, default=None)
    parser.add_argument("-T", "--single_title", action="store_true") # set only 1 title
    parser.add_argument("-S", "--schedule", action="store_true") # apply scheduling logic, for remote automated runs
    parser.add_argument("-M", "--models", choices=["all", "dev", "free", "budget"], default=None)
    args = parser.parse_args()

    if args.schedule and (args.Npapers is not None or args.Ncollabs is not None or args.max_paper_authors is not None or args.paid is not None or args.single_title or args.models):
        parser.error("--schedule cannot be combined with other options")

    timestamp = time.gmtime()

    if args.schedule:
        Npapers, Ncollabs, max_paper_authors, Ntitles, model_choice, Npaid = schedule_settings(timestamp)
        
    else:
        Npapers = 3 if args.Npapers is None else args.Npapers
        Ncollabs = 0 if args.Ncollabs is None else args.Ncollabs
        max_paper_authors = 2 if args.max_paper_authors is None else args.max_paper_authors # max authors on a collaborative paper
        Npaid = 2 if args.paid is None else args.paid
        if max_paper_authors < 2:
            parser.error("--max_paper_authors must be >= 2")

        model_choice = "budget" if args.models is None else args.models

        if args.single_title:
            Ntitles = 1
        else:
            Ntitles = Npapers
            
    paper_struct = plan_papers(Npapers, Ncollabs, max_paper_authors)
    MODELS = get_models(paper_struct, model_choice, Npaid) 

    if main(timestamp, paper_struct, Ntitles, MODELS): # main returns 1 if no papers produced
        sys.exit("No papers produced")
