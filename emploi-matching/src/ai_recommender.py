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

def get_ai_recommendations_from_cv(cv_text: str, all_jobs: list):
    """
    Generates job recommendations and a career recommendation text for a candidate
    based on their CV using Mistral via Ollama.
    
    Args:
        cv_text (str): The extracted text content of the candidate's CV.
        all_jobs (list): A list of dictionaries, where each dictionary represents a job
                         and contains at least 'title' and 'description'.
                         
    Returns:
        tuple: A tuple containing:
            - list: A list of recommended job dictionaries (up to 3).
            - str: A career recommendation text.
    """
    job_descriptions = "\n".join([
        f"Job Title: {job.get('title', 'N/A')}\nDescription: {job.get('description', 'N/A')}"
        for job in all_jobs
    ])

    # Prompt for job recommendations and career recommendation text
    prompt = (
        f"En tant qu'expert en recrutement et conseiller d'orientation, j'ai le CV suivant :\n"
        f"```\n{cv_text}\n```\n\n"
        f"Voici la liste des jobs disponibles :\n{job_descriptions}\n\n"
        f"Veuillez effectuer les tâches suivantes :\n"
        f"1. Recommander les 3 meilleurs jobs de cette liste pour ce candidat, en vous basant sur son CV. "
        f"Veuillez lister ces jobs sous la section 'Jobs Recommandés:' avec une liste numérotée des titres des jobs.\n"
        f"2. Fournir un texte de recommandation de carrière détaillé (environ 150-200 mots) pour le candidat, "
        f"en analysant son CV et les jobs recommandés. Ce texte doit inclure des points forts du CV, "
        f"des suggestions d'amélioration ou de développement de compétences, et des perspectives de carrière. "
        f"Veuillez placer ce texte sous la section 'Recommandation de Carrière:'."
    )
    print(f"Prompt sent to Mistral for CV analysis:\n{prompt[:500]}...")

    headers = {'Content-Type': 'application/json'}
    data = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        
        result = response.json()
        print(f"Raw response from Ollama API (CV analysis):\n{result}")
        
        generated_text = result.get('response', '')
        print(f"Generated text from Mistral (CV analysis):\n{generated_text}")
        
        recommended_titles = []
        career_recommendation_text = ""

        # Parse the generated text
        sections = generated_text.split('Recommandation de Carrière:')
        if len(sections) > 1:
            job_section = sections[0]
            career_recommendation_text = sections[1].strip()

            # Extract job titles from the job section
            for line in job_section.split('\n'):
                line = line.strip()
                if line.startswith(('1.', '2.', '3.')) and 'Jobs Recommandés:' in job_section:
                    title = line.split('.', 1)[1].strip()
                    recommended_titles.append(title)
        else:
            # Fallback if sections are not clearly separated, try to find titles directly
            for line in generated_text.split('\n'):
                line = line.strip()
                if line.startswith(('1.', '2.', '3.')):
                    title = line.split('.', 1)[1].strip()
                    recommended_titles.append(title)
            # Assume the rest is career recommendation if no clear separator
            if "Recommandation de Carrière:" in generated_text:
                career_recommendation_text = generated_text.split("Recommandation de Carrière:", 1)[1].strip()
            else:
                career_recommendation_text = generated_text.strip() # Take all if no specific section

        print(f"Extracted recommended titles from CV analysis: {recommended_titles}")
        print(f"Extracted career recommendation text: {career_recommendation_text[:200]}...") # Print first 200 chars

        recommended_jobs = []
        for title in recommended_titles:
            found = False
            for job in all_jobs:
                if job.get('title', '').strip().lower() == title.strip().lower():
                    recommended_jobs.append(job)
                    found = True
                    break
            if not found:
                print(f"Warning: Recommended job title '{title}' from CV analysis not found in available jobs.")
        
        return recommended_jobs[:3], career_recommendation_text

    except requests.exceptions.RequestException as e:
        print(f"❌ Error communicating with Ollama API for CV analysis: {e}")
        return [], "Erreur lors de la génération de la recommandation de carrière."
    except json.JSONDecodeError:
        print(f"❌ Error decoding JSON response from Ollama API (CV analysis). Response text: {response.text}")
        return [], "Erreur lors du décodage de la réponse de l'API pour la recommandation de carrière."

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

    print("\nGenerating recommendations from CV text...")
    sample_cv_text = """
    Alice Dupont
    Email: alice.dupont@example.com
    Summary: Highly motivated data scientist with 5 years of experience in machine learning and data analysis.
    Skills: Python, R, SQL, TensorFlow, PyTorch, Scikit-learn, Data Visualization, Statistical Modeling.
    Experience:
    - Data Scientist at Tech Solutions (2020-Present): Developed and deployed ML models, performed data analysis.
    - Junior Analyst at Data Insights (2018-2020): Assisted in data collection and reporting.
    Education:
    - Master's in Data Science, University of Paris
    """
    recommended_jobs_cv, career_text = get_ai_recommendations_from_cv(sample_cv_text, sample_jobs)
    print("\nRecommended Jobs from CV:")
    for job in recommended_jobs_cv:
        print(f"- {job['title']}")
    print("\nCareer Recommendation Text:")
    print(career_text)
