/* =========================================================
   NEXSPIRE CRM - DASHBOARD.JS
   Complete frontend controller

   Works with:
   - Dashboard
   - Leads
   - Customers
   - Opportunities
   - Activities
   - Follow-Ups
   - Tickets
   - Notifications
   - Reports
   - Global Search
   - Authentication
   - CRUD actions
========================================================= */

"use strict";

/* =========================================================
   CONFIGURATION
========================================================= */

const CRM_API_URL = window.location.origin;


/* =========================================================
   GLOBAL STATE
========================================================= */

let allLeads = [];
let allCustomers = [];
let allOpportunities = [];
let allActivities = [];
let allFollowups = [];
let allTickets = [];

let currentOpportunityFilter = "all";

let editingLeadId = null;
let editingCustomerId = null;
let editingOpportunityId = null;
let editingActivityId = null;
let editingFollowupId = null;
let editingTicketId = null;
let currentRoleName = localStorage.getItem("role_name") || "Viewer";
let currentPermissions = [];
let adminUsers = [];


/* =========================================================
   DOM READY
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    console.log("=================================");
    console.log("Nexspire CRM Dashboard Loaded");
    console.log("=================================");

    const token = localStorage.getItem("access_token");
    const menuButton = document.getElementById("menuButton");
    const sidebar = document.getElementById("sidebar");
    const overlay = document.getElementById("mobileOverlay");
    if (menuButton && sidebar && overlay) {
        menuButton.addEventListener("click", () => {
            sidebar.classList.add("open");
            overlay.classList.add("visible");
        });
        const closeMenu = () => {
            sidebar.classList.remove("open");
            overlay.classList.remove("visible");
        };
        overlay.addEventListener("click", closeMenu);
        sidebar.querySelectorAll("nav button, nav a").forEach(item =>
            item.addEventListener("click", closeMenu)
        );
    }

    if (!token) {
        window.location.href = "login.html";
        return;
    }

    initializeDashboard();

});


/* =========================================================
   INITIALIZE
========================================================= */

async function initializeDashboard() {

    try {

        await loadUser();

        const allowedSections = sectionsForCurrentUser();
        const loaders = {
            dashboard: loadDashboard,
            leads: loadLeads,
            customers: loadCustomers,
            opportunities: loadOpportunities,
            activities: loadActivities,
            followups: loadFollowups,
            tickets: loadTickets,
            notifications: loadNotifications,
            admin: loadAdminData

        };
        for (const sectionName of allowedSections) {
            if (loaders[sectionName]) await loaders[sectionName]();
        }

        console.log("CRM initialization completed.");

    } catch (error) {

        console.error(
            "Dashboard initialization error:",
            error
        );

    }

}


/* =========================================================
   API HELPER
========================================================= */

async function apiRequest(endpoint, options = {}) {

    const token =
        localStorage.getItem("access_token");

    const url =
        endpoint.startsWith("http")
            ? endpoint
            : `${CRM_API_URL}${endpoint}`;

    const headers = {
        "Content-Type": "application/json",
        ...(options.headers || {})
    };

    if (token) {
        headers["Authorization"] =
            `Bearer ${token}`;
    }

    const response =
        await fetch(url, {
            ...options,
            headers
        });

    let result = null;

    const contentType =
        response.headers.get("content-type") || "";

    if (contentType.includes("application/json")) {

        result = await response.json();

    } else {

        result = await response.text();

    }


    /* =====================================================
       AUTH ERROR
    ===================================================== */

    if (response.status === 401) {

        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");

        window.location.href = "login.html";

        throw new Error(
            "Session expired. Please login again."
        );

    }


    /* =====================================================
       API ERROR
    ===================================================== */

    if (!response.ok) {

        let message = `HTTP ${response.status}`;

        if (result) {

            if (typeof result === "string") {

                message = result;

            } else if (result.detail) {

                if (Array.isArray(result.detail)) {

                    message = result.detail
                        .map(item =>
                            item.msg || JSON.stringify(item)
                        )
                        .join(", ");

                } else {

                    message = result.detail;

                }

            } else if (result.message) {

                message = result.message;

            } else {

                message = JSON.stringify(result);

            }

        }

        throw new Error(message);

    }

    return result;

}


/* =========================================================
   ARRAY EXTRACTION
========================================================= */

function extractArray(data, possibleKeys = []) {

    if (Array.isArray(data)) {
        return data;
    }

    if (!data || typeof data !== "object") {
        return [];
    }

    for (const key of possibleKeys) {

        if (Array.isArray(data[key])) {
            return data[key];
        }

    }

    if (Array.isArray(data.data)) {
        return data.data;
    }

    if (Array.isArray(data.items)) {
        return data.items;
    }

    if (Array.isArray(data.results)) {
        return data.results;
    }

    return [];

}


/* =========================================================
   GET NUMERIC LEAD ID
========================================================= */

function getLeadId(lead) {

    if (!lead) {
        return null;
    }

    /*
       IMPORTANT:

       Backend expects:
           /leads/{lead_id}

       and lead_id is INTEGER.

       Do NOT use MongoDB _id here.
    */

    if (
        lead.lead_id !== undefined &&
        lead.lead_id !== null
    ) {

        return Number(lead.lead_id);

    }

    if (
        lead.id !== undefined &&
        lead.id !== null &&
        !isNaN(Number(lead.id))
    ) {

        return Number(lead.id);

    }

    return null;

}


/* =========================================================
   GET NUMERIC CUSTOMER ID
========================================================= */

function getCustomerId(customer) {

    if (!customer) {
        return null;
    }

    if (
        customer.customer_id !== undefined &&
        customer.customer_id !== null
    ) {

        return Number(customer.customer_id);

    }

    if (
        customer.id !== undefined &&
        customer.id !== null &&
        !isNaN(Number(customer.id))
    ) {

        return Number(customer.id);

    }

    return null;

}


/* =========================================================
   GET NUMERIC OPPORTUNITY ID
========================================================= */

function getOpportunityId(opportunity) {

    if (!opportunity) {
        return null;
    }

    if (
        opportunity.opportunity_id !== undefined &&
        opportunity.opportunity_id !== null
    ) {

        return Number(opportunity.opportunity_id);

    }

    if (
        opportunity.id !== undefined &&
        opportunity.id !== null &&
        !isNaN(Number(opportunity.id))
    ) {

        return Number(opportunity.id);

    }

    return null;

}



/* =========================================================
   ESCAPE HTML
========================================================= */

function escapeHtml(value) {

    if (
        value === null ||
        value === undefined
    ) {

        return "";

    }

    return String(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");

}


/* =========================================================
   FORMAT CURRENCY
========================================================= */

function formatCurrency(value) {

    const amount =
        Number(value) || 0;

    return "₹" +
        amount.toLocaleString("en-IN");

}


/* =========================================================
   NAVIGATION
========================================================= */

function showSection(sectionName) {

    const allowedSections = sectionsForCurrentUser();
    const section = document.getElementById(sectionName);

    if (!section || !allowedSections.includes(sectionName)) {
        return;
    }

    document
        .querySelectorAll(".section")
        .forEach(section => {

            section.classList.remove("active");

        });

    section.hidden = false;
    section.classList.add("active");


    switch (sectionName) {

        case "dashboard":
            loadDashboard();
            break;

        case "leads":
            loadLeads();
            break;

        case "customers":
            loadCustomers();
            break;

        case "opportunities":
            loadCustomers();
            loadOpportunities();
            break;

        case "activities":
            loadActivities();
            break;

        case "followups":
            loadFollowups();
            break;

        case "tickets":
            loadTickets();
            break;

        case "notifications":
            loadNotifications();
            break;

        case "reports":
            loadReports();
            break;

        case "search":
            break;

        case "admin":
            loadAdminData();
            break;

    }

}


/* =========================================================
   DASHBOARD
========================================================= */

async function loadDashboard() {

    try {

        const data =
            await apiRequest(
                "/dashboard/summary"
            );

        console.log(
            "Dashboard Summary:",
            data
        );


        const summary =
            data.summary || {};

        const opportunities =
            data.opportunities || {};

        const totalUsers = document.getElementById("totalUsers");
        if (totalUsers) totalUsers.textContent = summary.total_users ?? 0;


        const totalLeads =
            document.getElementById("totalLeads");

        const totalCustomers =
            document.getElementById("totalCustomers");

        const totalOpportunities =
            document.getElementById(
                "totalOpportunities"
            );

        const totalActivities =
            document.getElementById(
                "totalActivities"
            );

        const totalTickets =
            document.getElementById(
                "totalTickets"
            );

        const wonRevenue =
            document.getElementById(
                "wonRevenue"
            );


        if (totalLeads) {

            totalLeads.textContent =
                summary.total_leads ?? 0;

        }


        if (totalCustomers) {

            totalCustomers.textContent =
                summary.total_customers ?? 0;

        }


        if (totalOpportunities) {

            totalOpportunities.textContent =
                summary.total_opportunities ?? 0;

        }


        if (totalActivities) {

            totalActivities.textContent =
                summary.total_activities ?? 0;

        }


        if (totalTickets) {

            totalTickets.textContent =
                summary.total_tickets ?? 0;

        }


        if (wonRevenue) {

            wonRevenue.textContent =
                formatCurrency(
                    opportunities.won_revenue ?? 0
                );

        }


    } catch (error) {

        console.error(
            "Dashboard summary error:",
            error
        );

    }


    const recentLeads = document.getElementById("recentLeads");
    const upcomingFollowups = document.getElementById("upcomingFollowups");
    if (recentLeads) {
        recentLeads.closest(".panel").hidden = !isPermissionAllowed("leads.view");
        if (isPermissionAllowed("leads.view")) await loadRecentLeads();
    }
    if (upcomingFollowups) {
        upcomingFollowups.closest(".panel").hidden = !isPermissionAllowed("followups.view");
        if (isPermissionAllowed("followups.view")) await loadUpcomingFollowups();
    }

}


/* =========================================================
   RECENT LEADS
========================================================= */

async function loadRecentLeads() {

    const container =
        document.getElementById(
            "recentLeads"
        );

    if (!container) {
        return;
    }


    container.innerHTML =
        "<p>Loading...</p>";


    try {

        const data =
            await apiRequest(
                "/dashboard/recent-leads"
            );


        const leads =
            extractArray(
                data,
                ["leads"]
            );


        if (!leads.length) {

            container.innerHTML =
                "<p>No recent leads.</p>";

            return;

        }


        container.innerHTML =
            leads
                .slice(0, 5)
                .map(lead => `

                    <div class="list-item">

                        <strong>
                            ${escapeHtml(
                                lead.name ||
                                "Unnamed"
                            )}
                        </strong>

                        <span>
                            ${escapeHtml(
                                lead.status ||
                                "New"
                            )}
                        </span>

                    </div>

                `)
                .join("");


    } catch (error) {

        console.error(
            "Recent leads error:",
            error
        );

        container.innerHTML =
            "<p>Unable to load recent leads.</p>";

    }

}


/* =========================================================
   UPCOMING FOLLOWUPS
========================================================= */

async function loadUpcomingFollowups() {

    const container =
        document.getElementById(
            "upcomingFollowups"
        );

    if (!container) {
        return;
    }


    container.innerHTML =
        "<p>Loading...</p>";


    try {

        const data =
            await apiRequest(
                "/dashboard/upcoming-followups"
            );


        const followups =
            extractArray(
                data,
                ["followups"]
            );


        if (!followups.length) {

            container.innerHTML =
                "<p>No upcoming follow-ups.</p>";

            return;

        }


        container.innerHTML =
            followups
                .slice(0, 5)
                .map(item => `

                    <div class="list-item">

                        <strong>
                            ${escapeHtml(
                                item.subject ||
                                "Follow-Up"
                            )}
                        </strong>

                        <span>
                            ${escapeHtml(formatDateTime(item.next_followup_date))}
                        </span>

                        ${item.notes ? `
                            <small>${escapeHtml(item.notes)}</small>
                        ` : ""}

                    </div>

                `)
                .join("");


    } catch (error) {

        console.error(
            "Upcoming followups error:",
            error
        );

        container.innerHTML =
            "<p>Unable to load follow-ups.</p>";

    }

}


/* =========================================================
   LEADS - READ
========================================================= */

async function loadLeads() {

    const container =
        document.getElementById(
            "leadsContent"
        );

    if (!container) {
        return;
    }


    container.innerHTML = "<p>Loading leads...</p>";


    try {

        const data =
            await apiRequest(
                "/leads/"
            );


        allLeads =
            extractArray(
                data,
                ["leads"]
            );


        if (!allLeads.length) {

            container.innerHTML = "<p>No leads found.</p>";

            return;

        }


        container.innerHTML = `
            <table class="crm-table leads-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Phone</th>
                        <th>Status</th>
                        <th>Source</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${allLeads.map(renderLeadRow).join("")}
                </tbody>
            </table>
        `;


    } catch (error) {

        console.error(
            "Load leads error:",
            error
        );

        container.innerHTML = `
            <p class="error">
                Unable to load leads. ${escapeHtml(error.message)}
            </p>
        `;

    }

}


/* =========================================================
   RENDER LEAD
========================================================= */

/* =========================================================
   RENDER LEAD
========================================================= */

function renderLeadRow(lead) {

    const leadId = getLeadId(lead);

    if (leadId === null) {
        return `
            <tr>
                <td colspan="7" class="error">
                    Invalid Lead ID
                </td>
            </tr>
        `;
    }

    const status = String(
        lead.status || "New"
    ).trim();

    /*
       Get role from both:
       1. currentRoleName
       2. localStorage

       This prevents Delete from disappearing
       when currentRoleName is not updated correctly.
    */
    const currentRole = String(
        currentRoleName || ""
    )
        .trim()
        .toLowerCase();

    const storedRole = String(
        localStorage.getItem("role_name") || ""
    )
        .trim()
        .toLowerCase();

    const role =
        currentRole === "admin" || storedRole === "admin"
            ? "admin"
            : currentRole || storedRole;

    console.log("=================================");
    console.log("LEAD ACTION DEBUG");
    console.log("Lead ID:", leadId);
    console.log("currentRoleName:", currentRoleName);
    console.log("Stored role:", storedRole);
    console.log("Final role:", role);
    console.log("=================================");

    /*
       EDIT PERMISSIONS
    */
    const canEdit = [
        "admin",
        "manager",
        "sales executive",
        "calling executive",
        "marketing executive"
    ].includes(role);

    /*
       CONVERT PERMISSIONS
    */
    const canConvert = [
        "admin",
        "manager",
        "sales executive"
    ].includes(role);

    /*
       DELETE PERMISSION
       ONLY ADMIN
    */
    const canDelete = role === "admin";

    let actions = "";

    /* =====================================================
       EDIT BUTTON
    ===================================================== */

    if (canEdit) {

        actions += `
            <button
                type="button"
                class="action-btn edit-btn"
                onclick="editLead(${leadId})"
                title="Edit Lead">
                ✏️ Edit
            </button>
        `;
    }


    /* =====================================================
       CONVERT BUTTON
    ===================================================== */

    if (canConvert) {

        actions += `
            <button
                type="button"
                class="action-btn convert-btn"
                onclick="convertLead(${leadId})"
                title="Convert Lead to Customer">
                🔄 Convert
            </button>
        `;
    }


    /* =====================================================
       DELETE BUTTON
    ===================================================== */

    if (canDelete) {

        actions += `
            <button
                type="button"
                class="action-btn delete-btn"
                onclick="deleteLead(${leadId})"
                title="Delete Lead">
                🗑️ Delete
            </button>
        `;
    }


    /* =====================================================
       NO ACTIONS
    ===================================================== */

    if (!actions) {

        actions = `
            <span class="no-actions">
                No actions
            </span>
        `;
    }


    /* =====================================================
       RETURN ROW
    ===================================================== */

    return `
        <tr>

            <td>
                ${escapeHtml(leadId)}
            </td>

            <td>
                ${escapeHtml(lead.name || "")}
            </td>

            <td>
                ${escapeHtml(lead.email || "")}
            </td>

            <td>
                ${escapeHtml(lead.phone || "")}
            </td>

            <td>
                <span class="lead-status status-${escapeHtml(
                    status.toLowerCase()
                )}">
                    ${escapeHtml(status)}
                </span>
            </td>

            <td>
                ${escapeHtml(lead.source || "")}
            </td>

            <td class="lead-actions">
                ${actions}
            </td>

        </tr>
    `;
}

/* =========================================================
   LEADS - DELETE
========================================================= */

async function deleteLead(leadId) {

    console.log("=================================");
    console.log("DELETE LEAD CLICKED");
    console.log("Received Lead ID:", leadId);
    console.log("=================================");

    const id = Number(leadId);

    if (!Number.isInteger(id)) {

        alert(
            "Invalid Lead ID: " + leadId
        );

        return;
    }


    const confirmed = confirm(
        "Are you sure you want to delete Lead #" + id + "?"
    );

    if (!confirmed) {
        return;
    }


    try {

        console.log(
            "Sending DELETE request:",
            `/leads/${id}`
        );


        const response = await apiRequest(
            `/leads/${id}`,
            {
                method: "DELETE"
            }
        );


        console.log(
            "DELETE RESPONSE:",
            response
        );


        alert(
            "Lead deleted successfully."
        );


        /*
           Reload leads table
        */
        await loadLeads();


        /*
           Reload dashboard statistics
        */
        await loadDashboard();


    } catch (error) {

        console.error(
            "DELETE LEAD ERROR:",
            error
        );


        alert(
            "Unable to delete lead.\n\n" +
            error.message
        );
    }
}

/* =========================================================
   LEADS - EDIT
========================================================= */

async function editLead(leadId) {

    const id = Number(leadId);

    if (!Number.isInteger(id)) {
        alert("Invalid Lead ID.");
        return;
    }

    const lead = allLeads.find(
        item => getLeadId(item) === id
    );

    if (!lead) {
        alert("Lead not found.");
        return;
    }

    const name = prompt(
        "Lead Name:",
        lead.name || ""
    );

    if (name === null) {
        return;
    }

    const email = prompt(
        "Email:",
        lead.email || ""
    );

    if (email === null) {
        return;
    }

    const phone = prompt(
        "Phone:",
        lead.phone || ""
    );

    if (phone === null) {
        return;
    }

    const company = prompt(
        "Company:",
        lead.company || ""
    );

    if (company === null) {
        return;
    }

    const source = prompt(
        "Source:",
        lead.source || ""
    );

    if (source === null) {
        return;
    }

    const body = {
        name: name.trim(),
        email: email.trim(),
        phone: phone.trim(),
        company: company.trim(),
        source: source.trim()
    };

    console.log("Updating Lead:", id, body);

    try {

        await apiRequest(
            `/leads/${id}`,
            {
                method: "PUT",
                body: JSON.stringify(body)
            }
        );

        alert("Lead updated successfully.");

        await loadLeads();
        await loadDashboard();

    } catch (error) {

        console.error(
            "Edit lead error:",
            error
        );

        alert(
            "Unable to update lead.\n\n" +
            error.message
        );
    }
}






function openOpportunityModal() {

    const modal =
        document.getElementById("opportunityModal");

    if (modal) {
        modal.style.display = "flex";
    }

}


function closeOpportunityModal() {

    const modal =
        document.getElementById("opportunityModal");

    if (modal) {

        modal.style.display = "none";

        const form =
            document.getElementById("opportunityForm");

        if (form) {
            form.reset();
        }

    }

}


/*
    Close modal when clicking outside the modal content
*/

document.addEventListener("click", function(event) {

    const modal =
        document.getElementById("opportunityModal");

    if (
        modal &&
        event.target === modal
    ) {
        closeOpportunityModal();
    }

});



/* =========================================================
   CUSTOMERS - READ
========================================================= */

async function loadCustomers() {

    const container =
        document.getElementById(
            "customersContent"
        );

    if (!container) {
        return;
    }


    container.innerHTML =
        "<p>Loading customers...</p>";


    try {

        const data =
            await apiRequest(
                "/customers/"
            );


        allCustomers =
            extractArray(
                data,
                ["customers"]
            );


        if (!allCustomers.length) {

            container.innerHTML =
                "<p>No customers found.</p>";

            await loadOpportunityCustomers();

            return;

        }


        container.innerHTML = `

            <table class="crm-table">

                <thead>

                    <tr>

                        <th>ID</th>

                        <th>Name</th>

                        <th>Email</th>

                        <th>Phone</th>

                        <th>Company</th>

                        <th>Actions</th>

                    </tr>

                </thead>

                <tbody>

                    ${
                        allCustomers
                            .map(renderCustomerRow)
                            .join("")
                    }

                </tbody>

            </table>

        `;


        await loadOpportunityCustomers();


    } catch (error) {

        console.error(
            "Load customers error:",
            error
        );


        container.innerHTML =
            `<p class="error">
                Unable to load customers:
                ${escapeHtml(error.message)}
            </p>`;

    }

}


/* =========================================================
   CUSTOMER ROW
========================================================= */

function renderCustomerRow(customer) {

    const customerId =
        getCustomerId(customer);
    const canEdit = ["Admin", "Manager", "Sales Executive"].includes(currentRoleName);
    const canDelete = currentRoleName === "Admin";


    return `

        <tr>

            <td>
                ${escapeHtml(
                    customerId ??
                    customer._id ??
                    ""
                )}
            </td>

            <td>
                ${escapeHtml(
                    customer.name || ""
                )}
            </td>

            <td>
                ${escapeHtml(
                    customer.email || ""
                )}
            </td>

            <td>
                ${escapeHtml(
                    customer.phone || ""
                )}
            </td>

            <td>
                ${escapeHtml(
                    customer.company || ""
                )}
            </td>

            <td>

                ${
                    customerId !== null
                    ? `

                        ${canEdit ? `
                            <button
                                type="button"
                                onclick="editCustomer(${customerId})"
                            >
                                ✏️ Edit
                            </button>
                        ` : ""}

                        ${canDelete ? `
                            <button
                                type="button"
                                onclick="deleteCustomer(${customerId})"
                            >
                                🗑️ Delete
                            </button>
                        ` : ""}

                    `
                    : "Invalid ID"
                }

            </td>

        </tr>

    `;

}


/* =========================================================
   CUSTOMER - CREATE
========================================================= */

document.addEventListener(
    "submit",
    async function (event) {

        if (
            event.target.id !==
            "customerForm"
        ) {
            return;
        }


        event.preventDefault();

        const body = {

            name:
                document
                    .getElementById(
                        "customerName"
                    )
                    .value
                    .trim(),

            email:
                document
                    .getElementById(
                        "customerEmail"
                    )
                    .value
                    .trim(),

            phone:
                document
                    .getElementById(
                        "customerPhone"
                    )
                    .value
                    .trim(),

            company:
                document
                    .getElementById(
                        "customerCompany"
                    )
                    .value
                    .trim()

        };


        if (!body.name) {

            alert(
                "Please enter customer name."
            );

            return;

        }


        if (!body.company) {

            alert(
                "Please enter company."
            );

            return;

        }


        try {

            console.log(
                "Creating customer:",
                body
            );


            await apiRequest(
                "/customers/",
                {
                    method: "POST",
                    body: JSON.stringify(body)
                }
            );


            alert(
                "Customer created successfully."
            );


            event.target.reset();


            await loadCustomers();

            await loadDashboard();


        } catch (error) {

            console.error(
                "Create customer error:",
                error
            );


            alert(
                "Unable to create customer: " +
                error.message
            );

        }

    }
);


/* =========================================================
   CUSTOMER - EDIT
========================================================= */

async function editCustomer(customerId) {

    customerId =
        Number(customerId);


    if (isNaN(customerId)) {

        alert(
            "Invalid customer ID."
        );

        return;

    }


    const customer =
        allCustomers.find(
            item =>
                getCustomerId(item) ===
                customerId
        );


    if (!customer) {

        alert(
            "Customer not found."
        );

        return;

    }


    const name =
        prompt(
            "Customer name:",
            customer.name || ""
        );

    if (name === null) {
        return;
    }


    const email =
        prompt(
            "Email:",
            customer.email || ""
        );

    if (email === null) {
        return;
    }


    const phone =
        prompt(
            "Phone:",
            customer.phone || ""
        );

    if (phone === null) {
        return;
    }


    const company =
        prompt(
            "Company:",
            customer.company || ""
        );

    if (company === null) {
        return;
    }


    const body = {

        name: name.trim(),

        email: email.trim(),

        phone: phone.trim(),

        company: company.trim()

    };


    try {

        await apiRequest(
            `/customers/${customerId}`,
            {
                method: "PUT",
                body: JSON.stringify(body)
            }
        );


        alert(
            "Customer updated successfully."
        );


        await loadCustomers();

        await loadDashboard();


    } catch (error) {

        console.error(
            "Update customer error:",
            error
        );


        alert(
            "Unable to update customer: " +
            error.message
        );

    }

}


/* =========================================================
   CUSTOMER - DELETE
========================================================= */

async function deleteCustomer(customerId) {

    customerId =
        Number(customerId);


    if (isNaN(customerId)) {

        alert(
            "Invalid customer ID."
        );

        return;

    }


    if (
        !confirm(
            "Are you sure you want to delete this customer?"
        )
    ) {

        return;

    }


    try {

        await apiRequest(
            `/customers/${customerId}`,
            {
                method: "DELETE"
            }
        );


        alert(
            "Customer deleted successfully."
        );


        await loadCustomers();

        await loadOpportunities();

        await loadDashboard();


    } catch (error) {

        console.error(
            "Delete customer error:",
            error
        );


        alert(
            "Unable to delete customer: " +
            error.message
        );

    }

}


/* =========================================================
   LOAD CUSTOMERS INTO OPPORTUNITY SELECT
========================================================= */

async function loadOpportunityCustomers() {

    const select =
        document.getElementById(
            "opportunityCustomer"
        );

    if (!select) {
        return;
    }


    select.innerHTML = `
        <option value="">
            Select Customer
        </option>
    `;


    allCustomers.forEach(customer => {

        const customerId =
            getCustomerId(customer);


        if (customerId === null) {
            return;
        }


        const option =
            document.createElement(
                "option"
            );


        option.value =
            customerId;


        option.textContent =
            customer.company
                ? `${customer.name} - ${customer.company}`
                : customer.name;


        select.appendChild(option);

    });

}


/* =========================================================
   OPPORTUNITIES - READ
========================================================= */

async function loadOpportunities() {

    const tbody =
        document.getElementById(
            "opportunitiesTableBody"
        );

    if (!tbody) {
        return;
    }


    tbody.innerHTML = `
        <tr>
            <td colspan="7">
                Loading opportunities...
            </td>
        </tr>
    `;


    try {

        const data =
            await apiRequest(
                "/opportunities/"
            );


        allOpportunities =
            extractArray(
                data,
                ["opportunities"]
            );


        console.log(
            "Opportunities:",
            allOpportunities
        );


        renderOpportunities();


    } catch (error) {

        console.error(
            "Load opportunities error:",
            error
        );


        tbody.innerHTML = `
            <tr>
                <td colspan="7">
                    Unable to load opportunities:
                    ${escapeHtml(error.message)}
                </td>
            </tr>
        `;

    }

}


/* =========================================================
   RENDER OPPORTUNITIES
========================================================= */

function renderOpportunities() {

    const tbody =
        document.getElementById(
            "opportunitiesTableBody"
        );

    if (!tbody) {
        return;
    }


    let opportunities =
        [...allOpportunities];


    if (
        currentOpportunityFilter !==
        "all"
    ) {

        opportunities =
            opportunities.filter(
                opportunity =>
                    opportunity.stage ===
                    currentOpportunityFilter
            );

    }


    if (!opportunities.length) {

        tbody.innerHTML = `
            <tr>
                <td colspan="7">
                    No opportunities found.
                </td>
            </tr>
        `;

        return;

    }


    tbody.innerHTML =
        opportunities
            .map(
                renderOpportunityRow
            )
            .join("");

}


/* =========================================================
   OPPORTUNITY ROW
========================================================= */

function renderOpportunityRow(
    opportunity
) {

    const opportunityId =
        getOpportunityId(
            opportunity
        );
    const canEdit = [
        "Admin",
        "Manager",
        "Sales Executive",
        "Business Development Executive",
    ].includes(currentRoleName);
    const canDelete = currentRoleName === "Admin";


    const customer =
        allCustomers.find(
            item =>
                getCustomerId(item) ===
                Number(
                    opportunity.customer_id
                )
        );


    const customerName =
        customer
            ? customer.company
                ? `${customer.name} - ${customer.company}`
                : customer.name
            : (
                opportunity.customer_name ||
                opportunity.customer_id ||
                "-"
            );


    return `

        <tr>

            <td>
                ${escapeHtml(
                    opportunityId ??
                    opportunity._id ??
                    ""
                )}
            </td>

            <td>
                ${escapeHtml(
                    opportunity.name ||
                    ""
                )}
            </td>

            <td>
                ${escapeHtml(
                    customerName
                )}
            </td>

            <td>
                ${formatCurrency(
                    opportunity.amount
                )}
            </td>

            <td>
                ${escapeHtml(
                    opportunity.stage ||
                    ""
                )}
            </td>

            <td>
                ${escapeHtml(
                    opportunity.probability ??
                    0
                )}%
            </td>

            <td>

                ${
                    opportunityId !== null
                    ? `

                        ${canEdit ? `
                            <button
                                type="button"
                                onclick="editOpportunity(${opportunityId})"
                            >
                                ✏️ Edit
                            </button>
                        ` : ""}

                        ${canDelete ? `
                            <button
                                type="button"
                                onclick="deleteOpportunity(${opportunityId})"
                            >
                                🗑️ Delete
                            </button>
                        ` : ""}

                    `
                    : "Invalid ID"
                }

            </td>

        </tr>

    `;

}


/* =========================================================
   OPPORTUNITY FILTER
========================================================= */

function filterOpportunities(stage) {

    currentOpportunityFilter =
        stage;


    document
        .querySelectorAll(
            ".stage-filter"
        )
        .forEach(button => {

            button.classList.remove(
                "active"
            );

        });


    const selectedButton =
        document.querySelector(
            `.stage-filter[data-stage="${stage}"]`
        );


    if (selectedButton) {

        selectedButton.classList.add(
            "active"
        );

    }


    renderOpportunities();

}


/* =========================================================
   OPEN OPPORTUNITY MODAL
========================================================= */

async function openOpportunityModal() {

    const modal =
        document.getElementById(
            "opportunityModal"
        );

    const form =
        document.getElementById(
            "opportunityForm"
        );


    if (!modal) {
        return;
    }


    if (form) {
        form.reset();
    }


    editingOpportunityId =
        null;


    const title =
        modal.querySelector(
            ".modal-header h3"
        );


    if (title) {

        title.textContent =
            "Add Opportunity";

    }


    await loadCustomers();


    modal.style.display =
        "flex";

}


/* =========================================================
   CLOSE OPPORTUNITY MODAL
========================================================= */

function closeOpportunityModal() {

    const modal =
        document.getElementById(
            "opportunityModal"
        );


    const form =
        document.getElementById(
            "opportunityForm"
        );


    if (form) {
        form.reset();
    }


    editingOpportunityId =
        null;


    if (modal) {

        modal.style.display =
            "none";

    }

}


/* =========================================================
   OPPORTUNITY CREATE / UPDATE
========================================================= */

document.addEventListener(
    "submit",
    async function (event) {

        if (
            event.target.id !==
            "opportunityForm"
        ) {
            return;
        }


        event.preventDefault();


        const name =
            document
                .getElementById(
                    "opportunityName"
                )
                .value
                .trim();


        const customerId =
            document
                .getElementById(
                    "opportunityCustomer"
                )
                .value;


        const amount =
            Number(
                document
                    .getElementById(
                        "opportunityAmount"
                    )
                    .value
            );


        const stage =
            document
                .getElementById(
                    "opportunityStage"
                )
                .value;


        const probability =
            Number(
                document
                    .getElementById(
                        "opportunityProbability"
                    )
                    .value
            );


        if (!name) {

            alert(
                "Please enter opportunity name."
            );

            return;

        }


        if (!customerId) {

            alert(
                "Please select a customer."
            );

            return;

        }


        if (isNaN(amount) || amount < 0) {

            alert(
                "Please enter a valid amount."
            );

            return;

        }


        if (
            isNaN(probability) ||
            probability < 0 ||
            probability > 100
        ) {

            alert(
                "Probability must be between 0 and 100."
            );

            return;

        }


        const body = {

            name: name,

            customer_id:
                Number(customerId),

            amount: amount,

            stage: stage,

            probability: probability

        };


        console.log(
            "Opportunity request:",
            body
        );


        try {

            if (
                editingOpportunityId !==
                null
            ) {

                await apiRequest(
                    `/opportunities/${editingOpportunityId}`,
                    {
                        method: "PUT",
                        body:
                            JSON.stringify(body)
                    }
                );


                alert(
                    "Opportunity updated successfully."
                );


            } else {

                await apiRequest(
                    "/opportunities/",
                    {
                        method: "POST",
                        body:
                            JSON.stringify(body)
                    }
                );


                alert(
                    "Opportunity created successfully."
                );

            }


            closeOpportunityModal();


            await loadOpportunities();

            await loadDashboard();


        } catch (error) {

            console.error(
                "Opportunity save error:",
                error
            );


            alert(
                "Unable to save opportunity: " +
                error.message
            );

        }

    }
);


/* =========================================================
   EDIT OPPORTUNITY
========================================================= */

async function editOpportunity(
    opportunityId
) {

    opportunityId =
        Number(opportunityId);


    if (isNaN(opportunityId)) {

        alert(
            "Invalid opportunity ID."
        );

        return;

    }


    const opportunity =
        allOpportunities.find(
            item =>
                getOpportunityId(item) ===
                opportunityId
        );


    if (!opportunity) {

        alert(
            "Opportunity not found."
        );

        return;

    }


    editingOpportunityId =
        opportunityId;


    await loadCustomers();


    document.getElementById(
        "opportunityName"
    ).value =
        opportunity.name || "";


    document.getElementById(
        "opportunityCustomer"
    ).value =
        opportunity.customer_id || "";


    document.getElementById(
        "opportunityAmount"
    ).value =
        opportunity.amount ?? 0;


    document.getElementById(
        "opportunityStage"
    ).value =
        opportunity.stage ||
        "Prospecting";


    document.getElementById(
        "opportunityProbability"
    ).value =
        opportunity.probability ?? 0;


    const modal =
        document.getElementById(
            "opportunityModal"
        );


    const title =
        modal?.querySelector(
            ".modal-header h3"
        );


    if (title) {

        title.textContent =
            "Edit Opportunity";

    }


    if (modal) {

        modal.style.display =
            "flex";

    }

}


/* =========================================================
   DELETE OPPORTUNITY
========================================================= */

async function deleteOpportunity(
    opportunityId
) {

    opportunityId =
        Number(opportunityId);


    if (isNaN(opportunityId)) {

        alert(
            "Invalid opportunity ID."
        );

        return;

    }


    if (
        !confirm(
            "Are you sure you want to delete this opportunity?"
        )
    ) {

        return;

    }


    try {

        await apiRequest(
            `/opportunities/${opportunityId}`,
            {
                method: "DELETE"
            }
        );


        alert(
            "Opportunity deleted successfully."
        );


        await loadOpportunities();

        await loadDashboard();


    } catch (error) {

        console.error(
            "Delete opportunity error:",
            error
        );


        alert(
            "Unable to delete opportunity: " +
            error.message
        );

    }

}


/* =========================================================
   ACTIVITIES
========================================================= */

async function loadActivities() {

    const container =
        document.getElementById(
            "activitiesContent"
        );

    if (!container) {
        return;
    }


    container.innerHTML =
        "<p>Loading activities...</p>";


    try {

        const data =
            await apiRequest(
                "/activities/"
            );


        allActivities =
            extractArray(
                data,
                ["activities"]
            );


        if (!allActivities.length) {

            container.innerHTML =
                "<p>No activities found.</p>";

            return;

        }


        container.innerHTML = `

            <table class="crm-table">

                <thead>

                    <tr>

                        <th>ID</th>

                        <th>Subject</th>

                        <th>Type</th>

                        <th>Date</th>

                        <th>Actions</th>

                    </tr>

                </thead>

                <tbody>

                    ${
                        allActivities
                            .map(item => `

                                <tr>

                                    <td>
                                        ${escapeHtml(
                                            item.activity_id ||
                                            item.id ||
                                            item._id ||
                                            ""
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            item.subject ||
                                            item.title ||
                                            ""
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            item.type ||
                                            item.activity_type ||
                                            ""
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(formatDateTime(item.due_date))}
                                    </td>

                                    <td>

                                        <button
                                            type="button"
                                            onclick="editActivity('${escapeHtml(
                                                item.activity_id ||
                                                item.id ||
                                                item._id ||
                                                ""
                                            )}')"
                                        >
                                            ✏️ Edit
                                        </button>

                                        ${currentRoleName === "Admin" ? `
                                            <button
                                                type="button"
                                                onclick="deleteActivity('${escapeHtml(
                                                    item.activity_id ||
                                                    item.id ||
                                                    item._id ||
                                                    ""
                                                )}')"
                                            >
                                                🗑️ Delete
                                            </button>
                                        ` : ""}

                                    </td>

                                </tr>

                            `)
                            .join("")
                    }

                </tbody>

            </table>

        `;


    } catch (error) {

        console.error(
            "Activities error:",
            error
        );


        container.innerHTML =
            `<p class="error">
                Unable to load activities:
                ${escapeHtml(error.message)}
            </p>`;

    }

}


/* =========================================================
   ACTIVITY CREATE
========================================================= */

document.addEventListener(
    "submit",
    async function (event) {

        if (
            event.target.id !==
            "activityForm"
        ) {
            return;
        }


        event.preventDefault();

        const activityDate =
            document.getElementById("activityDate").value;

        const body = {

            subject:
                document
                    .getElementById(
                        "activitySubject"
                    )
                    .value
                    .trim(),

            activity_type:
                document
                    .getElementById(
                        "activityType"
                    )
                    .value
                    .trim() || "Task",

            due_date: activityDate
                ? `${activityDate}T10:00:00`
                : null
        };


        try {

            await apiRequest(
                "/activities/",
                {
                    method: "POST",
                    body:
                        JSON.stringify(body)
                }
            );


            alert(
                "Activity created successfully."
            );


            event.target.reset();


            await loadActivities();

            await loadDashboard();


        } catch (error) {

            console.error(
                "Create activity error:",
                error
            );


            alert(
                "Unable to create activity: " +
                error.message
            );

        }

    }
);


/* =========================================================
   ACTIVITY EDIT
========================================================= */

async function editActivity(id) {

    const activity =
        allActivities.find(
            item =>
                String(
                    item.activity_id ||
                    item.id ||
                    item._id
                ) === String(id)
        );


    if (!activity) {

        alert(
            "Activity not found."
        );

        return;

    }


    const subject =
        prompt(
            "Subject:",
            activity.subject || ""
        );


    if (subject === null) {
        return;
    }


    const type =
        prompt(
            "Type:",
            activity.type ||
            activity.activity_type ||
            ""
        );


    if (type === null) {
        return;
    }


    const date =
        prompt(
            "Due date (YYYY-MM-DD):",
            activity.due_date
                ? new Date(activity.due_date).toISOString().slice(0, 10)
                : ""
        );


    if (date === null) {
        return;
    }


    const body = {

        subject: subject.trim(),

        activity_type: type.trim(),

        due_date: date.trim()
            ? `${date.trim()}T10:00:00`
            : null

    };


    try {

        await apiRequest(
            `/activities/${id}`,
            {
                method: "PUT",
                body:
                    JSON.stringify(body)
            }
        );


        alert(
            "Activity updated successfully."
        );


        await loadActivities();


    } catch (error) {

        console.error(
            "Update activity error:",
            error
        );


        alert(
            "Unable to update activity: " +
            error.message
        );

    }

}


/* =========================================================
   ACTIVITY DELETE
========================================================= */

async function deleteActivity(id) {

    if (
        !confirm(
            "Delete this activity?"
        )
    ) {
        return;
    }


    try {

        await apiRequest(
            `/activities/${id}`,
            {
                method: "DELETE"
            }
        );


        alert(
            "Activity deleted successfully."
        );


        await loadActivities();

        await loadDashboard();


    } catch (error) {

        console.error(
            "Delete activity error:",
            error
        );


        alert(
            "Unable to delete activity: " +
            error.message
        );

    }

}


/* =========================================================
   FOLLOWUPS
========================================================= */

async function loadFollowups() {

    const container =
        document.getElementById(
            "followupsContent"
        );

    if (!container) {
        return;
    }


    container.innerHTML =
        "<p>Loading follow-ups...</p>";


    try {

        const data =
            await apiRequest(
                "/followups/"
            );


        allFollowups =
            extractArray(
                data,
                ["followups"]
            );


        if (!allFollowups.length) {

            container.innerHTML =
                "<p>No follow-ups found.</p>";

            return;

        }


        container.innerHTML = `

            <table class="crm-table">

                <thead>

                    <tr>

                        <th>ID</th>

                        <th>Lead ID</th>

                        <th>Subject</th>

                        <th>Date</th>

                        <th>Notes</th>

                        <th>Actions</th>

                    </tr>

                </thead>

                <tbody>

                    ${
                        allFollowups
                            .map(item => `

                                <tr>

                                    <td>
                                        ${escapeHtml(
                                            item.followup_id ||
                                            item.id ||
                                            item._id ||
                                            ""
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            item.lead_id ??
                                            ""
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(item.subject || "Follow-up")}
                                    </td>

                                    <td>
                                        ${escapeHtml(formatDateTime(item.next_followup_date))}
                                    </td>

                                    <td>
                                        ${escapeHtml(item.notes || item.remarks || "")}
                                    </td>

                                    <td>

                                        <button
                                            type="button"
                                            onclick="editFollowup('${escapeHtml(
                                                item.followup_id ||
                                                item.id ||
                                                item._id ||
                                                ""
                                            )}')"
                                        >
                                            ✏️ Edit
                                        </button>

                                        ${currentRoleName === "Admin" ? `
                                            <button
                                                type="button"
                                                onclick="deleteFollowup('${escapeHtml(
                                                    item.followup_id ||
                                                    item.id ||
                                                    item._id ||
                                                    ""
                                                )}')"
                                            >
                                                🗑️ Delete
                                            </button>
                                        ` : ""}

                                    </td>

                                </tr>

                            `)
                            .join("")
                    }

                </tbody>

            </table>

        `;


    } catch (error) {

        console.error(
            "Followups error:",
            error
        );


        container.innerHTML =
            `<p class="error">
                Unable to load follow-ups:
                ${escapeHtml(error.message)}
            </p>`;

    }

}


/* =========================================================
   FOLLOWUP CREATE
========================================================= */

document.addEventListener(
    "submit",
    async function (event) {

        if (
            event.target.id !==
            "followupForm"
        ) {
            return;
        }


        event.preventDefault();

        const leadId = Number(
            document.getElementById("followupLeadId").value
        );
        const subject = document
            .getElementById("followupSubject")
            .value
            .trim();
        const date = document
            .getElementById("followupDate")
            .value;
        const notes = document
            .getElementById("followupNotes")
            .value
            .trim();

        if (!Number.isInteger(leadId)) {
            alert("Please enter a valid Lead ID.");
            return;
        }
        if (!subject) {
            alert("Please enter a subject.");
            return;
        }
        if (!date) {
            alert("Please select a follow-up date.");
            return;
        }

        const body = {
            lead_id: leadId,
            subject,
            next_followup_date: `${date}T10:00:00`,
            notes
        };


        try {

            await apiRequest(
                "/followups/",
                {
                    method: "POST",
                    body:
                        JSON.stringify(body)
                }
            );


            alert(
                "Follow-up created successfully."
            );


            event.target.reset();


            await loadFollowups();

            await loadDashboard();


        } catch (error) {

            console.error(
                "Create followup error:",
                error
            );


            alert(
                "Unable to create follow-up: " +
                error.message
            );

        }

    }
);


/* =========================================================
   FOLLOWUP EDIT
========================================================= */

async function editFollowup(id) {

    const item = allFollowups.find(
        followup =>
            Number(
                followup.followup_id ||
                followup.id ||
                followup._id
            ) === Number(id)
    );


    if (!item) {

        alert(
            "Follow-up not found."
        );

        return;
    }


    const subject = prompt(
        "Subject:",
        item.subject || "Follow-up"
    );

    if (subject === null) {
        return;
    }

    const date = prompt(
        "Next follow-up date (YYYY-MM-DD):",
        item.next_followup_date
            ? new Date(item.next_followup_date).toISOString().slice(0, 10)
            : ""
    );

    if (date === null) {
        return;
    }


    const notes = prompt(
        "Notes:",
        item.notes || item.remarks || ""
    );

    if (notes === null) {
        return;
    }


    const body = {
        subject: subject.trim(),
        notes: notes.trim(),
        next_followup_date: `${date.trim()}T10:00:00`
    };


    try {

        await apiRequest(
            `/followups/${id}`,
            {
                method: "PUT",
                body: JSON.stringify(body)
            }
        );


        alert(
            "Follow-up updated successfully."
        );


        await loadFollowups();


    } catch (error) {

        console.error(
            "Update followup error:",
            error
        );


        alert(
            "Unable to update follow-up: " +
            error.message
        );
    }
}

function formatDateTime(value) {
    return value ? new Date(value).toLocaleString() : "n/a";
}

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("userForm");
    if (form) {
        form.addEventListener("submit", async event => {
            event.preventDefault();
            try {
                await apiRequest("/users/", { method: "POST", body: JSON.stringify({
                    full_name: document.getElementById("userFullName").value.trim(),
                    email: document.getElementById("userEmail").value.trim(),
                    mobile_no: document.getElementById("userMobile").value.trim(),
                    password: document.getElementById("userPassword").value,
                    role_id: Number(document.getElementById("userRole").value)
                }) });
                form.reset();
                await loadAdminData();
            } catch (error) { alert(error.message); }
        });
    }

    const roleForm = document.getElementById("roleForm");
    if (roleForm) {
        roleForm.addEventListener("submit", async event => {
            event.preventDefault();
            try {
                await apiRequest("/roles/", {
                    method: "POST",
                    body: JSON.stringify({
                        role_name: document.getElementById("roleName").value.trim(),
                        permissions: ["dashboard.view"]
                    })
                });
                roleForm.reset();
                await loadAdminData();
            } catch (error) { alert(error.message); }
        });
    }
});


/* =========================================================
   FOLLOWUP DELETE
========================================================= */

async function deleteFollowup(id) {

    if (
        !confirm(
            "Delete this follow-up?"
        )
    ) {
        return;
    }


    try {

        await apiRequest(
            `/followups/${id}`,
            {
                method: "DELETE"
            }
        );


        alert(
            "Follow-up deleted successfully."
        );


        await loadFollowups();

        await loadDashboard();


    } catch (error) {

        console.error(
            "Delete followup error:",
            error
        );


        alert(
            "Unable to delete follow-up: " +
            error.message
        );

    }

}


/* =========================================================
   TICKETS
========================================================= */

async function loadTickets() {

    const container =
        document.getElementById(
            "ticketsContent"
        );

    if (!container) {
        return;
    }


    container.innerHTML =
        "<p>Loading tickets...</p>";


    try {

        const data =
            await apiRequest(
                "/tickets/"
            );


        allTickets =
            extractArray(
                data,
                ["tickets"]
            );


        if (!allTickets.length) {

            container.innerHTML =
                "<p>No tickets found.</p>";

            return;

        }


        container.innerHTML = `

            <table class="crm-table">

                <thead>

                    <tr>

                        <th>ID</th>

                        <th>Title</th>

                        <th>Priority</th>

                        <th>Description</th>

                        <th>Status</th>

                        <th>Actions</th>

                    </tr>

                </thead>

                <tbody>

                    ${
                        allTickets
                            .map(item => `

                                <tr>

                                    <td>
                                        ${escapeHtml(
                                            item.ticket_id ||
                                            item.id ||
                                            item._id ||
                                            ""
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            item.title ||
                                            item.subject ||
                                            ""
                                        )}
                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            item.priority ||
                                            ""
                                        )}
                                    </td>

                                    <td>

                                        ${escapeHtml(
                                            item.description ||
                                            ""
                                        )}

                                    </td>

                                    <td>
                                        ${escapeHtml(
                                            item.status ||
                                            ""
                                        )}
                                    </td>

                                    <td>

                                        <button
                                            type="button"
                                            onclick="editTicket('${escapeHtml(
                                                item.ticket_id ||
                                                item.id ||
                                                item._id ||
                                                ""
                                            )}')"
                                        >
                                            ✏️ Edit
                                        </button>

                                        ${currentRoleName === "Admin" ? `
                                            <button
                                                type="button"
                                                onclick="deleteTicket('${escapeHtml(
                                                    item.ticket_id ||
                                                    item.id ||
                                                    item._id ||
                                                    ""
                                                )}')"
                                            >
                                                🗑️ Delete
                                            </button>
                                        ` : ""}

                                    </td>

                                </tr>

                            `)
                            .join("")
                    }

                </tbody>

            </table>

        `;


    } catch (error) {

        console.error(
            "Tickets error:",
            error
        );


        container.innerHTML =
            `<p class="error">
                Unable to load tickets:
                ${escapeHtml(error.message)}
            </p>`;

    }

}


/* =========================================================
   TICKET CREATE
========================================================= */

document.addEventListener(
    "submit",
    async function (event) {

        if (
            event.target.id !==
            "ticketForm"
        ) {
            return;
        }


        event.preventDefault();


        const body = {

            title:
                document
                    .getElementById(
                        "ticketTitle"
                    )
                    .value
                    .trim(),

            priority:
                document
                    .getElementById(
                        "ticketPriority"
                    )
                    .value,

            description:
                document
                    .getElementById(
                        "ticketDescription"
                    )
                    .value
                    .trim(),

            status:
                document
                    .getElementById(
                        "ticketStatus"
                    )
                    .value

        };



        try {

            await apiRequest(
                "/tickets/",
                {
                    method: "POST",
                    body:
                        JSON.stringify(body)
                }
            );


            alert(
                "Ticket created successfully."
            );


            event.target.reset();


            await loadTickets();

            await loadDashboard();


        } catch (error) {

            console.error(
                "Create ticket error:",
                error
            );


            alert(
                "Unable to create ticket: " +
                error.message
            );

        }

    }
);


/* =========================================================
   TICKET EDIT
========================================================= */

async function editTicket(id) {

    const ticket =
        allTickets.find(
            item =>
                String(
                    item.ticket_id ||
                    item.id ||
                    item._id
                ) === String(id)
        );


    if (!ticket) {

        alert(
            "Ticket not found."
        );

        return;

    }


    const title =
        prompt(
            "Title:",
            ticket.title ||
            ticket.subject ||
            ""
        );


    if (title === null) {
        return;
    }


    const priority =
        prompt(
            "Priority:",
            ticket.priority || "Medium"
        );


    if (priority === null) {
        return;
    }


    const status =
        prompt(
            "Status:",
            ticket.status || "Open"
        );


    if (status === null) {
        return;
    }


    const description =
        prompt(
            "Description:",
            ticket.description || ""
        );


    if (description === null) {
        return;
    }


    const body = {

        title: title.trim(),

        priority: priority.trim(),

        description:
            description.trim(),

        status: status.trim()

        

    };


    try {

        await apiRequest(
            `/tickets/${id}`,
            {
                method: "PUT",
                body:
                    JSON.stringify(body)
            }
        );


        alert(
            "Ticket updated successfully."
        );


        await loadTickets();


    } catch (error) {

        console.error(
            "Update ticket error:",
            error
        );


        alert(
            "Unable to update ticket: " +
            error.message
        );

    }

}


/* =========================================================
   TICKET DELETE
========================================================= */

async function deleteTicket(id) {

    if (
        !confirm(
            "Delete this ticket?"
        )
    ) {
        return;
    }


    try {

        await apiRequest(
            `/tickets/${id}`,
            {
                method: "DELETE"
            }
        );


        alert(
            "Ticket deleted successfully."
        );


        await loadTickets();

        await loadDashboard();


    } catch (error) {

        console.error(
            "Delete ticket error:",
            error
        );


        alert(
            "Unable to delete ticket: " +
            error.message
        );

    }

}


/* =========================================================
   NOTIFICATIONS
========================================================= */

async function loadNotifications() {

    const container =
        document.getElementById(
            "notificationsContent"
        );

    if (!container) {
        return;
    }


    container.innerHTML =
        "<p>Loading notifications...</p>";


    try {

        const data =
            await apiRequest(
                "/notifications/"
            );


        const notifications =
            extractArray(
                data,
                ["notifications"]
            );


        if (!notifications.length) {

            container.innerHTML =
                "<p>No notifications.</p>";

            return;

        }


        container.innerHTML =
            notifications
                .map(
                    item => `

                        <div class="notification-item">

                            <strong>
                                ${escapeHtml(
                                    item.title ||
                                    item.subject ||
                                    "Notification"
                                )}
                            </strong>

                            <p>
                                ${escapeHtml(
                                    item.message ||
                                    item.description ||
                                    ""
                                )}
                            </p>

                        </div>

                    `
                )
                .join("");


    } catch (error) {

        console.error(
            "Notifications error:",
            error
        );


        container.innerHTML =
            `<p class="error">
                Unable to load notifications:
                ${escapeHtml(error.message)}
            </p>`;

    }

}


/* =========================================================
   REPORTS
========================================================= */

async function loadReports() {

    const container =
        document.getElementById(
            "reportsContent"
        );

    if (!container) {
        return;
    }


    container.innerHTML =
        "<p>Loading reports...</p>";


    try {

        const [
            leads,
            opportunities,
            activities,
            tickets,
            revenue
        ] =
            await Promise.all([

                apiRequest(
                    "/dashboard/leads"
                ),

                apiRequest(
                    "/dashboard/opportunities"
                ),

                apiRequest(
                    "/dashboard/activities"
                ),

                apiRequest(
                    "/dashboard/tickets"
                ),

                apiRequest(
                    "/dashboard/revenue"
                )

            ]);


        container.innerHTML = `

            <div class="report-card">

                <h3>Lead Report</h3>

                <pre>
${escapeHtml(
    JSON.stringify(
        leads.report || leads,
        null,
        2
    )
)}
                </pre>

            </div>


            <div class="report-card">

                <h3>Opportunity Report</h3>

                <pre>
${escapeHtml(
    JSON.stringify(
        opportunities.report ||
        opportunities,
        null,
        2
    )
)}
                </pre>

            </div>


            <div class="report-card">

                <h3>Activity Report</h3>

                <pre>
${escapeHtml(
    JSON.stringify(
        activities.report ||
        activities,
        null,
        2
    )
)}
                </pre>

            </div>


            <div class="report-card">

                <h3>Ticket Report</h3>

                <pre>
${escapeHtml(
    JSON.stringify(
        tickets.report ||
        tickets,
        null,
        2
    )
)}
                </pre>

            </div>


            <div class="report-card">

                <h3>Revenue Report</h3>

                <pre>
${escapeHtml(
    JSON.stringify(
        revenue.revenue ||
        revenue,
        null,
        2
    )
)}
                </pre>

            </div>

        `;


    } catch (error) {

        console.error(
            "Reports error:",
            error
        );


        container.innerHTML =
            `<p class="error">
                Unable to load reports:
                ${escapeHtml(error.message)}
            </p>`;

    }

}


async function performSearch() {

    const input =
        document.getElementById(
            "globalSearch"
        );

    const container =
        document.getElementById(
            "searchResults"
        );


    if (!input || !container) {
        return;
    }


    const query =
        input.value
            .trim()
            .toLowerCase();


    if (!query) {

        container.innerHTML =
            "<p>Please enter something to search.</p>";

        return;
    }


    container.innerHTML =
        "<p>Searching...</p>";


    try {

        const permittedSections = new Set(sectionsForCurrentUser());
        const permittedLoads = [];
        if (permittedSections.has("leads")) permittedLoads.push(loadLeads());
        if (permittedSections.has("customers")) permittedLoads.push(loadCustomers());
        if (permittedSections.has("opportunities")) permittedLoads.push(loadOpportunities());
        await Promise.all(permittedLoads);

        // rest of your existing search code...


        const leadResults =
            allLeads.filter(
                item =>
                    JSON.stringify(item)
                        .toLowerCase()
                        .includes(query)
            );


        const customerResults =
            allCustomers.filter(
                item =>
                    JSON.stringify(item)
                        .toLowerCase()
                        .includes(query)
            );


        const opportunityResults =
            allOpportunities.filter(
                item =>
                    JSON.stringify(item)
                        .toLowerCase()
                        .includes(query)
            );


        container.innerHTML = `

            <h3>
                Search Results
            </h3>


            <h4>
                Leads (${leadResults.length})
            </h4>

            ${
                leadResults.length
                ? `
                    <ul>
                        ${
                            leadResults
                                .map(
                                    item => `
                                        <li>
                                            ${escapeHtml(
                                                item.name ||
                                                ""
                                            )}
                                            -
                                            ${escapeHtml(
                                                item.email ||
                                                ""
                                            )}
                                        </li>
                                    `
                                )
                                .join("")
                        }
                    </ul>
                `
                : "<p>No leads found.</p>"
            }


            <h4>
                Customers (${customerResults.length})
            </h4>

            ${
                customerResults.length
                ? `
                    <ul>
                        ${
                            customerResults
                                .map(
                                    item => `
                                        <li>
                                            ${escapeHtml(
                                                item.name ||
                                                ""
                                            )}
                                            -
                                            ${escapeHtml(
                                                item.company ||
                                                ""
                                            )}
                                        </li>
                                    `
                                )
                                .join("")
                        }
                    </ul>
                `
                : "<p>No customers found.</p>"
            }


            <h4>
                Opportunities (${opportunityResults.length})
            </h4>

            ${
                opportunityResults.length
                ? `
                    <ul>
                        ${
                            opportunityResults
                                .map(
                                    item => `
                                        <li>
                                            ${escapeHtml(
                                                item.name ||
                                                ""
                                            )}
                                            -
                                            ${formatCurrency(
                                                item.amount
                                            )}
                                            -
                                            ${escapeHtml(
                                                item.stage ||
                                                ""
                                            )}
                                        </li>
                                    `
                                )
                                .join("")
                        }
                    </ul>
                `
                : "<p>No opportunities found.</p>"
            }

        `;


    } catch (error) {

        console.error(
            "Search error:",
            error
        );


        container.innerHTML =
            `<p class="error">
                Search failed:
                ${escapeHtml(error.message)}
            </p>`;

    }

}


/* =========================================================
   ADMIN CENTER - LOAD USERS + ROLES
========================================================= */

const MANAGED_PERMISSIONS = [
    ["dashboard.view", "View dashboard"],
    ["leads.view", "View leads"],
    ["leads.create", "Create leads"],
    ["leads.update", "Update leads"],
    ["leads.delete", "Delete leads"],
    ["leads.convert", "Convert leads"],
    ["customers.view", "View customers"],
    ["customers.create", "Create customers"],
    ["customers.update", "Update customers"],
    ["customers.delete", "Delete customers"],
    ["followups.view", "View follow-ups"],
    ["followups.create", "Create follow-ups"],
    ["followups.update", "Update follow-ups"],
    ["followups.delete", "Delete follow-ups"]
];

async function loadAdminData() {

    const usersContent =
        document.getElementById("usersContent");

    const rolesContent =
        document.getElementById("rolesContent");

    const userRole =
        document.getElementById("userRole");

    if (!usersContent || !rolesContent) {
        console.warn("Admin elements not found.");
        return;
    }

    const roleName = String(
        currentRoleName ||
        localStorage.getItem("role_name") ||
        ""
    ).trim().toLowerCase();

    if (roleName !== "admin") {
        console.warn(
            "Admin data blocked. Current role:",
            roleName
        );
        return;
    }

    /* Show loading */
    usersContent.innerHTML =
        `<p>Loading users...</p>`;

    rolesContent.innerHTML =
        `<p>Loading roles...</p>`;

    try {

        console.log("Loading Admin Center...");

        const [usersResponse, rolesResponse] =
            await Promise.all([
                apiRequest("/users/"),
                apiRequest("/roles/")
            ]);

        console.log("Users API response:", usersResponse);
        console.log("Roles API response:", rolesResponse);


        /* =====================================================
           ROLES
        ===================================================== */

        const roleList =
            extractArray(
                rolesResponse,
                ["roles", "data", "items"]
            );

        console.log(
            "Roles loaded:",
            roleList
        );


        /* Populate role dropdown */

        if (userRole) {

            userRole.innerHTML =
                `<option value="">
                    Select role
                </option>` +

                roleList
                    .map(role => {

                        const roleId =
                            role.role_id ??
                            role.id ??
                            "";

                        const roleName =
                            role.role_name ??
                            role.name ??
                            "";

                        return `
                            <option value="${roleId}">
                                ${escapeHtml(roleName)}
                            </option>
                        `;
                    })
                    .join("");
        }


        /* Display roles */

        if (!roleList.length) {

            rolesContent.innerHTML =
                `<p>No roles found.</p>`;

        } else {

            rolesContent.innerHTML = roleList.map(role => {
                const name = role.role_name ?? role.name ?? "Unknown Role";
                const permissions = Array.isArray(role.permissions) ? role.permissions : [];
                return `
                    <div class="role-permission-editor" data-role-name="${escapeHtml(name)}">
                        <strong>${escapeHtml(name)}</strong>
                        <small>Created ${formatDateTime(role.created_at)}</small>
                        <div class="permission-options">
                            ${MANAGED_PERMISSIONS.map(([key, label]) => `
                                <label>
                                    <input type="checkbox" value="${key}"
                                        ${permissions.includes(key) ? "checked" : ""}>
                                    ${label}
                                </label>
                            `).join("")}
                        </div>
                        <button type="button" onclick="saveRolePermissions(${Number(role.role_id)}, this)">
                            Save permissions
                        </button>
                    </div>
                `;
            }).join("");
        }


        /* =====================================================
           USERS
        ===================================================== */

        const userList =
            extractArray(
                usersResponse,
                ["users", "data", "items"]
            );
        adminUsers = userList;

        console.log(
            "Users loaded:",
            userList
        );


        if (!userList.length) {

            usersContent.innerHTML =
                `<p>No users found.</p>`;

        } else {

            usersContent.innerHTML =
                userList
                    .map(user => {

                        const name =
                            user.full_name ??
                            user.name ??
                            "Unknown User";

                        const email =
                            user.email ??
                            "";

                        const active =
                            user.is_active !== false;

                        const role =
                            user.role_name ??
                            user.role ??
                            "";
                        const assignedRoleId = Number(user.role_id);

                        return `
                            <div class="list-item">

                                <div>

                                    <strong>
                                        ${escapeHtml(name)}
                                    </strong>

                                    <br>

                                    <small>
                                        ${escapeHtml(email)}
                                    </small>

                                    ${
                                        role
                                            ? `
                                                <br>
                                                <small>
                                                    Role: ${escapeHtml(role)}
                                                </small>
                                              `
                                            : ""
                                    }

                                    <div class="role-assignment">
                                        <select id="assignedRole-${Number(user.user_id)}" aria-label="Role for ${escapeHtml(name)}">
                                            ${roleList.map(option => `
                                                <option value="${Number(option.role_id)}"
                                                    ${Number(option.role_id) === assignedRoleId ? "selected" : ""}>
                                                    ${escapeHtml(option.role_name)}
                                                </option>
                                            `).join("")}
                                        </select>
                                        <button type="button" onclick="updateUserRole(${Number(user.user_id)})">
                                            Save role
                                        </button>
                                    </div>
                                </div>

                                <small>
                                    ${
                                        active
                                            ? "Active"
                                            : "Inactive"
                                    }

                                    <br>

                                    Updated
                                    ${formatDateTime(
                                        user.updated_at
                                    )}
                                </small>

                            </div>
                        `;
                    })
                    .join("");
        }

        console.log(
            "Admin Center loaded successfully."
        );

    } catch (error) {

        console.error(
            "Admin Center loading error:",
            error
        );

        usersContent.innerHTML = `
            <p class="error">
                Unable to load users.
                ${escapeHtml(error.message)}
            </p>
        `;

        rolesContent.innerHTML = `
            <p class="error">
                Unable to load roles.
                ${escapeHtml(error.message)}
            </p>
        `;
    }
}

async function saveRolePermissions(roleId, button) {
    const editor = button.closest(".role-permission-editor");
    const permissions = [...editor.querySelectorAll("input:checked")]
        .map(input => input.value);
    button.disabled = true;
    try {
        await apiRequest(`/roles/${roleId}`, {
            method: "PUT",
            body: JSON.stringify({
                role_name: editor.dataset.roleName,
                permissions
            })
        });
        await loadAdminData();
    } catch (error) {
        alert(error.message);
    } finally {
        button.disabled = false;
    }
}

async function updateUserRole(userId) {
    const user = adminUsers.find(item => Number(item.user_id) === Number(userId));
    const roleSelect = document.getElementById(`assignedRole-${Number(userId)}`);
    if (!user || !roleSelect) return;
    try {
        await apiRequest(`/users/${Number(userId)}`, {
            method: "PUT",
            body: JSON.stringify({
                full_name: user.full_name,
                email: user.email,
                mobile_no: user.mobile_no,
                password: "",
                role_id: Number(roleSelect.value)
            })
        });
        await loadAdminData();
    } catch (error) {
        alert(error.message);
    }
}

/* =========================================================
   CURRENT USER
========================================================= */

async function loadUser() {

    const userInfo =
        document.getElementById(
            "userInfo"
        );


    if (!userInfo) {
        return;
    }


    try {

        const data =
            await apiRequest(
                "/auth/me"
            );


        const user = data.user || data;
        const roleName = normalizeRoleName(user.role_name || localStorage.getItem("role_name") || "User");
        currentRoleName = roleName;
        currentPermissions = Array.isArray(user.permissions) ? user.permissions : [];
        localStorage.setItem("role_name", roleName);
        applyRoleDashboard(roleName);
        applyRoleAccess(roleName);
        userInfo.textContent = `${user.full_name || user.name || user.email || "User"} · ${roleName}`;


    } catch (error) {

        console.error(
            "Load user error:",
            error
        );

        currentRoleName = "Viewer";
        currentPermissions = [];
        applyRoleDashboard(currentRoleName);
        applyRoleAccess(currentRoleName);
        userInfo.textContent = `${localStorage.getItem("email") || "User"} · ${currentRoleName}`;

    }

}

const ROLE_ACCESS = {
    Admin: ["dashboard", "leads", "customers", "opportunities", "activities", "followups", "tickets", "notifications", "reports", "search", "admin"],
    "Sales Executive": ["dashboard", "leads", "customers", "opportunities", "activities", "followups", "search"],
    "Calling Executive": ["dashboard", "leads", "followups", "activities", "search"],
    "Support Executive": ["dashboard", "customers", "tickets", "notifications", "search"],
    Manager: ["dashboard", "leads", "customers", "opportunities", "activities", "followups", "tickets", "reports", "search"],
    "Marketing Executive": ["dashboard", "leads", "customers", "activities", "reports", "search"],
    HR: ["dashboard", "activities", "notifications", "reports", "search"],
    "Finance Executive": ["dashboard", "customers", "opportunities", "reports", "search"],
    "Team Lead": ["dashboard", "leads", "customers", "opportunities", "activities", "followups", "reports", "search"],
    "Business Development Executive": ["dashboard", "leads", "customers", "opportunities", "followups", "search"],
    "Operations Executive": ["dashboard", "customers", "activities", "tickets", "notifications", "reports", "search"],
    Viewer: ["dashboard", "reports", "search"]
};

const ROLE_DASHBOARDS = {
    Admin: { title: "Command Center", subtitle: "Monitor the whole CRM and manage team access.", cards: ["role-card-admin", "leads-card", "customers-card", "opportunities-card", "activities-card", "tickets-card", "revenue-card"] },
    "Sales Executive": { title: "Sales Workspace", subtitle: "Move prospects forward and keep every opportunity on track.", cards: ["leads-card", "customers-card", "opportunities-card", "activities-card", "revenue-card"] },
    "Calling Executive": { title: "Calling Desk", subtitle: "Work today’s outreach queue and scheduled follow-ups.", cards: ["leads-card", "activities-card", "followups-card"] },
    "Support Executive": { title: "Support Desk", subtitle: "Resolve customer requests and stay ahead of open tickets.", cards: ["customers-card", "tickets-card", "activities-card"] },
    Manager: { title: "Manager Overview", subtitle: "Coordinate team performance across the CRM.", cards: ["leads-card", "customers-card", "opportunities-card", "activities-card", "tickets-card", "revenue-card"] },
    "Marketing Executive": { title: "Marketing Workspace", subtitle: "Track campaign responses and nurture new prospects.", cards: ["leads-card", "customers-card", "activities-card"] },
    HR: { title: "People Operations", subtitle: "Review team activity and internal work queues.", cards: ["activities-card", "tickets-card"] },
    "Finance Executive": { title: "Revenue Insights", subtitle: "Review customer value and opportunity performance.", cards: ["customers-card", "opportunities-card", "revenue-card"] },
    "Team Lead": { title: "Team Lead Dashboard", subtitle: "Keep team pipelines, work, and follow-ups moving.", cards: ["leads-card", "customers-card", "opportunities-card", "activities-card", "revenue-card"] },
    "Business Development Executive": { title: "Business Development", subtitle: "Build pipeline from prospect to opportunity.", cards: ["leads-card", "customers-card", "opportunities-card", "revenue-card"] },
    "Operations Executive": { title: "Operations Desk", subtitle: "Monitor customer operations, tasks, and service issues.", cards: ["customers-card", "activities-card", "tickets-card"] },
    Viewer: { title: "Insights Dashboard", subtitle: "Review CRM performance and business activity.", cards: ["leads-card", "customers-card", "opportunities-card", "revenue-card"] }
};

function normalizeRoleName(roleName) {
    const raw = String(roleName ?? "").trim().replace(/\s+/g, " ");
    if (!raw) return "Viewer";

    const exactMatch = Object.keys(ROLE_ACCESS).find(
        key => key.toLowerCase() === raw.toLowerCase()
    );

    return exactMatch || raw;
}

function sectionsForCurrentUser() {
    const role = normalizeRoleName(currentRoleName);
    const knownRole = Object.keys(ROLE_ACCESS).includes(role);
    const sections = new Set(ROLE_ACCESS[knownRole ? role : "Viewer"]);
    const areaPermissions = {
        leads: "leads.view",
        customers: "customers.view",
        followups: "followups.view"
    };

    for (const [section, permission] of Object.entries(areaPermissions)) {
        if (isPermissionAllowed(permission)) sections.add(section);
        else sections.delete(section);
    }
    if (!knownRole) {
        for (const section of ["opportunities", "activities", "tickets", "notifications", "reports", "search", "admin"]) {
            sections.delete(section);
        }
    }
    sections.add("dashboard");
    return [...sections];
}

function isPermissionAllowed(permission) {
    return currentRoleName.toLowerCase() === "admin" ||
        currentPermissions.includes(permission);
}

function applyRoleDashboard(roleName) {
    const normalizedRole = normalizeRoleName(roleName);
    const dashboard = ROLE_DASHBOARDS[normalizedRole] || ROLE_DASHBOARDS.Viewer;
    document.getElementById("dashboardTitle").textContent = dashboard.title;
    document.getElementById("dashboardSubtitle").textContent = dashboard.subtitle;
    const cardMap = {
        totalLeads: "leads-card", totalCustomers: "customers-card", totalOpportunities: "opportunities-card",
        totalActivities: "activities-card", totalTickets: "tickets-card", wonRevenue: "revenue-card", totalUsers: "role-card-admin"
    };
    Object.entries(cardMap).forEach(([valueId, cardClass]) => {
        const value = document.getElementById(valueId);
        if (value) value.closest(".card").classList.toggle("role-hidden", !dashboard.cards.includes(cardClass));
    });
}

function applyRoleAccess(roleName) {
    const normalizedRole = normalizeRoleName(roleName);
    const allowedSections = sectionsForCurrentUser();
    document.querySelectorAll(".sidebar nav button[onclick]").forEach(button => {
        const match = button.getAttribute("onclick").match(/showSection\('([^']+)'\)/);
        if (match) button.hidden = !allowedSections.includes(match[1]);
    });
    document.querySelectorAll(".section").forEach(section => {
        section.hidden = !allowedSections.includes(section.id);
        section.classList.toggle("role-hidden", !allowedSections.includes(section.id));
    });
    if (!allowedSections.includes("admin")) {
        document.querySelectorAll(".admin-only").forEach(element => element.hidden = true);
    }

    const writePermissions = {
        leadForm: "leads.create",
        customerForm: "customers.create",
        followupForm: "followups.create",
        opportunityForm: null,
    };
    Object.entries(writePermissions).forEach(([formId, permission]) => {
        const form = document.getElementById(formId);
        if (form && permission) form.classList.toggle("role-hidden", !isPermissionAllowed(permission));
    });
    const opportunityRoles = ["Admin", "Manager", "Sales Executive", "Business Development Executive"];
    const opportunityCreateButton = document.querySelector(
        "#opportunities .section-actions .btn-primary"
    );
    if (opportunityCreateButton) {
        opportunityCreateButton.classList.toggle(
            "role-hidden",
            !opportunityRoles.includes(normalizedRole)
        );
    }

    const defaultSection = allowedSections.includes("dashboard") ? "dashboard" : allowedSections[0];
    showSection(defaultSection);
}


/* =========================================================
   LOGOUT
========================================================= */

function logout() {

    localStorage.removeItem(
        "access_token"
    );

    localStorage.removeItem(
        "refresh_token"
    );

    localStorage.removeItem(
        "user_id"
    );

    localStorage.removeItem(
        "email"
    );

    localStorage.removeItem(
        "role_id"
    );

    localStorage.removeItem(
        "role_name"
    );


    window.location.href =
        "login.html";

}


/* =========================================================
   CLOSE OPPORTUNITY MODAL
   WHEN CLICKING OUTSIDE
========================================================= */

document.addEventListener(
    "click",
    function (event) {

        const modal =
            document.getElementById(
                "opportunityModal"
            );


        if (
            modal &&
            event.target === modal
        ) {

            closeOpportunityModal();

        }

    }
);


/* =========================================================
   ESCAPE KEY - CLOSE MODAL
========================================================= */

document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Escape"
        ) {

            closeOpportunityModal();

        }

    }
);


/* =========================================================
   ENTER KEY SEARCH
========================================================= */

document.addEventListener(
    "keydown",
    function (event) {

        if (
            event.key === "Enter" &&
            document.activeElement?.id ===
            "globalSearch"
        ) {

            performSearch();

        }

    }
);

async function convertLead(id) {
    const leadId = Number(id);

    if (!Number.isInteger(leadId)) {
        alert("Invalid Lead ID.");
        return;
    }

    const confirmed = window.confirm(
        `Convert Lead #${leadId} to Customer?`
    );

    if (!confirmed) {
        return;
    }

    try {
        await apiRequest(
            `/leads/${leadId}/convert`,
            {
                method: "POST"
            }
        );

        alert("Lead converted successfully.");

        await loadLeads();
        await loadCustomers();
        await loadDashboard();

    } catch (error) {
        console.error("Convert lead error:", error);

        alert(
            "Unable to convert lead.\n\n" +
            error.message
        );
    }
}

/* =========================================================
   GLOBAL EXPORTS
========================================================= */

/*
   HTML onclick="..." requires functions
   to be available globally.
*/

window.showSection =
    showSection;

window.loadDashboard =
    loadDashboard;

window.loadLeads =
    loadLeads;

window.editLead =
    editLead;

window.deleteLead =
    deleteLead;

window.convertLead =
    convertLead;

window.loadCustomers =
    loadCustomers;

window.editCustomer =
    editCustomer;

window.deleteCustomer =
    deleteCustomer;

window.loadOpportunities =
    loadOpportunities;

window.filterOpportunities =
    filterOpportunities;

window.openOpportunityModal =
    openOpportunityModal;

window.closeOpportunityModal =
    closeOpportunityModal;

window.editOpportunity =
    editOpportunity;

window.deleteOpportunity =
    deleteOpportunity;

window.loadActivities =
    loadActivities;

window.editActivity =
    editActivity;

window.deleteActivity =
    deleteActivity;

window.loadFollowups =
    loadFollowups;

window.editFollowup =
    editFollowup;

window.deleteFollowup =
    deleteFollowup;

window.loadTickets =
    loadTickets;

window.editTicket =
    editTicket;

window.deleteTicket =
    deleteTicket;

window.loadNotifications =
    loadNotifications;

window.loadReports =
    loadReports;

window.performSearch =
    performSearch;

window.loadUser =
    loadUser;

window.logout =
    logout;
