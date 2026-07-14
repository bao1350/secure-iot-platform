import { apiFetch } from "./client";

export async function createSensor(data) {
    return apiFetch("/sensor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
}

export async function deleteSensor(id) {
    return apiFetch(`/sensor/${id}`, {
        method: "DELETE"
    });
}

export async function getSensorHistory(id, period) {
    return apiFetch(`/sensor/${id}/history?period=${period}`);
}
