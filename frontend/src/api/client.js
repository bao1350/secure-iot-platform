const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function csrfToken() {
    return document.cookie
        .split("; ")
        .find((cookie) => cookie.startsWith("csrf_token="))
        ?.split("=")[1];
}

function request(path, options = {}) {
    const headers = { ...(options.headers || {}) };
    if (!["GET", "HEAD", "OPTIONS"].includes((options.method || "GET").toUpperCase())) {
        const token = csrfToken();
        if (token) headers["X-CSRF-Token"] = token;
    }
    return fetch(`${BASE_URL}${path}`, {
        cache: "no-store",
        credentials: "include",
        ...options,
        headers,
    });
}

export async function apiFetch(path, options = {}) {
    let response = await request(path, options);
    if (response.status !== 401 || ["/auth/login", "/auth/refresh"].includes(path)) return response;

    const refreshed = await request("/auth/refresh", { method: "POST" });
    if (refreshed.ok) response = await request(path, options);
    return response;
}
