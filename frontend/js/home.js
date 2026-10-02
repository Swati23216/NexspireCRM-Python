"use strict";

document.addEventListener("DOMContentLoaded", () => {
    bindHomeEvents();
    hydrateUser();
    loadHomeData();
});

function bindHomeEvents() {
    const menuButton = document.getElementById("menuButton");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("mobileOverlay");
    const closeMenu = () => { sidebar.classList.remove("open"); overlay.classList.remove("visible"); };
    menuButton.addEventListener("click", () => { sidebar.classList.add("open"); overlay.classList.add("visible"); });
    overlay.addEventListener("click", closeMenu);
    document.querySelectorAll(".nav-link").forEach(link => link.addEventListener("click", closeMenu));
    document.getElementById("logoutButton").addEventListener("click", () => { localStorage.clear(); window.location.href = "login.html"; });
    document.querySelectorAll("[data-target]").forEach(button => button.addEventListener("click", () => {
        const target = button.dataset.target;
        window.location.href = `index.html#${target === "lead" ? "leads" : target === "activity" ? "activities" : target}`;
    }));
    document.getElementById("globalSearch").addEventListener("keydown", event => {
        if (event.key === "Enter" && event.target.value.trim()) window.location.href = "index.html#search";
    });
}

function hydrateUser() {
    const email = localStorage.getItem("email") || "Workspace user";
    const role = localStorage.getItem("role_name") || "Team member";
    const name = email.split("@")[0].replace(/[._-]/g, " ").replace(/\b\w/g, letter => letter.toUpperCase());
    const initials = name.split(" ").map(part => part[0]).join("").slice(0, 2) || "NW";
    setText("userName", name); setText("welcomeName", name.split(" ")[0]);
    setText("userRole", role); setText("userAvatar", initials);
}

async function loadHomeData() {
    if (!localStorage.getItem("access_token")) { window.location.href = "login.html"; return; }
    try {
        const [summary, leads, followups] = await Promise.all([
            apiRequest("/dashboard/summary"), apiRequest("/dashboard/recent-leads"), apiRequest("/dashboard/upcoming-followups")
        ]);
        renderSummary(summary); renderLeads(extractArray(leads, ["leads"])); renderFollowups(extractArray(followups, ["followups"]));
        setText("lastUpdated", `Last updated ${new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`);
    } catch (error) {
        const alert = document.getElementById("statusAlert"); alert.hidden = false;
        alert.textContent = "Live data is temporarily unavailable. Check that the API and database are running.";
        document.getElementById("recentLeads").innerHTML = '<tr><td colspan="5" class="empty-state">No live lead data available.</td></tr>';
        document.getElementById("followupList").innerHTML = '<div class="empty-state">No follow-ups available.</div>';
    }
}

function renderSummary(data) {
    const summary = data?.summary || {}, leads = data?.leads || {}, opportunities = data?.opportunities || {};
    setText("totalLeads", summary.total_leads || 0); setText("navLeadCount", summary.total_leads || 0);
    setText("totalCustomers", summary.total_customers || 0); setText("totalOpportunities", opportunities.open ?? summary.total_opportunities ?? 0);
    setText("wonRevenue", formatMoney(summary.won_revenue)); setText("pipelineValue", formatMoney(opportunities.total_value));
    const total = summary.total_leads || 0; setText("conversionRate", `${total ? Math.round(((leads.converted || 0) / total) * 100) : 0}%`);
    const points = [["New", leads.new || 0, "bar-teal"], ["Contacted", leads.contacted || 0, "bar-blue"], ["Qualified", leads.qualified || 0, "bar-yellow"], ["Converted", leads.converted || 0, "bar-coral"]];
    const max = Math.max(...points.map(point => point[1]), 1);
    document.getElementById("leadChart").innerHTML = points.map(([label, value, color]) => `<div class="chart-bar ${color}" style="height:${Math.max((value / max) * 100, 4)}%"><span>${value}</span><small>${label}</small></div>`).join("");
}

function renderLeads(leads) {
    const body = document.getElementById("recentLeads");
    if (!leads.length) { body.innerHTML = '<tr><td colspan="5" class="empty-state">Your latest leads will appear here.</td></tr>'; return; }
    body.innerHTML = leads.slice(0, 8).map(lead => `<tr><td class="lead-name">${escapeHtml(lead.name || "Unnamed lead")}</td><td>${escapeHtml(lead.company || "-")}</td><td><span class="status ${String(lead.status || "").toLowerCase()}">${escapeHtml(lead.status || "New")}</span></td><td>${escapeHtml(lead.source || "-")}</td><td>${formatDate(lead.created_at)}</td></tr>`).join("");
}

function renderFollowups(followups) {
    const container = document.getElementById("followupList");
    if (!followups.length) { container.innerHTML = '<div class="empty-state">You are all caught up.</div>'; return; }
    container.innerHTML = followups.slice(0, 4).map(item => { const date = new Date(item.next_followup_date); return `<div class="followup-item"><div class="date-box"><strong>${date.getDate() || "-"}</strong><small>${date.toLocaleString("en", { month: "short" })}</small></div><div class="followup-copy"><strong>${escapeHtml(item.remarks || "Follow-up reminder")}</strong><small>${item.lead_id ? `Lead #${escapeHtml(item.lead_id)}` : "Customer follow-up"}</small></div></div>`; }).join("");
}

function setText(id, value) { document.getElementById(id).textContent = value; }
function formatMoney(value) { return `₹${Number(value || 0).toLocaleString("en-IN")}`; }
function formatDate(value) { if (!value) return "-"; return new Date(value).toLocaleDateString("en-IN", { day: "2-digit", month: "short" }); }
