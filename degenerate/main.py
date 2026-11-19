from dotenv import load_dotenv
import time, json
from degenerate.registry import MODELS, PROVIDERS
from degenerate.prompts import TITLE_LIST
from degenerate.pipeline import create_jobs, run_processes
load_dotenv()


def print_jobs(jobs):
    for job in jobs:
        print(json.dumps(job, indent=4))
        print()

def print_failed_jobs(jobs):
    for job, error in jobs:
        print(json.dumps(job, indent=4))
        print(error)
        print()
        
def main(Npapers=1):

    jobs = create_jobs(MODELS, TITLE_LIST, Npapers)

    print("Created the following jobs:")
    print_jobs(jobs)

    results, failures, to_retry = run_processes(jobs)

    if to_retry:
        time.sleep(10) # minutes for final production
        retry = [job for job,_ in to_retry]
        retry_results, retry_failures, retry_retry =  run_processes(retry)
        results.extend(retry_results)
        failures.extend(retry_failures+retry_retry)

    if results: # replace with the actual write to the website
        print("Successful jobs:\n")
        print_jobs(results)

    if failures: # replace with a write to a log
        print ("Failed with errors:\n")
        print_failed_jobs(failures)

    if to_retry: # replace with a write to a log
        print ("Failed due to time-outs:\n")
        print_failed_jobs(to_retry)

if __name__ == "__main__":
    main()
