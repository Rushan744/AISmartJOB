import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def get_ai_recommendations(candidate_info, all_jobs):
    """
    Generates job recommendations for a candidate using Mistral via Ollama.
    
    Args:
        candidate_info (dict): A dictionary containing candidate details (e.g., 'nom', 'compétences').
        all_jobs (list): A list of dictionaries, where each dictionary represents a job
                         and contains at least 'title' and 'description'.
                         
    Returns:
        list: A list of recommended job dictionaries (up to 3).
    """
    
    candidate_skills = candidate_info.get('compétences', 'Aucune compétence spécifiée')
    candidate_name = candidate_info.get('nom', 'Candidat inconnu')

    job_descriptions = "\n".join([
        f"Job Title: {job.get('title', 'N/A')}\nDescription: {job.get('description', 'N/A')}"
        for job in all_jobs
    ])

    # Construct the prompt for Mistral
    prompt = (
        f"En tant qu'expert en recrutement, je souhaite obtenir des recommandations de jobs "
        f"pour le candidat suivant : {candidate_name}.\n"
        f"Ses compétences principales sont : {candidate_skills}.\n\n"
        f"Voici la liste des jobs disponibles :\n{job_descriptions}\n\n"
        f"Veuillez recommander les 3 meilleurs jobs de cette liste pour ce candidat, en vous basant sur ses compétences et la description des jobs. "
        f"Veuillez ne répondre qu'avec une liste numérotée des titres des jobs recommandés, sans aucune autre information ou texte explicatif."
    )
    print(f"Prompt sent to Mistral:\n{prompt[:500]}...") # Print first 500 chars of prompt

    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False # We want a single response
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        
        result = response.json()
        print(f"Raw response from Ollama API:\n{result}")
        
        # Extract the content from the response
        generated_text = result.get('response', '')
        print(f"Generated text from Mistral:\n{generated_text}")
        
        # Parse the generated text to get job titles
        recommended_titles = []
        for line in generated_text.split('\n'):
            line = line.strip()
            if line.startswith(('1.', '2.', '3.')):
                # Extract title after the number and period
                title = line.split('.', 1)[1].strip()
                recommended_titles.append(title)
        print(f"Extracted recommended titles: {recommended_titles}")
        
        # Filter all_jobs to get the full job details for the recommended titles
        recommended_jobs = []
        for title in recommended_titles:
            found = False
            for job in all_jobs:
                # Use .lower() and .strip() for robust comparison
                if job.get('title', '').strip().lower() == title.strip().lower():
                    recommended_jobs.append(job)
                    found = True
                    break # Move to the next recommended title
            if not found:
                print(f"Warning: Recommended job title '{title}' not found in available jobs.")
        
        print(f"Final recommended jobs (full data): {recommended_jobs}")
        # Return only the top 3 jobs as requested
        return recommended_jobs[:3]

    except requests.exceptions.RequestException as e:
        print(f"❌ Error communicating with Ollama API: {e}")
        return []
    except json.JSONDecodeError:
        print(f"❌ Error decoding JSON response from Ollama API. Response text: {response.text}")
        return []

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    sample_candidate = {
        "nom": "Alice Dupont",
        "compétences": "Python, Machine Learning, Data Analysis, SQL"
    }
    
    sample_jobs = [
        {"title": "Senior Python Developer", "description": "Experienced Python developer for web applications."},
        {"title": "Data Scientist", "description": "Analyzing large datasets, building ML models."},
        {"title": "Web Designer", "description": "UI/UX design, frontend development."},
        {"title": "Junior Python Programmer", "description": "Entry-level Python role, good for learning."},
        {"title": "AI Engineer", "description": "Developing AI solutions and deep learning models."},
    ]
    
    print("Generating recommendations...")
    recommendations = get_ai_recommendations(sample_candidate, sample_jobs)
    print("\nRecommended Jobs:")
    for job in recommendations:
        print(f"- {job['title']} ({job['company'] if 'company' in job else 'N/A'}, {job['location'] if 'location' in job else 'N/A'})")
