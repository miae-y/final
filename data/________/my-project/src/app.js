document.addEventListener('DOMContentLoaded', () => {
    // --- Login Form Selection ---
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const errorMessage = document.getElementById('errorMessage');
    
    // --- View Container Selection ---
    const loginView = document.getElementById('loginView');
    const dashboardView = document.getElementById('dashboardView');
    
    // --- Sidebar Menu Selection ---
    const menuItems = document.querySelectorAll('.menu-item');
    const contentPanels = document.querySelectorAll('.content-panel');
    
    // --- Action Buttons ---
    const logoutBtn = document.getElementById('logoutBtn');

    // Default credentials
    const DEFAULT_USER = 'admin';
    const DEFAULT_PASS = 'guess';

    // 1. Handle Login Form Submit
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const username = usernameInput.value.trim();
            const password = passwordInput.value;

            if (username === DEFAULT_USER && password === DEFAULT_PASS) {
                // Clear any error messages
                errorMessage.style.display = 'none';
                
                // Switch views with smooth transition
                loginView.style.transition = 'opacity 0.4s ease';
                loginView.style.opacity = '0';
                
                setTimeout(() => {
                    loginView.style.display = 'none';
                    dashboardView.style.display = 'grid';
                    dashboardView.style.opacity = '0';
                    
                    // Trigger reflow to enable transition
                    dashboardView.getBoundingClientRect();
                    
                    dashboardView.style.transition = 'opacity 0.4s ease';
                    dashboardView.style.opacity = '1';
                }, 400);
            } else {
                // Display error message
                errorMessage.innerText = "사용자 이름 또는 비밀번호가 잘못되었습니다. (ID: admin, PW: guess)";
                errorMessage.style.display = 'block';
                
                // Shake effect on error
                const card = document.querySelector('.login-card');
                card.style.animation = 'none';
                // Trigger reflow
                card.getBoundingClientRect();
                card.style.animation = 'shake 0.4s ease';
            }
        });
    }

    // 2. Handle Sidebar Menu Click Navigation
    menuItems.forEach(item => {
        item.addEventListener('click', () => {
            // Remove active class from all menu items
            menuItems.forEach(el => el.classList.remove('active'));
            // Add active class to clicked item
            item.classList.add('active');
            
            // Get target panel id
            const targetPanelId = item.getAttribute('data-target');
            
            // Hide all panels and show the active one
            contentPanels.forEach(panel => {
                panel.classList.remove('active');
                if (panel.id === targetPanelId) {
                    panel.classList.add('active');
                }
            });
        });
    });

    // 3. Handle Logout Action
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            // Reset input fields
            usernameInput.value = '';
            passwordInput.value = '';
            
            // Transition back to login view
            dashboardView.style.transition = 'opacity 0.4s ease';
            dashboardView.style.opacity = '0';
            
            setTimeout(() => {
                dashboardView.style.display = 'none';
                loginView.style.display = 'flex';
                loginView.style.opacity = '0';
                
                loginView.getBoundingClientRect();
                
                loginView.style.transition = 'opacity 0.4s ease';
                loginView.style.opacity = '1';
            }, 400);
        });
    }
});
