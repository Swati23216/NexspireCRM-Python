const API_URL = window.location.origin;

console.log("API URL:", API_URL);

/* =========================================================
API REQUEST HELPER
========================================================= */

async function apiRequest(endpoint, options = {}) {


const token =
    localStorage.getItem("access_token");


const headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    ... (options.headers || {})
};


if (token) {

    headers["Authorization"] =
        `Bearer ${token}`;

}


console.log(
    `${options.method || "GET"} ${endpoint}`
);


try {

    const response =
        await fetch(
            `${API_URL}${endpoint}`,
            {
                ...options,
                headers
            }
        );


    console.log(
        `${endpoint} → ${response.status}`
    );


    /* -------------------------------------------------
       AUTHENTICATION ERROR
    ------------------------------------------------- */

    if (response.status === 401) {

        localStorage.clear();

        window.location.href =
            "login.html";

        return null;
    }


    /* -------------------------------------------------
       READ RESPONSE
    ------------------------------------------------- */

    const contentType =
        response.headers.get(
            "content-type"
        ) || "";


    let data;


    if (
        contentType.includes(
            "application/json"
        )
    ) {

        data =
            await response.json();

    } else {

        data =
            await response.text();

    }


    /* -------------------------------------------------
       API ERROR
    ------------------------------------------------- */

    if (!response.ok) {

        let message =
            "API request failed";


        if (
            typeof data === "object" &&
            data?.detail
        ) {

            if (
                typeof data.detail === "string"
            ) {

                message =
                    data.detail;

            } else {

                message =
                    JSON.stringify(
                        data.detail
                    );
            }

        } else if (
            typeof data === "string"
        ) {

            message =
                data;
        }


        throw new Error(
            `${response.status}: ${message}`
        );
    }


    return data;


} catch (error) {

    console.error(
        "API Error:",
        endpoint,
        error
    );

    throw error;
}


}

/* =========================================================
GET ARRAY FROM DIFFERENT RESPONSE FORMATS
========================================================= */

function extractArray(data, keys = []) {


if (Array.isArray(data)) {
    return data;
}


for (const key of keys) {

    if (Array.isArray(data?.[key])) {
        return data[key];
    }

}


if (Array.isArray(data?.items)) {
    return data.items;
}


if (Array.isArray(data?.data)) {
    return data.data;
}


return [];


}

/* =========================================================
HTML ESCAPE
========================================================= */

function escapeHtml(value) {


return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");


}

