import pandas as pd
from faker import Faker

fake = Faker('fr_FR')

def generate_candidate():
    skills = set(fake.words(nb=5, ext_word_list=['Python', 'SQL', 'Java', 'Spring', 'React', 'Angular', 'Node.js', 'C++', 'JavaScript', 'AWS', 'Docker', 'Machine Learning', 'Data Analysis', 'Cloud Computing', 'Cybersecurity', 'Project Management', 'Communication', 'Teamwork', 'Problem Solving']))  # Added more skills
    return {
        'id': fake.random_number(digits=5),
        'nom': fake.name(),
        'email': fake.email(),
        'compétences': ', '.join(skills),  # Removed duplicates
        'expérience': fake.random_int(min=0, max=10),
        'localisation': fake.city(),
        'secteur': fake.job()
    }

def generate_candidates_csv(num_candidates=10):
    candidates = [generate_candidate() for _ in range(num_candidates)]
    df = pd.DataFrame(candidates)
    df.to_csv('D:/Smartjob_working_withfastapi/emploi-matching/data/candidats.csv', index=False)

if __name__ == '__main__':
    generate_candidates_csv()
