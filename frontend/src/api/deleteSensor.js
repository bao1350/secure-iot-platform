import { apiFetch } from "./client";

export default async function deleteSensor(id){
    return apiFetch(`/sensor/${id}`, {
        method: "DELETE"
    });
}
