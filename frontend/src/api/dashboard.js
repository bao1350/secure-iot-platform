import { apiFetch } from "./client";

export async function getDashboard() {
    return apiFetch("/sensors/dashboard");
}

export async function getSensor(sensorId) {
    return apiFetch(`/sensors/${sensorId}`);
}
