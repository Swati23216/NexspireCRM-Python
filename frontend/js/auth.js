"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");
    const toggle = document.getElementById("authToggle");
    const subtitle = document.getElementById("authSubtitle");
    let registering = false;

    toggle.addEventListener("click", () => {
        registering = !registering;
        loginForm.hidden = registering;
        registerForm.hidden = !registering;
        subtitle.textContent = registering
            ? "Create your Nexspire CRM account"
            : "Sign in to your workspace";
        toggle.textContent = registering
            ? "Already have an account? Sign in"
            : "New to Nexspire? Create an account";
        document.getElementById("loginMessage").textContent = "";
        document.getElementById("registerMessage").textContent = "";
    });

    loginForm.addEventListener("submit", async event => {
        event.preventDefault();
        const button = document.getElementById("loginButton");
        const message = document.getElementById("loginMessage");
        button.disabled = true;
        button.textContent = "Signing in...";

        try {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    email: document.getElementById("email").value.trim(),
                    password: document.getElementById("password").value
                })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Sign in failed.");
            storeSession(data);
            window.location.href = "index.html#dashboard";
        } catch (error) {
            message.textContent = error.message || "Sign in failed.";
        } finally {
            button.disabled = false;
            button.textContent = "Login";
        }
    });

    registerForm.addEventListener("submit", async event => {
        event.preventDefault();
        const button = document.getElementById("registerButton");
        const message = document.getElementById("registerMessage");
        button.disabled = true;
        button.textContent = "Creating account...";

        try {
            const response = await fetch(`${API_URL}/auth/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    full_name: document.getElementById("registerName").value.trim(),
                    email: document.getElementById("registerEmail").value.trim(),
                    mobile_no: document.getElementById("registerMobile").value.trim(),
                    password: document.getElementById("registerPassword").value
                })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.detail || "Registration failed.");
            document.getElementById("email").value =
                document.getElementById("registerEmail").value.trim();
            document.getElementById("password").value =
                document.getElementById("registerPassword").value;
            toggle.click();
            document.getElementById("loginMessage").textContent =
                `Account created as ${data.role_name}. Sign in to continue.`;
            registerForm.reset();
        } catch (error) {
            message.textContent = error.message || "Registration failed.";
        } finally {
            button.disabled = false;
            button.textContent = "Create account";
        }
    });
});

function storeSession(data) {
    localStorage.setItem("access_token", data.access_token);
    if (data.refresh_token) localStorage.setItem("refresh_token", data.refresh_token);
    localStorage.setItem("user_id", data.user_id);
    localStorage.setItem("email", data.email);
    localStorage.setItem("role_id", data.role_id);
    localStorage.setItem("role_name", data.role_name);
}
