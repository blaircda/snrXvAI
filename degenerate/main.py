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
        
def main(Npapers, Ncollab, max_paper_authors, Ntitles, models):

    print(f"Generating {Npapers} papers, of which {Ncollab} collaborative.")
    print(f"Generating {Ntitles} titles:")
  
    titles = generate_titles(Ntitles)

    print(f"{'\n'.join(titles)}")
    print("*"*25)
    
    jobs = create_jobs(models, titles, Npapers, Ncollab, max_paper_authors=max_paper_authors)

    #print(f"Created {Npapers} jobs:")
    #print_jobs(jobs)

    results, failures, to_retry = run_processes(jobs)

    if to_retry:
        time.sleep(60) 
        #retry = [job for job,_ in to_retry]
        retry_results, retry_failures, retry_retry =  run_processes(to_retry)
        results.extend(retry_results)
        failures.extend(retry_failures+retry_retry)

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        
    if failures: # write failures to JSON
        print (f"Failed jobs ({len(failures)}/{Npapers}):\n")
        failures_save = { "date": timestamp, "papers": failures}
        failures_dir = Path("failed")
        failures_dir.mkdir(parents=True, exist_ok=True)
        with open(failures_dir / 'errors.json', 'w', encoding='utf-8') as f:
            json.dump(failures_save, f, ensure_ascii=False, indent=2)
        print(f"Failed job listings saved to {failures_dir}/errors.json")
        #print_failed_jobs(failures)
        
    if results: # write successful jobs to JSON
        print(f"Successful jobs: ({len(results)}/{Npapers})")
        results_save = { "date": timestamp, "papers": results}
        wdir = Path("degenerate")
        with open(wdir / 'listing.json', 'w', encoding='utf-8') as f:
            json.dump(results_save, f, ensure_ascii=False, indent=2)
        print(f"Successful job listing saved to {wdir}/listing.json")
        #print_jobs(results)
        return 0
    else:
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-N", "--Npapers", type=int, default=1)
    parser.add_argument("-C", "--Ncollabs", type=int, default=0)
    parser.add_argument("-K", "--max_paper_authors", type=int, default=2)
    parser.add_argument("-T", "--single_title", action="store_true") # set only 1 title
    parser.add_argument("-M", "--models", choices=["all", "dev", "free", "budget"], default="budget")
    args = parser.parse_args()

    Npapers = args.Npapers # number of papers
    Ncollabs = args.Ncollabs # number of collaborative papers
    max_paper_authors = args.max_paper_authors # max authors on a collaborative paper

    if max_paper_authors < 2:
        parser.error("--max_paper_authors must be >= 2")
    
    models_needed = Npapers + Ncollabs*(max_paper_authors-1) 
    
    if args.single_title:
        Ntitles = 1
    else:
        Ntitles = args.Npapers

    if args.models == "all": # all models 
        MODELS = PAID_MODELS + FREE_MODELS
    elif args.models == "dev": # examples for testing
        MODELS = DEV_MODELS
    elif args.models == "free": # free models only
        MODELS = FREE_MODELS
    elif args.models == "budget": # take all free models and a minimum number of paid models
        k = models_needed - len(FREE_MODELS)
        # if k <= 0 then we already have enough models, so take at most a small number of paid models
        # if k > 0 then we need more models
        Npaid = max(k, 2) 
        MODELS = FREE_MODELS + random.sample(PAID_MODELS, Npaid)

    if main(Npapers, Ncollabs, max_paper_authors, Ntitles, MODELS): # main returns 1 if no papers produced
        sys.exit("No papers produced")
