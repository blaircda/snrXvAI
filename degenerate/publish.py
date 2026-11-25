from jinja2 import Environment, FileSystemLoader, select_autoescape
import json, time, shutil
from pathlib import Path
from degenerate.paths import ROOT, SITE_DIR, PACKAGE_DIR, PAPERS_DIR

def create_site_dir():
    """
    Create site directory, every time afresh
    """
    if SITE_DIR.exists() and SITE_DIR.parent == ROOT and SITE_DIR.name=="site":
        shutil.rmtree(SITE_DIR)

    shutil.copytree(PACKAGE_DIR / "static", SITE_DIR)
    
    shutil.copytree(ROOT / "abs", SITE_DIR,  dirs_exist_ok=True)

    PDF_DIR = SITE_DIR / "pdf"
    PDF_DIR.mkdir(parents=True)
    
    return PDF_DIR

def get_listings(listings_file):
    """
    Load listings
    """
    with open(listings_file, "r") as f:
        job_results = json.load(f)
        
    datestamp = job_results["date"]
    datestamp_time = time.strptime(datestamp, "%Y-%m-%d_%H%M%S")
    paper_details = job_results["papers"] 
    listing_date = time.strftime("%A, %-d %B %Y",datestamp_time )
    listings = []
    
    for i, p in enumerate(paper_details):
        listing = {}
        listing["order"] = i+1
        listing["id"] = p["job_id"]
        listing["title"] = p["title"]
        listing["authors"] = ', '.join([s["model"]["display_name"] for s in p["stages"]])
        listing["abstract"] = p["abstract"]
        listing["comments"] = f"{p['thought_tokens']+p['output_tokens']} tokens"
        #f"{p['thought_tokens']} thought tokens, {p['output_tokens']} output tokens"
        listings.append(listing)

    return listing_date, listings
    

if __name__ == "__main__":
    PDF_DIR = create_site_dir()

    date, listings = get_listings(PACKAGE_DIR / "listing.json")
    
    env = Environment(
        loader=FileSystemLoader(PACKAGE_DIR / "templates/"),
        autoescape=select_autoescape()
    )

    template = env.get_template("index.html")
    template_output = template.render(pretty_date=date, listings=listings)

    with open(SITE_DIR / "index.html", "w") as f:
        f.write(template_output)

    for paper in listings:
        pid = paper["id"]+".pdf"
        pdf = PAPERS_DIR / pid
        shutil.copy( pdf, PDF_DIR)
