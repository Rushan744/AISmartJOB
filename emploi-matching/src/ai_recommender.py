import requests
import json
import re

OLLAMA_API_URL = "http://host.docker.internal:11434/api/generate"

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
        f"en français"
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
        f"en français"
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
        career_recommendation_text = ""
        job_section_raw = generated_text # Initialize with full text

        # First, try to extract the career recommendation text by splitting at its header
        parts_by_career_header = generated_text.split("Recommandation de Carrière:", 1)
        if len(parts_by_career_header) > 1:
            job_section_raw = parts_by_career_header[0] # Content before career recommendation
            career_recommendation_text = parts_by_career_header[1].strip() # Actual career recommendation text
        else:
            # If "Recommandation de Carrière:" header is not found, assume the entire text is the recommendation
            # and we will try to extract jobs from it.
            career_recommendation_text = generated_text.strip()

        # --- Robust Job Title Extraction ---
        available_job_titles = [job.get('title', '').strip().lower() for job in all_jobs]
        found_titles_from_ai = []

        # Strategy 1: Look for explicit numbered/bulleted lists in the *entire* generated text
        # This is because the AI might put the list anywhere.
        list_pattern = re.compile(r'^\s*(?:\d+\.|\-)\s*(.+)$', re.MULTILINE)
        for match in list_pattern.finditer(generated_text):
            extracted_title_candidate = match.group(1).strip()
            # Check if this extracted title is close to any actual job title
            for actual_title in available_job_titles:
                if actual_title in extracted_title_candidate.lower() or extracted_title_candidate.lower() in actual_title:
                    found_titles_from_ai.append(actual_title)
                    break
        
        # Strategy 2: Look for embedded job titles within the text, matching against available job titles
        # This is a more general approach if the AI doesn't follow the list format.
        for actual_title in available_job_titles:
            # Use word boundaries to avoid partial matches (e.g., "developer" matching "web developer")
            # and escape special characters in the title for regex safety.
            if re.search(r'\b' + re.escape(actual_title) + r'\b', generated_text.lower()):
                found_titles_from_ai.append(actual_title)

        # Filter out potential duplicates and ensure we only take unique titles, preserving order
        recommended_titles = list(dict.fromkeys(found_titles_from_ai))
        
        # Limit to top 3 recommendations as requested in the prompt
        recommended_titles = recommended_titles[:3]

        # --- Clean up career_recommendation_text ---
        # Remove the lines that were identified as job titles from the career_recommendation_text.
        # This is crucial to avoid redundancy in the final output.
        if recommended_titles and career_recommendation_text:
            lines = career_recommendation_text.split('\n')
            cleaned_lines = []
            for line in lines:
                is_job_title_line = False
                # Check if the line contains any of the extracted job titles (case-insensitive)
                for title in recommended_titles:
                    if re.search(r'\b' + re.escape(title) + r'\b', line.lower()):
                        is_job_title_line = True
                        break
                # Also remove the "1. Jobs Recommandés :" and "2. Recommandation de Carrière :" lines if they appear
                if re.match(r'^\s*\d+\.\s*Jobs Recommandés\s*:\s*$', line, re.IGNORECASE) or \
                   re.match(r'^\s*\d+\.\s*Recommandation de Carrière\s*:\s*$', line, re.IGNORECASE):
                    is_job_title_line = True

                if not is_job_title_line and line.strip(): # Keep non-job title/header lines that are not empty
                    cleaned_lines.append(line)
            career_recommendation_text = "\n".join(cleaned_lines).strip()

        # Final fallback: if after all extraction and cleanup, the career_recommendation_text is empty,
        # but the original generated text had content, use the original text as a fallback.
        if not career_recommendation_text and generated_text.strip():
            career_recommendation_text = generated_text.strip()

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

def extract_skills_with_scores_from_cv(cv_text: str):
    """
    Extracts 10 key skills from the CV text and assigns a score (0-100) to each
    using Mistral via Ollama.
    
    Args:
        cv_text (str): The extracted text content of the candidate's CV.
                          
    Returns:
        list: A list of dictionaries, each with 'skill' (str) and 'score' (int).
    """
    prompt = (
        f"en français"
        f"En tant qu'expert en analyse de CV, veuillez extraire les 10 compétences clés "
        f"du CV suivant et attribuer un score de pertinence entre 0 et 100 pour chaque compétence. "
        f"Le score doit refléter la force ou la présence de la compétence dans le CV. "
        f"Veuillez formater votre réponse comme une liste JSON, où chaque élément est un objet "
        f"avec les clés 'skill' (string) et 'score' (integer).\n\n"
        f"CV:\n```\n{cv_text}\n```\n\n"
        f"Exemple de format de réponse:\n"
        f"[\n"
        f"  {{\"skill\": \"Python\", \"score\": 90}},\n"
        f"  {{\"skill\": \"Gestion de projet\", \"score\": 75}}\n"
        f"]\n"
        f"Assurez-vous que la réponse est un JSON valide et ne contient aucun autre texte."
    )
    print(f"Prompt sent to Mistral for skill extraction:\n{prompt[:500]}...")

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
        generated_text = result.get('response', '').strip()
        print(f"Generated text from Mistral (skill extraction):\n{generated_text}")
        
        # Attempt to parse the JSON response
        skills_data = json.loads(generated_text)
        
        # Validate the structure and content
        if not isinstance(skills_data, list):
            raise ValueError("Expected a JSON list.")
        
        extracted_skills = []
        for item in skills_data:
            if not isinstance(item, dict) or "skill" not in item or "score" not in item:
                raise ValueError("Each item in the JSON list must be an object with 'skill' and 'score'.")
            if not isinstance(item["skill"], str) or not isinstance(item["score"], int):
                raise ValueError("Skill must be a string and score must be an integer.")
            
            # Ensure score is within 0-100
            item["score"] = max(0, min(100, item["score"]))
            extracted_skills.append(item)
        
        # Return up to 10 skills
        return extracted_skills[:10]

    except requests.exceptions.RequestException as e:
        print(f"❌ Error communicating with Ollama API for skill extraction: {e}")
        return []
    except json.JSONDecodeError:
        print(f"❌ Error decoding JSON response from Ollama API (skill extraction). Response text: {generated_text}")
        return []
    except ValueError as e:
        print(f"❌ Error parsing or validating skill extraction response: {e}. Raw response: {generated_text}")
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

    print("\nExtracting skills from CV text...")
    extracted_skills = extract_skills_with_scores_from_cv(sample_cv_text)
    print("\nExtracted Skills with Scores:")
    for skill_item in extracted_skills:
        print(f"- {skill_item['skill']}: {skill_item['score']}")
