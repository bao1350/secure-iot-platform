import { useState } from "react";


function CreateSensor({ refresh }){

    const [name,setName] = useState("");
    const [room,setRoom] = useState("");
    const [type,setType] = useState("");


    async function createSensor(){

        const token = localStorage.getItem("token");

        const response = await fetch(
            "http://localhost:8000/sensor",
            {
                method:"POST",

                headers:{
                    "Content-Type":"application/json",

                    "Authorization":
                    `Bearer ${token}`
                },

                body:JSON.stringify({

                    name:name,

                    room:room,

                    sensor_type:type

                })
            }
        );


        const data = await response.json();


        if(response.ok){

            alert("Capteur créé");
            refresh();

        }
        else{

            alert(data.detail);

        }

    }


    return(

        <div className="sensor-form">

            <h2>
                Ajouter un capteur
            </h2>


            <input
                placeholder="Nom"
                value={name}
                onChange={
                    e=>setName(e.target.value)
                }
            />


            <input
                placeholder="Pièce"
                value={room}
                onChange={
                    e=>setRoom(e.target.value)
                }
            />


            <input
                placeholder="Type (DHT22...)"
                value={type}
                onChange={
                    e=>setType(e.target.value)
                }
            />


            <button onClick={createSensor}>
                Ajouter
            </button>

        </div>

    );

}


export default CreateSensor;