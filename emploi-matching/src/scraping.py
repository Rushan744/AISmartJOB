import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def assign_category_from_text(title, description=""):
    """
    Assigns a category to a job based on keywords found in its title and description.
    Uses a dictionary for more compact keyword mapping.
    """
    text = (title + " " + description).lower()

    # Define categories and their associated keywords in a dictionary
    category_keywords = {
        "data": ["data", "analyst", "scientist", "ai", "ml", "machine learning", "nlp", "vision", "bi", "statistics"],
        "web": ["web", "frontend", "backend", "full stack", "developer", "javascript", "typescript", "node.js", "react", "angular", "vue", "python", "programmer", "software"], # Added 'software'
        "mobile": ["mobile", "ios", "android", "flutter", "react native"],
        "security": ["security", "cybersecurity", "penetration tester", "soc analyst"],
        "infrastructure": ["devops", "cloud", "infrastructure", "site reliability", "platform", "system", "network"], # Added 'system', 'network'
        "management": ["product manager", "project manager", "scrum master", "agile coach", "executive", "director", "manager", "product owner", "lead", "head"], # Added 'lead', 'head'
        "testing": ["qa", "tester", "quality assurance", "test engineer", "automation"],
        "health": ["trainer", "fitness", "gym", "personal coach", "health", "medical"],
        "legal": ["law", "legal", "attorney", "paralegal", "compliance"],
        "engineering": ["engineer", "engineering", "developer", "architect", "technical", "research"], # Added 'research'
        "environment": ["energy", "environment", "sustainability", "green", "renewable", "ecologist"],
        "it support": ["support", "helpdesk", "it support", "technician", "administrator", "admin", "assistant"], # Added 'administrator', 'admin', 'assistant'
        "content_media": ["journalist", "writer", "editor", "content", "media", "communication"],
        "finance_accounting": ["accountant", "finance", "financial", "auditor", "bookkeeper"],
        "sales_marketing": ["sales", "marketing", "business development", "client", "customer", "relations"]
    }

    # Add a very broad 'general' category as a last resort before 'unknown'
    # This will catch jobs that don't fit specific categories but are clearly jobs
    category_keywords["general"] = ["job", "position", "opportunity", "hiring", "career", "specialist", "coordinator", "associate", "officer"]


    for category, keywords in category_keywords.items():
        if any(keyword in text for keyword in keywords):
            return category
    
    return "unknown" # If no category matches

def get_job_description_from_url(job_url):
    """
    Scrapes the detailed job description from a given URL.
    """
    try:
        response = requests.get(job_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        # The job description is usually within a specific div or p tag on the detail page
        # Inspect the HTML of a job detail page to find the correct selector
        description_element = soup.find("div", class_="content") # This is a common class for main content
        if description_element:
            # Extract all text, clean up extra whitespace and newlines
            return description_element.get_text(separator="\n", strip=True)
        return ""
    except requests.exceptions.RequestException as e:
        print(f"❌ Error scraping job description from {job_url}: {e}")
        return ""

def extract_from_web():
    """
    Scrapes job listings from a predefined URL and assigns categories.
    """
    base_url = "https://realpython.github.io/fake-jobs/"
    scraped_data = []
    try:
        response = requests.get(base_url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        soup = BeautifulSoup(response.content, "html.parser")
        job_listings = soup.find_all("div", class_="card-content")

        for job in job_listings:
            title = job.find("h2", class_="title is-5").text.strip() if job.find("h2", class_="title is-5") else ""
            company = job.find("h3", class_="subtitle is-6 company").text.strip() if job.find("h3", class_="subtitle is-6 company") else ""
            location = job.find("p", class_="location").text.strip() if job.find("p", class_="location") else ""
            
            # Find the "Apply" link and extract the job detail URL
            apply_link = job.find("a", class_="card-footer-item", string="Apply")
            job_detail_url = ""
            if apply_link and 'href' in apply_link.attrs:
                job_detail_url = urljoin(base_url, apply_link['href']) # Construct full URL

            # Scrape the detailed description from the job detail page
            detailed_description = get_job_description_from_url(job_detail_url)
            
            # Assign category using the refactored function
            category = assign_category_from_text(title, detailed_description)

            scraped_data.append({
                "title": title,
                "company": company,
                "location": location,
                "description": detailed_description, # Use the detailed description
                "category": category
            })

        # Example print to verify
        print("✅ Example scraped job:", scraped_data[0] if scraped_data else "No jobs scraped")
        return scraped_data

    except requests.exceptions.RequestException as e:
        print(f"❌ Error scraping web data: {e}")
        return []

if __name__ == "__main__":
    extract_from_web()
