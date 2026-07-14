const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function getToken() {
    return localStorage.getItem("token");
}

export function getAuthHeaders(existingHeaders = {}) {
    const token = getToken();

    return {
        ...(existingHeaders || {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
}

export async function apiFetch(path, options = {}) {
    const headers = getAuthHeaders(options.headers);

    return fetch(`${BASE_URL}${path}`, {
        cache: "no-store",
        ...options,
        headers,
    });
}
