// app.js
console.log("app.js file is running!");

document.addEventListener('DOMContentLoaded', () => {
    // ... rest of your code
});


document.addEventListener('DOMContentLoaded', () => {
    // --- Theme Toggle Logic (with localStorage) ---
    const themeToggleBtn = document.getElementById('theme-toggle');

    const applyTheme = () => {
        const savedTheme = localStorage.getItem('theme') || 'light';
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
        } else {
            document.body.classList.remove('dark-mode');
        }
    };

    const toggleTheme = () => {
        document.body.classList.toggle('dark-mode');
        let currentTheme = document.body.classList.contains('dark-mode') ? 'dark' : 'light';
        localStorage.setItem('theme', currentTheme);
    };

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', toggleTheme);
    }
    
    applyTheme(); // Apply theme on initial load

    // --- Two-Step Login Logic ---
    const stepUsername = document.getElementById('step-username');
    const stepPassword = document.getElementById('step-password');
    const nextBtn = document.getElementById('next-btn');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const lockedUsernameDisplay = document.getElementById('locked-username');
    
    if (nextBtn) { // This ensures the code only runs on the login page
        nextBtn.addEventListener('click', () => {
            if (usernameInput.value.trim() !== '') {
                lockedUsernameDisplay.textContent = usernameInput.value;
                stepUsername.classList.add('hidden');
                stepPassword.classList.remove('hidden');
                passwordInput.focus();
            }
        });

        usernameInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                nextBtn.click();
            }
        });
    }
});


document.addEventListener('DOMContentLoaded', () => {
    const stepUsername = document.getElementById('step-username');
    const stepPassword = document.getElementById('step-password');
    const nextBtn = document.getElementById('next-btn');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const lockedUsernameDisplay = document.getElementById('locked-username');
    const loginForm = document.getElementById('login-form');

    nextBtn.addEventListener('click', () => {
        // If username is not empty
        if (usernameInput.value.trim() !== '') {
            lockedUsernameDisplay.textContent = usernameInput.value;
            stepUsername.classList.add('hidden');
            stepPassword.classList.remove('hidden');
            passwordInput.focus();
        }
    });

    // Allow pressing Enter on username field to go to the next step
    usernameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent form submission
            nextBtn.click();
        }
    });

// Theme toggle logic
const themeToggleBtn = document.getElementById('theme-toggle');

const applyTheme = (theme) => {
    if (theme === 'dark') {
        document.body.classList.add('dark-mode');
    } else {
        document.body.classList.remove('dark-mode');
    }
};

const toggleTheme = () => {
    const isDarkMode = document.body.classList.toggle('dark-mode');
    const currentTheme = isDarkMode ? 'dark' : 'light';
    localStorage.setItem('theme', currentTheme);
};

// Apply saved theme on page load
const savedTheme = localStorage.getItem('theme') || 'light';
applyTheme(savedTheme);

themeToggleBtn.addEventListener('click', toggleTheme);
});

