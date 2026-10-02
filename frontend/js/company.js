"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const menuButton = document.querySelector(".menu-toggle");
    const siteNav = document.querySelector(".site-nav");
    const year = document.getElementById("year");
    const form = document.getElementById("inquiryForm");
    const message = document.getElementById("formMessage");

    year.textContent = new Date().getFullYear();
    const loginLink = document.querySelector(".login-link");
    if (localStorage.getItem("access_token")) {
        loginLink.href = "index.html#dashboard";
        loginLink.setAttribute("aria-label", "Open your CRM dashboard");
        loginLink.title = "Open your CRM dashboard";
    }
    menuButton.addEventListener("click", () => {
        const expanded = menuButton.getAttribute("aria-expanded") === "true";
        menuButton.setAttribute("aria-expanded", String(!expanded));
        siteNav.classList.toggle("open", !expanded);
    });
    siteNav.querySelectorAll("a").forEach(link => link.addEventListener("click", () => {
        siteNav.classList.remove("open");
        menuButton.setAttribute("aria-expanded", "false");
    }));

    const revealObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                revealObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });
    document.querySelectorAll(".reveal").forEach(element => revealObserver.observe(element));

    document.querySelectorAll("[data-service]").forEach(link => link.addEventListener("click", () => {
        const service = link.dataset.service;
        const select = form.elements.service_interest;
        const matchingOption = [...select.options].find(option => option.text === service);
        if (matchingOption) select.value = matchingOption.value;
    }));

    form.addEventListener("submit", async event => {
        event.preventDefault();
        const submitButton = form.querySelector("button[type='submit']");
        const formData = new FormData(form);
        const payload = Object.fromEntries(formData.entries());
        submitButton.disabled = true;
        submitButton.textContent = "Sending enquiry...";
        message.textContent = "Sending your project details securely.";
        try {
            const response = await fetch(`${window.location.origin}/leads/public-inquiries`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "Accept": "application/json" },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            if (!response.ok) throw new Error(result.detail || "We could not send your enquiry. Please try again.");
            form.reset();
            message.textContent = result.message || "Thanks, your request has been received.";
        } catch (error) {
            message.textContent = error.message || "Unable to send right now. Please email support@nexspiretechnologies.in.";
        } finally {
            submitButton.disabled = false;
            submitButton.innerHTML = 'Send project enquiry <span>↗</span>';
        }
    });
});