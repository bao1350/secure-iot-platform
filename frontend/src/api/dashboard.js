import { apiFetch } from "./client";

export async function getDashboard() {
    return apiFetch("/dashboard");
}

export async function getSensor(sensorId) {
    return apiFetch(`/sensor/${sensorId}`);
}
