// Common JavaScript functions for VirtuWellness Hub

// Breathing exercise functionality
let breathingInterval;

function startBreathing() {
    const breathingText = document.querySelector('.breathing-text');
    const btn = document.querySelector('.btn-primary');
    
    if (btn.textContent === 'Start Exercise') {
        btn.textContent = 'Stop Exercise';
        breathingInterval = setInterval(() => {
            breathingText.textContent = 'Breathe in...';
            setTimeout(() => {
                breathingText.textContent = 'Hold...';
                setTimeout(() => {
                    breathingText.textContent = 'Breathe out...';
                }, 4000);
            }, 4000);
        }, 12000);
    } else {
        btn.textContent = 'Start Exercise';
        clearInterval(breathingInterval);
        breathingText.textContent = 'Breathe in... Breathe out...';
    }
}

// Activity start function
function startActivity(activity) {
    switch(activity) {
        case 'meditation':
            showMeditationGuide();
            break;
        case 'journaling':
            showJournalingPrompt();
            break;
        case 'relaxation':
            startRelaxationExercise();
            break;
        case 'gratitude':
            showGratitudePrompt();
            break;
        case 'walking':
            startWalkingGuide();
            break;
        case 'bodyscan':
            startBodyScan();
            break;
        default:
            alert('Starting ' + activity + ' activity...');
    }
}

// Meditation guide
function showMeditationGuide() {
    alert("Find a comfortable position and focus on your breath. We'll guide you through a 5-minute meditation.");
    // Add more sophisticated meditation guide implementation
}

// Journaling prompt
function showJournalingPrompt() {
    const prompts = [
        "What are three things you're grateful for today?",
        "How are you feeling right now, and why?",
        "What's one thing you're looking forward to?",
        "What's one challenge you faced today, and how did you handle it?"
    ];
    const randomPrompt = prompts[Math.floor(Math.random() * prompts.length)];
    alert("Today's journaling prompt:\n\n" + randomPrompt);
    // Add more sophisticated journaling implementation
}

// Relaxation exercise
function startRelaxationExercise() {
    alert("Let's begin progressive muscle relaxation. Start by tensing and relaxing your toes...");
    // Add more sophisticated relaxation guide implementation
}

// Gratitude practice
function showGratitudePrompt() {
    alert("Take a moment to reflect on three things that brought you joy today...");
    // Add more sophisticated gratitude practice implementation
}

// Walking meditation guide
function startWalkingGuide() {
    alert("Find a quiet place to walk. Focus on each step, feeling the sensation of your feet touching the ground...");
    // Add more sophisticated walking meditation guide implementation
}

// Body scan meditation
function startBodyScan() {
    alert("Find a comfortable position lying down. We'll guide you through a full body scan meditation...");
    // Add more sophisticated body scan implementation
}

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
});
