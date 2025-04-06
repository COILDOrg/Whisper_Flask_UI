// Theme initialization and toggle functionality
(function() {
    // Check for saved theme preference or use device preference
    function getInitialTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            return savedTheme;
        }
        
        // Check for device preference
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    // Apply theme to document
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    }
    
    // Initialize theme
    const initialTheme = getInitialTheme();
    applyTheme(initialTheme);
    
    // Make sure the DOM is loaded before adding event listeners
    document.addEventListener('DOMContentLoaded', function() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            // Update toggle button UI based on current theme
            updateToggleUI(initialTheme);
            
            // Add event listener to toggle button
            themeToggle.addEventListener('click', function() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                applyTheme(newTheme);
                updateToggleUI(newTheme);
            });
        }
    });
    
    // Update toggle button UI
    function updateToggleUI(theme) {
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        if (!themeToggle || !themeIcon) return;
        
        if (theme === 'dark') {
            // For SVG access through img, we'll add a class to the button
            themeToggle.classList.add('dark-mode');
            themeToggle.classList.remove('light-mode');
            themeToggle.setAttribute('aria-label', 'Switch to light mode');
        } else {
            themeToggle.classList.add('light-mode');
            themeToggle.classList.remove('dark-mode');
            themeToggle.setAttribute('aria-label', 'Switch to dark mode');
        }
    }
})();
