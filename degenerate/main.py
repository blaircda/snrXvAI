from dotenv import load_dotenv
import time, random
from degenerate.registry import MODELS, PROVIDERS
from degenerate.prompts import TITLE_LIST
from degenerate.pipeline import run_processes
load_dotenv()

def main(Npapers=1):
    
    authors = random.sample(MODELS, Npapers)
    titles = random.sample(TITLE_LIST, Npapers) 

    jobs = list(zip(authors, titles))
    results, failures, to_retry = run_processes(jobs)

    if to_retry:
        time.sleep(10) # minutes for final production
        retry = [job for job,_ in to_retry]
        retry_results, retry_failures, retry_retry =  run_processes(retry)
        results.extend(retry_results)
        failures.extend(retry_failures+retry_retry)

    if results: # replace with the actual write to the website
        print(f"Successful jobs: {results}")

    if failures: # replace with a write to a log
        print (f"Failed solidly: {failures}")

    if to_retry: # replace with a write to a log
        print (f"Failed despite retrying: {retry_retry}")

if __name__ == "__main__":
    main()
