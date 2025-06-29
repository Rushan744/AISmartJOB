from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io

def create_pdf(text_content, filename="dummy_cv.pdf"):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    textobject = p.beginText()
    textobject.setTextOrigin(100, 750)
    
    # Split text into lines and add them
    for line in text_content.split('\n'):
        textobject.textLine(line)
    
    p.drawText(textobject)
    p.save()
    
    with open(filename, 'wb') as f:
        f.write(buffer.getvalue())
    print(f"Created {filename} with dummy content.")

if __name__ == "__main__":
    dummy_text = """
    Curriculum Vitae

    John Doe
    Email: john.doe@example.com
    Phone: +1234567890
    Location: Paris, France

    Summary:
    Highly motivated software engineer with 5 years of experience in Python and web development.
    Passionate about building scalable and efficient applications.

    Skills:
    - Programming Languages: Python, JavaScript, SQL
    - Frameworks: FastAPI, Flask, React
    - Databases: PostgreSQL, MongoDB, SQLite
    - Tools: Git, Docker, AWS
    - Concepts: RESTful APIs, Microservices, Agile Development

    Experience:
    Senior Software Engineer | Tech Innovations Inc. | Paris, France
    Jan 2022 - Present
    - Led the development of a new microservices-based platform using FastAPI and PostgreSQL.
    - Implemented robust API endpoints and integrated third-party services.
    - Mentored junior developers and conducted code reviews.

    Software Engineer | Web Solutions Co. | Lyon, France
    Jul 2019 - Dec 2021
    - Developed and maintained web applications using Flask and MongoDB.
    - Collaborated with cross-functional teams to define, design, and ship new features.
    - Optimized database queries, resulting in a 20% performance improvement.

    Education:
    Master of Science in Computer Science | University of Paris | 2019
    Bachelor of Science in Software Engineering | University of Lyon | 2017
    """
    create_pdf(dummy_text)