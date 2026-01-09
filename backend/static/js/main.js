// Care Navigator - Main JavaScript
// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', function() {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.getElementById('navMenu');
    const navOverlay = document.getElementById('navOverlay');
    
    if (navToggle && navMenu) {
        // Toggle navigation
        navToggle.addEventListener('click', function() {
            navToggle.classList.toggle('active');
            navMenu.classList.toggle('active');
            navOverlay.classList.toggle('active');
            document.body.classList.toggle('nav-open');
        });
        
        // Close menu when clicking overlay
        if (navOverlay) {
            navOverlay.addEventListener('click', function() {
                closeNav();
            });
        }
        
        // Close menu when clicking a link
        const navLinks = navMenu.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                closeNav();
            });
        });
        
        // Function to close navigation
        function closeNav() {
            navToggle.classList.remove('active');
            navMenu.classList.remove('active');
            navOverlay.classList.remove('active');
            document.body.classList.remove('nav-open');
        }
    }
});
