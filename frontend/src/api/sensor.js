import { apiFetch } from "./client";

export async function createSensor(data) {
    return apiFetch("/sensors", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
}

export async function deleteSensor(id) {
    return apiFetch(`/sensors/${id}`, {
        method: "DELETE"
    });
}

export async function getSensorHistory(id, period) {
    return apiFetch(`/sensors/${id}/history?period=${period}`);
}
