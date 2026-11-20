from dotenv import load_dotenv
import time, json, argparse, sys
from pathlib import Path
from degenerate.registry import MODELS
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
        
def main(Npapers, Ncollab, Ntitles):

    print(f"Generating {Npapers} papers, of which {Ncollab} collaborative.")
    print(f"Generating {Ntitles} titles:")

    titles = generate_titles(Ntitles)

    print(f"{'\n'.join(titles)}")
    print("*"*25)
    
    jobs = create_jobs(MODELS, titles, Npapers, Ncollab, max_collabs=2)

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
        wdir = Path("degenerate")
        with open(wdir / 'errors.json', 'w', encoding='utf-8') as f:
            json.dump(failures_save, f, ensure_ascii=False, indent=2)
        print(f"Failed job listings saved to {wdir}/errors.json")
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
    parser.add_argument("-C", "--Ncoll", type=int, choices=range(0, 6), default=0)
    parser.add_argument("-T", "--onetitle", action="store_true")
    args = parser.parse_args()

    Npapers = args.Npapers
    Ncollabs = args.Ncoll
    onetitle = args.onetitle

    if onetitle:
        Ntitles = 1
    else:
        Ntitles = Npapers
    
    if main(Npapers, Ncollabs, Ntitles): # main returns 1 if no papers produced
        sys.exit("No papers produced")
