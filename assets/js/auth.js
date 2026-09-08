// Check if user is logged in and update UI elements accordingly
function checkAuthStatus() {
    const token = localStorage.getItem("access_token");
    const username = localStorage.getItem("username");
    const isAdmin = localStorage.getItem("is_admin") === "true";
    const navLinks = document.getElementById("navLinks");
    if (isAdmin && navLinks) {
        navLinks.innerHTML = `<a href="admin-dashboard.html" class="nav-link">Dashboard</a><a href="admin-upload.html" class="nav-link">Manage PDFs</a><a href="admin-faqs.html" class="nav-link">Manage FAQs</a><form class="nav-search" action="pdfs.html" method="get" role="search"><input name="q" aria-label="Search documents" placeholder="Search ID or name"><button type="submit" aria-label="Search documents">⌕</button></form><span id="auth-nav" class="inline-flex items-center"></span>`;
    }
    const authNav = document.getElementById("auth-nav");
    if (!authNav) return;

    if (token && username) {
        const adminLink = '';
        authNav.innerHTML = `
            <div class="auth-profile">
                <button class="auth-user-button" type="button" aria-expanded="false"><span class="auth-user-name">${username}</span><span aria-hidden="true">▾</span></button>
                <div class="auth-menu">
                    ${adminLink}
                    <button onclick="logout()" class="button button-danger">Logout</button>
                </div>
            </div>
        `;
        const profileButton = authNav.querySelector('.auth-user-button');
        profileButton.addEventListener('click', () => {
            const open = authNav.classList.toggle('auth-menu-open');
            profileButton.setAttribute('aria-expanded', String(open));
        });
    } else {
        authNav.innerHTML = `
            <a href="login.html" class="auth-btn-login">Login</a>
            <a href="register.html" class="auth-btn-signup">Signup</a>
        `;
    }
}

// Handle User Login
async function handleLogin(event, formId) {
    event.preventDefault();
    const form = document.getElementById(formId);
    
    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: form.username.value,
                password: form.password.value
            })
        });

        const data = await response.json();
        if (response.ok) {
            localStorage.setItem("access_token", data.access_token);
            localStorage.setItem("username", data.username);
            localStorage.setItem("is_admin", data.is_admin);
            window.location.href = "/pdfs.html"; // Redirect to notes page after login
        } else {
            alert(data.detail || "Login failed");
        }
    } catch (err) {
        console.error("Login error:", err);
        alert("An error occurred during login.");
    }
}

// Handle User Registration
async function handleRegister(event, formId) {
    event.preventDefault();
    const form = document.getElementById(formId);

    try {
        const response = await fetch("/api/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: form.username.value,
                email: form.email.value,
                password: form.password.value
            })
        });

        const data = await response.json();
        if (response.ok) {
            alert("Registration successful! Please log in.");
            window.location.href = "/login.html";
        } else {
            alert(data.detail || "Registration failed");
        }
    } catch (err) {
        console.error("Registration error:", err);
        alert("An error occurred during registration.");
    }
}

// Handle Logout
function logout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("username");
    localStorage.removeItem("is_admin");
    window.location.href = "/login.html";
}

// Run auth check automatically when the DOM loads
document.addEventListener("DOMContentLoaded", checkAuthStatus);
// Handle Admin Login Specifically
async function handleAdminLogin(event, formId) {
    event.preventDefault();
    const form = document.getElementById(formId);
    
    try {
        const response = await fetch("/api/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username: form.username.value,
                password: form.password.value
            })
        });

        const data = await response.json();
        if (response.ok) {
            // Verify if user is actually an admin
            if (data.is_admin === true || data.is_admin === "true") {
                localStorage.setItem("access_token", data.access_token);
                localStorage.setItem("username", data.username);
                localStorage.setItem("is_admin", data.is_admin);
                window.location.href = "/admin-dashboard.html";
            } else {
                alert("Access denied. This account does not have administrator privileges.");
            }
        } else {
            alert(data.detail || "Admin login failed");
        }
    } catch (err) {
        console.error("Admin login error:", err);
        alert("An error occurred during admin login.");
    }
}