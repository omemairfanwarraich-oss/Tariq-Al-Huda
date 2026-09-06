// Check if user is logged in and update UI elements accordingly
function checkAuthStatus() {
    const token = localStorage.getItem("access_token");
    const username = localStorage.getItem("username");
    
    const authNav = document.getElementById("auth-nav");
    if (!authNav) return;

    if (token && username) {
        authNav.innerHTML = `
            <div class="relative group cursor-pointer inline-block">
                <span class="nav-link font-medium flex items-center">👤 ${username} ▾</span>
                <div class="absolute right-0 hidden group-hover:block bg-white shadow-md rounded mt-1 py-2 w-32 border z-50">
                    <button onclick="logout()" class="w-full text-left px-4 py-2 text-red-600 hover:bg-gray-100 text-sm">Logout</button>
                </div>
            </div>
        `;
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