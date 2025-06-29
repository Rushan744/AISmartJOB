import re

def match_job_to_candidate(job, candidate):
    job_skills = [s.strip() for s in re.split(r',\s*', job.get('skills', '').lower())]
    candidate_skills = [s.strip() for s in re.split(r',\s*', candidate.get('compétences', '').lower())]
    common_skills = set(job_skills) & set(candidate_skills)
    skill_score = len(common_skills)

    job_location = job.get('location', '').lower()
    candidate_location = candidate.get('localisation', '').lower()
    if job_location in candidate_location:
        location_score = 0.5  # Partial score for containing location
    elif candidate_location in job_location:
        location_score = 0.5
    else:
        location_score = 0

    # Experience score
    job_experience = job.get('experience_min', 0)
    candidate_experience = candidate.get('expérience', 0)
    experience_score = 0
    if candidate_experience >= job_experience:
        experience_score = 1
        if candidate_experience - job_experience > 5:
            experience_score += 0.5  # Bonus for significantly more experience

    total_score = skill_score + location_score + experience_score
    return total_score

if __name__ == '__main__':
    job = {'skills': 'Python, Java, SQL', 'location': {'display_name': 'Paris'}, 'experience_min': 2}
    candidate = {'compétences': 'Python, SQL', 'localisation': 'Paris', 'expérience': 3}
    score = match_job_to_candidate(job, candidate)
    print(f"Matching score: {score}")
