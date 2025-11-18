let currentQuiz = {
    topic: '',
    difficulty: 'medium',
    questions: [],
    currentQuestion: 0,
    userAnswers: [],
    score: 0,
    timeLeft: 60,
    timerInterval: null
};

const API_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadHistory();
});

function setupEventListeners() {
    document.querySelectorAll('.diff-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.diff-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentQuiz.difficulty = e.target.dataset.difficulty;
        });
    });

    document.getElementById('start-quiz-btn').addEventListener('click', startQuiz);
    document.getElementById('submit-answer-btn').addEventListener('click', submitAnswer);
    document.getElementById('next-question-btn').addEventListener('click', nextQuestion);
    document.getElementById('new-quiz-btn').addEventListener('click', resetQuiz);
    
    document.getElementById('topic-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') startQuiz();
    });
}

async function startQuiz() {
    const topic = document.getElementById('topic-input').value.trim();
    if (!topic) {
        alert('Prašome įvesti temą!');
        return;
    }

    currentQuiz.topic = topic;
    const btn = document.getElementById('start-quiz-btn');
    const btnText = btn.querySelector('.btn-text');
    const loader = btn.querySelector('.loader');
    
    btn.disabled = true;
    btnText.textContent = 'Generuojami klausimai...';
    loader.classList.remove('hidden');

    try {
        const response = await fetch(`${API_URL}/generate-questions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: currentQuiz.topic,
                difficulty: currentQuiz.difficulty,
                num_questions: 5
            })
        });

        const data = await response.json();

        if (data.success) {
            currentQuiz.questions = data.questions;
            currentQuiz.currentQuestion = 0;
            currentQuiz.userAnswers = [];
            currentQuiz.score = 0;
            showScreen('quiz-screen');
            displayQuestion();
            startTimer();
        } else {
            alert('Klaida: ' + (data.error || 'Nežinoma klaida'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Nepavyko prisijungti prie serverio.');
    } finally {
        btn.disabled = false;
        btnText.textContent = 'Pradėti Quiz';
        loader.classList.add('hidden');
    }
}

function displayQuestion() {
    const question = currentQuiz.questions[currentQuiz.currentQuestion];
    const total = currentQuiz.questions.length;

    document.getElementById('question-number').textContent = 
        `Klausimas ${currentQuiz.currentQuestion + 1} iš ${total}`;

    const progress = ((currentQuiz.currentQuestion + 1) / total) * 100;
    document.getElementById('progress-fill').style.width = `${progress}%`;

    document.getElementById('question-text').textContent = question.question;

    const answerSection = document.getElementById('answer-section');
    answerSection.innerHTML = '';

    if (question.type === 'multiple_choice') {
        const optionsDiv = document.createElement('div');
        optionsDiv.className = 'answer-options';

        question.options.forEach((option) => {
            const btn = document.createElement('button');
            btn.className = 'answer-option';
            btn.textContent = option;
            btn.dataset.value = option.trim().charAt(0).toUpperCase();
            btn.addEventListener('click', selectOption);
            optionsDiv.appendChild(btn);
        });

        answerSection.appendChild(optionsDiv);
    } else {
        const input = document.createElement('input');
        input.type = 'text';
        input.id = 'short-answer';
        input.className = 'short-answer-input';
        input.placeholder = 'Įveskite atsakymą...';
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') submitAnswer();
        });
        answerSection.appendChild(input);
    }

    document.getElementById('feedback-section').classList.add('hidden');
    document.getElementById('submit-answer-btn').classList.remove('hidden');
    document.getElementById('next-question-btn').classList.add('hidden');
}

function selectOption(e) {
    document.querySelectorAll('.answer-option').forEach(btn => {
        btn.classList.remove('selected');
    });
    e.target.classList.add('selected');
}

function startTimer() {
    currentQuiz.timeLeft = 60;
    updateTimerDisplay();

    clearInterval(currentQuiz.timerInterval);
    currentQuiz.timerInterval = setInterval(() => {
        currentQuiz.timeLeft--;
        updateTimerDisplay();

        if (currentQuiz.timeLeft <= 0) {
            clearInterval(currentQuiz.timerInterval);
            submitAnswer();
        }
    }, 1000);
}

function updateTimerDisplay() {
    const timerEl = document.getElementById('timer');
    const timeLeftEl = document.getElementById('time-left');
    
    timeLeftEl.textContent = `${currentQuiz.timeLeft}s`;
    
    if (currentQuiz.timeLeft < 10) {
        timerEl.classList.add('warning');
    } else {
        timerEl.classList.remove('warning');
    }
}

async function submitAnswer() {
    clearInterval(currentQuiz.timerInterval);

    const question = currentQuiz.questions[currentQuiz.currentQuestion];
    let userAnswer;

    if (question.type === 'multiple_choice') {
        const selected = document.querySelector('.answer-option.selected');
        userAnswer = selected ? selected.dataset.value : '';
    } else {
        const input = document.getElementById('short-answer');
        userAnswer = input ? input.value : '';
    }

    try {
        const response = await fetch(`${API_URL}/check-answer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                user_answer: userAnswer
            })
        });

        const data = await response.json();

        if (data.success) {
            const isCorrect = data.is_correct;
            const feedback = data.feedback;

            currentQuiz.userAnswers.push({
                question: question,
                user_answer: userAnswer,
                is_correct: isCorrect
            });

            if (isCorrect) {
                currentQuiz.score++;
            }

            displayFeedback(feedback);

            document.getElementById('submit-answer-btn').classList.add('hidden');
            document.getElementById('next-question-btn').classList.remove('hidden');

            if (question.type === 'multiple_choice') {
                document.querySelectorAll('.answer-option').forEach(btn => {
                    btn.disabled = true;
                    if (btn.dataset.value === question.correct) {
                        btn.classList.add('correct');
                    } else if (btn.classList.contains('selected') && !isCorrect) {
                        btn.classList.add('incorrect');
                    }
                });
            } else {
                document.getElementById('short-answer').disabled = true;
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Klaida tikrinant atsakymą');
    }
}

function displayFeedback(feedback) {
    const feedbackSection = document.getElementById('feedback-section');
    feedbackSection.innerHTML = '';
    feedbackSection.className = `feedback ${feedback.is_correct ? 'correct' : 'incorrect'}`;

    const header = document.createElement('div');
    header.className = 'feedback-header';
    header.textContent = feedback.is_correct ? '✓ Teisingai!' : '✗ Neteisingai!';
    feedbackSection.appendChild(header);

    if (!feedback.is_correct) {
        const correctAnswer = document.createElement('p');
        correctAnswer.innerHTML = `<strong>Teisingas atsakymas:</strong> ${feedback.correct_answer}`;
        feedbackSection.appendChild(correctAnswer);
    }

    if (feedback.explanation) {
        const explanation = document.createElement('p');
        explanation.textContent = feedback.explanation;
        feedbackSection.appendChild(explanation);
    }

    feedbackSection.classList.remove('hidden');
}

function nextQuestion() {
    currentQuiz.currentQuestion++;

    if (currentQuiz.currentQuestion < currentQuiz.questions.length) {
        displayQuestion();
        startTimer();
    } else {
        finishQuiz();
    }
}

async function finishQuiz() {
    clearInterval(currentQuiz.timerInterval);

    try {
        const response = await fetch(`${API_URL}/submit-quiz`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic: currentQuiz.topic,
                difficulty: currentQuiz.difficulty,
                results: currentQuiz.userAnswers.map(a => [
                    a.question,
                    a.user_answer,
                    a.is_correct
                ])
            })
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data.score, data.grade);
            loadHistory();
        }
    } catch (error) {
        console.error('Error:', error);

        const score = {
            correct: currentQuiz.score,
            total: currentQuiz.questions.length,
            percentage: ((currentQuiz.score / currentQuiz.questions.length) * 100).toFixed(1)
        };

        displayResults(score, 'Nepavyko gauti galutinio įvertinimo');
    }
}

function displayResults(score, grade) {
    showScreen('results-screen');
    
    // Display difficulty in Lithuanian
    const difficultyText = {
        'easy': 'Lengvas',
        'medium': 'Vidutinis',
        'hard': 'Sunkus'
    };
    
    document.getElementById('results-topic').textContent = 
        `Tema: ${currentQuiz.topic} (${difficultyText[currentQuiz.difficulty] || currentQuiz.difficulty})`;
    
    document.getElementById('score-percentage').textContent = 
        `${score.percentage}%`;
    
    document.getElementById('score-text').textContent = 
        `${score.correct} iš ${score.total} teisingų atsakymų`;
    
    document.getElementById('grade-message').textContent = grade;
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_URL}/history?limit=5`);
        const data = await response.json();

        if (data.success && data.history.length > 0) {
            displayHistory(data.history);
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayHistory(history) {
    const historyCard = document.getElementById('history-card');
    const historyList = document.getElementById('history-list');

    historyList.innerHTML = '';

    history.forEach(item => {
        const div = document.createElement('div');
        div.className = 'history-item';
        div.innerHTML = `
            <div class="history-info">
                <h3>${item.topic}</h3>
                <p>${item.date}</p>
            </div>
            <div class="history-score">
                <div class="percentage">${item.percentage}%</div>
                <div class="score">${item.score}/${item.total}</div>
            </div>
        `;
        historyList.appendChild(div);
    });

    historyCard.classList.remove('hidden');
}

function resetQuiz() {
    clearInterval(currentQuiz.timerInterval);
    currentQuiz = {
        topic: '',
        difficulty: 'medium',
        questions: [],
        currentQuestion: 0,
        userAnswers: [],
        score: 0,
        timeLeft: 60,
        timerInterval: null
    };

    document.getElementById('topic-input').value = '';
    document.querySelectorAll('.diff-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.difficulty === 'medium') {
            btn.classList.add('active');
        }
    });

    showScreen('home-screen');
}

function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(screen => {
        screen.classList.remove('active');
    });
    document.getElementById(screenId).classList.add('active');
}