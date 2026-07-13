export default async function deleteSensor(id){

    const token = localStorage.getItem("token");

    return fetch(
        `http://localhost:8000/sensor/${id}`,
        {
            method:"DELETE",
            headers:{
                Authorization:`Bearer ${token}`
            }
        }
    );

}