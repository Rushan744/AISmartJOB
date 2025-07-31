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

    const API_BASE_URL = 'http://127.0.0.1:8000'; // Ajustez si votre FastAPI s'exécute sur un port/hôte différent

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

    loginButton.addEventListener('click', async () => {
        const username = usernameInput.value;
        const password = passwordInput.value;
        const credentials = btoa(`${username}:${password}`); // Encodage Base64

        try {
            // Tenter de se connecter en récupérant les données utilisateur (nécessite une authentification)
            const loginResponse = await fetch(`${API_BASE_URL}/users/`, {
                method: 'GET',
                headers: {
                    'accept': 'application/json',
                    'Authorization': `Basic ${credentials}`
                }
            });

            if (loginResponse.ok) {
                authToken = credentials;
                localStorage.setItem('authToken', authToken);
                checkLoginStatus();
                loginError.classList.add('d-none');
            } else if (loginResponse.status === 401) {
                // Si la connexion échoue (401 Non autorisé), essayer de créer l'utilisateur
                const createUserResponse = await fetch(`${API_BASE_URL}/users/`, {
                    method: 'POST',
                    headers: {
                        'accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ username, password })
                });

                if (createUserResponse.ok) {
                    // Utilisateur créé avec succès, maintenant se connecter
                    authToken = credentials;
                    localStorage.setItem('authToken', authToken);
                    checkLoginStatus();
                    loginError.classList.add('d-none');
                } else {
                    const errorData = await createUserResponse.json();
                    loginError.textContent = errorData.detail || 'Échec de la création de l\'utilisateur.';
                    loginError.classList.remove('d-none');
                }
            } else {
                const errorData = await loginResponse.json();
                loginError.textContent = errorData.detail || 'Échec de la connexion.';
                loginError.classList.remove('d-none');
            }
        } catch (error) {
            console.error('Erreur de connexion/création d\'utilisateur :', error);
            loginError.textContent = `Une erreur inattendue s'est produite : ${error.message}`;
            loginError.classList.remove('d-none');
        }
    });

    uploadCvButton.addEventListener('click', async () => {
        const file = cvFile.files[0];
        if (!file) {
            uploadStatus.innerHTML = '<div class="alert alert-warning">Veuillez sélectionner un fichier PDF.</div>';
            return;
        }
        if (file.type !== 'application/pdf') {
            uploadStatus.innerHTML = '<div class="alert alert-warning">Seuls les fichiers PDF sont supportés.</div>';
            return;
        }

        uploadStatus.innerHTML = ''; // Effacer le statut précédent
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
            // Appeler l'API recommend_from_cv
            const recommendResponse = await fetch(`${API_BASE_URL}/ai_smartjob/recommend_from_cv/`, {
                method: 'POST',
                headers: headers,
                body: formData // FormData gère Content-Type pour multipart
            });

            if (!recommendResponse.ok) {
                const errorData = await recommendResponse.json();
                throw new Error(errorData.detail || `Erreur HTTP ! statut : ${recommendResponse.status}`);
            }

            const recommendData = await recommendResponse.json();
            displayJobRecommendations(recommendData.recommended_jobs, recommendData.career_recommendation_text);

        } catch (error) {
            console.error('Erreur lors de la recommandation d\'emplois à partir du CV :', error);
            recommendationsError.textContent = `Erreur : ${error.message}`;
            recommendationsError.classList.remove('d-none');
        } finally {
            recommendationsLoading.classList.add('d-none');
        }

        // Recréer FormData pour la deuxième requête car il est consommé par la première
        const formDataSkills = new FormData();
        formDataSkills.append('fichier_cv', file);

        try {
            // Appeler l'API extract_skills_from_cv
            const skillsResponse = await fetch(`${API_BASE_URL}/ai_smartjob/extract_skills_from_cv/`, {
                method: 'POST',
                headers: headers,
                body: formDataSkills
            });

            if (!skillsResponse.ok) {
                const errorData = await skillsResponse.json();
                throw new Error(errorData.detail || `Erreur HTTP ! statut : ${skillsResponse.status}`);
            }

            const skillsData = await skillsResponse.json();
            displayExtractedSkills(skillsData.extracted_skills);

        } catch (error) {
            console.error('Erreur lors de l\'extraction des compétences du CV :', error);
            skillsError.textContent = `Erreur : ${error.message}`;
            skillsError.classList.remove('d-none');
        } finally {
            skillsLoading.classList.add('d-none');
        }
    });

    const displayJobRecommendations = (jobs, careerText) => {
        careerRecommendationText.innerHTML = `<strong>Recommandation de carrière :</strong><br>${careerText}`;
        jobRecommendationsTableBody.innerHTML = ''; // Effacer les résultats précédents
        if (jobs.length === 0) {
            jobRecommendationsTableBody.innerHTML = '<tr><td colspan="4">Aucune recommandation d\'emploi trouvée.</td></tr>';
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
            skillsChart.innerHTML = '<div class="alert alert-info">Aucune compétence extraite.</div>';
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
            title: 'Compétences extraites du CV',
            xaxis: {
                title: 'Compétence'
            },
            yaxis: {
                title: 'Score (0-100)',
                range: [0, 100]
            },
            margin: { t: 50, b: 100 } // Ajuster les marges pour éviter que les étiquettes ne soient coupées
        };

        Plotly.newPlot('skills-chart', data, layout);
    };

    const feedbackForm = document.getElementById('feedback-form');
    const submitFeedbackButton = document.getElementById('submitFeedbackButton');
    const feedbackStatus = document.getElementById('feedback-status');

    submitFeedbackButton.addEventListener('click', async (event) => {
        event.preventDefault(); // Empêcher le rechargement de la page

        feedbackStatus.innerHTML = ''; // Clear previous status

        const selectedRating = document.querySelector('input[name="rating"]:checked');
        const comment = document.getElementById('comment').value;

        if (!selectedRating) {
            feedbackStatus.innerHTML = '<div class="alert alert-warning">Veuillez sélectionner une note.</div>';
            return;
        }

        const rating = parseInt(selectedRating.value);
        console.log('Feedback button clicked!'); // New log
        console.log('Attempting to submit feedback with:', { rating, comment });

        try {
            const response = await fetch(`${API_BASE_URL}/feedback/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Basic ${authToken}`
                },
                body: JSON.stringify({ rating, comment })
            });

            console.log('Feedback API raw response:', response); // New log
            console.log('Feedback API response status:', response.status); // New log
            console.log('Feedback API response statusText:', response.statusText); // New log

            if (response.ok) {
                feedbackStatus.innerHTML = '<div class="alert alert-success">Feedback soumis avec succès ! Merci.</div>';
                feedbackForm.reset(); // Reset the form
            } else {
                const errorData = await response.json();
                console.error('Feedback API error data:', errorData);
                feedbackStatus.innerHTML = `<div class="alert alert-danger">Erreur lors de la soumission du feedback : ${errorData.detail || response.statusText}</div>`;
            }
        } catch (error) {
            console.error('Erreur lors de la soumission du feedback :', error);
            feedbackStatus.innerHTML = `<div class="alert alert-danger">Une erreur inattendue s'est produite : ${error.message}</div>`;
        }
    });

    // Vérification initiale au chargement de la page
    checkLoginStatus();
});
