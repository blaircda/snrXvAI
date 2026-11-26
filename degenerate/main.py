from dotenv import load_dotenv
import time, json, argparse, sys, random, re, os
from datetime import date
from pathlib import Path
from degenerate.registry import DEV_MODELS, get_model_registry, split_models_by_cost
from degenerate.generate_titles import generate_titles
from degenerate.pipeline import create_jobs, run_processes
from degenerate.paths import OUTPUT_DIR, PACKAGE_DIR
        
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

def stage_cost(stage):
    usage = stage.get("usage") or {}
    reported = usage.get("reported_cost")
    return usage.get("computed_cost", 0) if reported is None else reported

def stage_tokens(stage):
    usage = stage.get("usage") or {}
    return usage.get("output_tokens", 0)

def get_cost(jobs):
    return sum(stage_cost(stage) for job in jobs for stage in job["stages"])

def get_tokens(jobs):
    return sum(stage_tokens(stage) for job in jobs for stage in job["stages"])

def summarise(results, failures):
    """
    Make a headline summary of successes, failures, cost
    """
    Npapers = len(results)
    Nfailed = len(failures)
    Ntotal = Npapers + Nfailed
    cost_papers = get_cost(results)
    cost_failures = get_cost(failures)
    total_cost = cost_papers + cost_failures
    summary = f"\nSucceeded: {Npapers}/{Ntotal} papers\nCost: {cost_papers:.2f}\n\nFailed: {Nfailed}/{Ntotal} papers\nCost: {cost_failures:.2f}\n\nTotal cost: {total_cost:.2f}\n"
    return summary

def tabularise(jobs):
    """
    Make a markdown table of job completion/failure/usage details
    """
    table = "|**Paper** + Stages|**Authors**|**Tokens**|**Cost**|**Final Status** + Status by Stage|\n|---|---|---|---|---|"
    
    for job in jobs:
        job_id = job["job_id"]
        title = job["title"]
        error = job.get("error")
        if error is not None:
            final_status = "**Error:** "+error
        else:
            final_status = "**Completed**"
        stages = job["stages"]        
        table += f"\n|**{job_id}**|{len(stages)}|{get_tokens([job])}|{get_cost([job]):.2f}|{final_status}|"

        ok = True
        for stage in stages:
            cost = stage_cost(stage) 
            model = stage["model"]["name"]
            if stage["model"].get("options",{}).get("effort") is not None:
                model += " "+stage["model"]["options"]["effort"]
            version = stage["version"]
            tokens = stage_tokens(stage)
            stage_status = stage.get("error")
            if stage_status is None: # no error found
                if ok:
                    stage_status = "Success"
                else:
                    stage_status = "Not run"
            else:
                stage_status = "Error"
                ok = False
            table += f"\n|{version}|{model}|{tokens}|{cost:.2f}|{stage_status}|"

    return table
    
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

    # uncomment for debugging job creation
    #print(f"Created {Npapers} jobs:")
    #print_jobs(jobs)
    #return jobs

    results, failures, to_retry = run_processes(jobs)

    #parse_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", timestamp)

    if to_retry:
        time.sleep(120) 
        retry_results, retry_failures, retry_retry =  run_processes(to_retry)
        results.extend(retry_results)
        failures.extend(retry_failures+retry_retry)

    summary = summarise(results, failures)
    table = tabularise(results+failures)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path: # only exists on GitHub; skip when running locally
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(f"### snrXvAI run {timestamp}\n")
            f.write(summary)
            f.write(table)
    else:
        print(summary)
        print(table)

    if failures: # write failures to JSON
        #print (f"Failed jobs ({len(failures)}/{Npapers}):\n")
        failures_save = { "date": timestamp, "papers": failures}
        with open(OUTPUT_DIR / 'errors.json', 'w', encoding='utf-8') as f:
            json.dump(failures_save, f, ensure_ascii=False, indent=2)
        print(f"\nFailed job listings saved to {OUTPUT_DIR}/errors.json")
        #print_failed_jobs(failures)
        
    if results: # write successful jobs to JSON
        #print(f"Successful jobs: ({len(results)}/{Npapers})")
        results_save = { "date": timestamp, "papers": results}
        with open(OUTPUT_DIR / 'listing.json', 'w', encoding='utf-8') as f:
            json.dump(results_save, f, ensure_ascii=False, indent=2)
        print(f"Successful job listing saved to {OUTPUT_DIR}/listing.json")
        #print_jobs(results)
        return 0
    else:
        return 1

def schedule_settings(timestamp):
    """
    define scheduled behaviour
    """
    # assuming timestamp a time struct
    # use: day = timestamp.tm_wday
    # assuming timestamp a string in the form
    # YYYY-MM-DD_HHMMSS
    # use: day = date.fromisoformat(timestamp[:10]).weekday()
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

    registry = get_model_registry(PACKAGE_DIR / "models.csv", 2.0)
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


def run_ts_arg(value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{6}", value):
        raise argparse.ArgumentTypeError(f"expected YYYY-MM-DD_HHMMSS, got {value!r}")
    return value

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("-N", "--Npapers", type=int, default=None)
    parser.add_argument("-C", "--Ncollabs", type=int, default=None)
    parser.add_argument("-A", "--max_paper_authors", type=int, default=None)
    parser.add_argument("-D", "--max_dear_models", type=int, default=None)
    parser.add_argument("-T", "--single_title", action="store_true") # set only 1 title
    parser.add_argument("-S", "--schedule", action="store_true") # apply scheduling logic, for remote automated runs
    parser.add_argument("-M", "--models", choices=["all", "dev", "free", "cheap", "balanced"], default=None)
    parser.add_argument("--run-ts", type=run_ts_arg, default=None) # run time stamp
    args = parser.parse_args()

    if args.schedule and (args.Npapers is not None or args.Ncollabs is not None or args.max_paper_authors is not None or args.max_dear_models is not None or args.single_title or args.models):
        parser.error("--schedule cannot be combined with other options")

    TS_FORMAT = "%Y-%m-%d_%H%M%S"
    run_timestamp = args.run_ts or time.strftime(TS_FORMAT, time.gmtime())
    
    if args.schedule:
        Npapers, Ncollabs, max_paper_authors, Ntitles, model_choice, Ndear = schedule_settings(run_timestamp)
        
    else:
        Npapers = 5 if args.Npapers is None else args.Npapers
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
    #for m in MODELS:
    #    print(m)
    #    print()
    #print("Expected cost:", sum([m["expected_cost"] for m in MODELS]))
    if main(run_timestamp, paper_struct, Ntitles, MODELS): # main returns 1 if no papers produced
        sys.exit("No papers produced")
