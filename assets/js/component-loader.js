document.addEventListener("DOMContentLoaded", async () => {
    try {
        // Load Header
        const headerPlaceholder = document.getElementById("header-placeholder");
        if (headerPlaceholder) {
            const headerRes = await fetch("components/header.html");
            if (headerRes.ok) {
                headerPlaceholder.innerHTML = await headerRes.text();
                setupMobileMenu(); // Initialize mobile toggle after injection
            } else {
                console.error("Failed to load header.html, status:", headerRes.status);
            }
        }

        // Load Footer
        const footerPlaceholder = document.getElementById("footer-placeholder");
        if (footerPlaceholder) {
            const footerRes = await fetch("components/footer.html");
            if (footerRes.ok) {
                footerPlaceholder.innerHTML = await footerRes.text();
            } else {
                console.error("Failed to load footer.html, status:", footerRes.status);
            }
        }
    } catch (error) {
        console.error("Error loading reusable components:", error);
    }
});

// Mobile Navigation Toggle Logic
function setupMobileMenu() {
    const menuToggle = document.getElementById("menuToggle");
    const navLinks = document.getElementById("navLinks");
    
    if (menuToggle && navLinks) {
        menuToggle.addEventListener("click", () => {
            navLinks.classList.toggle("active");
        });
    }
}