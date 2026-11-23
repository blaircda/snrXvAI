from jinja2 import Environment, FileSystemLoader, select_autoescape
import json, time, shutil
from pathlib import Path

def create_site_dir():
    """
    Create site directory, every time afresh
    """
    ROOT = Path(__file__).resolve().parent.parent   # publish.py -> degenerate/ -> project root
    SITE = ROOT / "site"
    if SITE.exists() and SITE.parent == ROOT and SITE.name=="site":
        shutil.rmtree(SITE)

    shutil.copytree(ROOT / "degenerate" / "static", SITE)
    
    shutil.copytree(ROOT / "abs", SITE,  dirs_exist_ok=True)

    PDF_DIR = SITE / "pdf"
    PDF_DIR.mkdir(parents=True)
    
    return ROOT, SITE, PDF_DIR

def get_listings(listings_file):
    """
    Load listings
    """
    with open(listings_file, "r") as f:
        job_results = json.load(f)
        
    datestamp = job_results["date"]
    datestamp_time = time.strptime(datestamp, "%Y-%m-%d %H:%M:%S")
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
    ROOT, SITE, PDF_DIR = create_site_dir()

    date, listings = get_listings("degenerate/listing.json")
    
    env = Environment(
        loader=FileSystemLoader("degenerate/templates/"),
        autoescape=select_autoescape()
    )

    template = env.get_template("index.html")
    template_output = template.render(pretty_date=date, listings=listings)

    with open(SITE / "index.html", "w") as f:
        f.write(template_output)

    for paper in listings:
        pid = paper["id"]+".pdf"
        pdf = ROOT / "papers" / pid
        shutil.copy( pdf, PDF_DIR)
