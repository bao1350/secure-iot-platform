import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import SensorCard from "./SensorCard";
import CreateSensor from "./CreateSensor";

function Dashboard(){

    const navigate = useNavigate();

    const [sensors, setSensors] = useState([]);


    useEffect(()=>{

        loadDashboard();

        const interval = setInterval(loadDashboard,5000);

        return ()=>clearInterval(interval);

    },[]);



    function loadDashboard(){

        const token = localStorage.getItem("token");

        fetch("http://localhost:8000/dashboard",{

            headers:{
                Authorization:`Bearer ${token}`
            }

        })

        .then(response=>{

            if(response.status===401){

                logout();
                return;

            }

            return response.json();

        })

        .then(data=>{

            if(data){

                setSensors(data);

            }

        })

        .catch(error=>console.log(error));

    }



    async function deleteSensor(id){

        const token = localStorage.getItem("token");

        const oldSensors = [...sensors];

        setSensors(
            sensors.filter(sensor=>sensor.id!==id)
        );

        const response = await fetch(

            `http://localhost:8000/sensor/${id}`,

            {

                method:"DELETE",

                headers:{
                    Authorization:`Bearer ${token}`
                }

            }

        );

        // Si erreur, on remet les capteurs
        if(!response.ok){

            setSensors(oldSensors);

            alert("Erreur lors de la suppression");

        }

    }



    function logout(){

        localStorage.removeItem("token");

        navigate("/");

    }



    return(

        <>

            <button
                className="logout"
                onClick={logout}
            >
                Déconnexion
            </button>


            <div className="title">

                <h1>
                    Secure IoT Dashboard
                </h1>

            </div>


            <div className="container">

                <CreateSensor refresh={loadDashboard}/>

                <p className="sensor-count">

                    Nombre de capteurs : <strong>{sensors.length}</strong>

                </p>


                <div className="grid">

                    {

                        sensors.map(sensor=>(

                            <SensorCard

                                key={sensor.id}

                                sensor={sensor}

                                deleteSensor={deleteSensor}

                            />

                        ))

                    }

                </div>

            </div>

        </>

    );

}

export default Dashboard;