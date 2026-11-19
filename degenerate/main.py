from dotenv import load_dotenv
import time, json, argparse
from degenerate.registry import MODELS
from degenerate.prompts import TITLE_LIST
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
        
def main(Npapers, Ncollab):

    print(f"Generating {Npapers} papers, of which {Ncollab} collaborative")
    
    jobs = create_jobs(MODELS, TITLE_LIST, Npapers, Ncollab, max_collabs=2)

    print(f"Created {Npapers} jobs:")
    print_jobs(jobs)

    results, failures, to_retry = run_processes(jobs)

    if to_retry:
        time.sleep(10) # minutes for final production
        #retry = [job for job,_ in to_retry]
        retry_results, retry_failures, retry_retry =  run_processes(to_retry)
        results.extend(retry_results)
        failures.extend(retry_failures+retry_retry)

    if results: # replace with the actual write to the website
        print(f"Successful jobs ({len(results)}/{Npapers}):\n")
        print_jobs(results)
        
    if failures: # replace with a write to a log
        print (f"Failed jobs ({len(failures)}/{Npapers}):\n")
        print_failed_jobs(failures)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-N", "--Npapers", type=int, choices=range(1, 5), default=1)
    parser.add_argument("-C", "--Ncoll", type=int, choices=range(0, 5), default=0)
    parser.add_argument("-T", "--onetitle", action="store_true")
    args = parser.parse_args()

    Npapers = args.Npapers
    Ncollabs = args.Ncoll
    onetitle = args.onetitle

    main(Npapers, Ncollabs)
