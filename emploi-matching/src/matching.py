import requests
import json

OLLAMA_API_URL = "http://localhost:11434/api/generate"

def match_job_to_candidate(job, candidate):
    """
    Calculates a matching score between a job and a candidate using Mistral via Ollama.
    
    Args:
        job (dict): A dictionary containing job details (e.g., 'title', 'description', 'location').
        candidate (dict): A dictionary containing candidate details (e.g., 'nom', 'compétences', 'expérience', 'localisation').
                          
    Returns:
        float: A matching score between 0 and 100, or 0 if an error occurs.
    """
    job_title = job.get('title', 'N/A')
    job_description = job.get('description', 'N/A')
    job_location = job.get('location', 'N/A')
    job_company = job.get('company', 'N/A')

    candidate_name = candidate.get('nom', 'N/A')
    candidate_skills = candidate.get('compétences', 'N/A')
    candidate_experience = candidate.get('expérience', 'N/A')
    candidate_location = candidate.get('localisation', 'N/A')
    candidate_sector = candidate.get('secteur', 'N/A')

    prompt = (
        f"En tant qu'expert en matching de profils, évaluez la pertinence du candidat suivant pour le poste proposé.\n\n"
        f"Détails du Candidat:\n"
        f"- Nom: {candidate_name}\n"
        f"- Compétences: {candidate_skills}\n"
        f"- Expérience: {candidate_experience} ans\n"
        f"- Localisation: {candidate_location}\n"
        f"- Secteur: {candidate_sector}\n\n"
        f"Détails du Poste:\n"
        f"- Titre: {job_title}\n"
        f"- Entreprise: {job_company}\n"
        f"- Localisation: {job_location}\n"
        f"- Description: {job_description}\n\n"
        f"Sur une échelle de 0 à 100, où 0 est aucune correspondance et 100 est une correspondance parfaite, "
        f"quel est le score de correspondance entre ce candidat et ce poste? "
        f"Veuillez ne répondre qu'avec le score numérique."
    )
    print(f"Prompt sent to Mistral for matching:\n{prompt[:500]}...")

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
        print(f"Generated text from Mistral (matching): {generated_text}")
        
        # extract a numerical score using regex
        import re
        score_match = re.search(r'(\d+(\.\d+)?)', generated_text)
        if score_match:
            try:
                score = float(score_match.group(1))
                return max(0.0, min(100.0, score)) # Ensure score is within 0-100
            except ValueError:
                print(f"Warning: Could not convert extracted number '{score_match.group(1)}' to float. Returning 0.")
                return 0.0
        else:
            print(f"Warning: Could not find a numerical score in Mistral response: '{generated_text}'. Returning 0.")
            return 0.0

    except requests.exceptions.RequestException as e:
        print(f"❌ Error communicating with Ollama API for matching: {e}")
        return 0.0
    except json.JSONDecodeError:
        print(f"❌ Error decoding JSON response from Ollama API (matching). Response text: {response.text}")
        return 0.0

if __name__ == '__main__':
    # Example Usage (for testing purposes)
    job_example = {
        'title': 'Développeur Python Senior',
        'company': 'Tech Innovations',
        'location': 'Paris',
        'description': 'Recherche un développeur Python senior avec expérience en FastAPI et bases de données SQL.'
    }
    candidate_example = {
        'nom': 'Alice Dupont',
        'compétences': 'Python, FastAPI, SQL, Machine Learning',
        'expérience': 5,
        'localisation': 'Paris',
        'secteur': 'IT'
    }
    
    score = match_job_to_candidate(job_example, candidate_example)
    print(f"Matching score for example: {score}")

    job_example_no_match = {
        'title': 'Designer Graphique Junior',
        'company': 'Creative Studio',
        'location': 'Lyon',
        'description': 'Création de visuels pour des campagnes marketing.'
    }
    candidate_example_no_match = {
        'nom': 'Bob Martin',
        'compétences': 'Java, Spring Boot, Microservices',
        'expérience': 3,
        'localisation': 'Marseille',
        'secteur': 'IT'
    }
    score_no_match = match_job_to_candidate(job_example_no_match, candidate_example_no_match)
    print(f"Matching score for no match example: {score_no_match}")
