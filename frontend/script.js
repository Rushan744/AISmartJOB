document.addEventListener('DOMContentLoaded', () => {
    const loginSection = document.getElementById('login-section');
    const mainAppSection = document.getElementById('main-app-section');
    const loginButton = document.getElementById('login-button');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const loginError = document.getElementById('login-error');

    const cvFile = document.getElementById('cvFile');
    const uploadCvButton = document.getElementById('uploadCvButton');
    const uploadStatus = document.getElementById('upload-status');

    const recommendationsLoading = document.getElementById('recommendations-loading');
    const recommendationsError = document.getElementById('recommendations-error');
    const recommendationsResults = document.getElementById('recommendations-results');
    const careerRecommendationText = document.getElementById('career-recommendation-text');
    const jobRecommendationsTableBody = document.querySelector('#job-recommendations-table tbody');

    const skillsLoading = document.getElementById('skills-loading');
    const skillsError = document.getElementById('skills-error');
    const skillsChart = document.getElementById('skills-chart');

    const API_BASE_URL = 'http://127.0.0.1:8000'; // Adjust if your FastAPI runs on a different port/host

    let authToken = localStorage.getItem('authToken');

    const checkLoginStatus = () => {
        if (authToken) {
            loginSection.style.display = 'none';
            mainAppSection.style.display = 'block';
        } else {
            loginSection.style.display = 'block';
            mainAppSection.style.display = 'none';
        }
    };

    loginButton.addEventListener('click', () => {
        const username = usernameInput.value;
        const password = passwordInput.value;
        const credentials = btoa(`${username}:${password}`); // Base64 encode
        
        // For simplicity, we're just storing the token directly.
        // In a real app, you'd send these to a /token endpoint and get a JWT.
        authToken = credentials;
        localStorage.setItem('authToken', authToken);
        checkLoginStatus();
        loginError.classList.add('d-none'); // Hide any previous errors
    });

    uploadCvButton.addEventListener('click', async () => {
        const file = cvFile.files[0];
        if (!file) {
            uploadStatus.innerHTML = '<div class="alert alert-warning">Please select a PDF file.</div>';
            return;
        }
        if (file.type !== 'application/pdf') {
            uploadStatus.innerHTML = '<div class="alert alert-warning">Only PDF files are supported.</div>';
            return;
        }

        uploadStatus.innerHTML = ''; // Clear previous status
        recommendationsError.classList.add('d-none');
        skillsError.classList.add('d-none');
        jobRecommendationsTableBody.innerHTML = '';
        careerRecommendationText.innerHTML = '';
        skillsChart.innerHTML = '';

        recommendationsLoading.classList.remove('d-none');
        skillsLoading.classList.remove('d-none');

        const formData = new FormData();
        formData.append('fichier_cv', file);

        const headers = {
            'accept': 'application/json',
            'Authorization': `Basic ${authToken}`
        };

        try {
            // Call recommend_from_cv API
            const recommendResponse = await fetch(`${API_BASE_URL}/ai_smartjob/recommend_from_cv/`, {
                method: 'POST',
                headers: headers,
                body: formData // FormData handles Content-Type for multipart
            });

            if (!recommendResponse.ok) {
                const errorData = await recommendResponse.json();
                throw new Error(errorData.detail || `HTTP error! status: ${recommendResponse.status}`);
            }

            const recommendData = await recommendResponse.json();
            displayJobRecommendations(recommendData.recommended_jobs, recommendData.career_recommendation_text);

        } catch (error) {
            console.error('Error recommending jobs from CV:', error);
            recommendationsError.textContent = `Error: ${error.message}`;
            recommendationsError.classList.remove('d-none');
        } finally {
            recommendationsLoading.classList.add('d-none');
        }

        // Re-create FormData for the second request as it's consumed by the first
        const formDataSkills = new FormData();
        formDataSkills.append('fichier_cv', file);

        try {
            // Call extract_skills_from_cv API
            const skillsResponse = await fetch(`${API_BASE_URL}/ai_smartjob/extract_skills_from_cv/`, {
                method: 'POST',
                headers: headers,
                body: formDataSkills
            });

            if (!skillsResponse.ok) {
                const errorData = await skillsResponse.json();
                throw new Error(errorData.detail || `HTTP error! status: ${skillsResponse.status}`);
            }

            const skillsData = await skillsResponse.json();
            displayExtractedSkills(skillsData.extracted_skills);

        } catch (error) {
            console.error('Error extracting skills from CV:', error);
            skillsError.textContent = `Error: ${error.message}`;
            skillsError.classList.remove('d-none');
        } finally {
            skillsLoading.classList.add('d-none');
        }
    });

    const displayJobRecommendations = (jobs, careerText) => {
        careerRecommendationText.innerHTML = `<strong>Career Recommendation:</strong><br>${careerText}`;
        jobRecommendationsTableBody.innerHTML = ''; // Clear previous results
        if (jobs.length === 0) {
            jobRecommendationsTableBody.innerHTML = '<tr><td colspan="4">No job recommendations found.</td></tr>';
            return;
        }
        jobs.forEach(job => {
            const row = jobRecommendationsTableBody.insertRow();
            row.insertCell().textContent = job.title;
            row.insertCell().textContent = job.company;
            row.insertCell().textContent = job.location;
            row.insertCell().textContent = job.description;
        });
    };

    const displayExtractedSkills = (skills) => {
        if (skills.length === 0) {
            skillsChart.innerHTML = '<div class="alert alert-info">No skills extracted.</div>';
            return;
        }

        const skillNames = skills.map(s => s.skill);
        const skillScores = skills.map(s => s.score);

        const data = [{
            x: skillNames,
            y: skillScores,
            type: 'bar',
            marker: {
                color: 'rgba(75, 192, 192, 0.6)'
            }
        }];

        const layout = {
            title: 'Extracted Skills from CV',
            xaxis: {
                title: 'Skill'
            },
            yaxis: {
                title: 'Score (0-100)',
                range: [0, 100]
            },
            margin: { t: 50, b: 100 } // Adjust margins to prevent labels from being cut off
        };

        Plotly.newPlot('skills-chart', data, layout);
    };

    // Initial check on page load
    checkLoginStatus();
});