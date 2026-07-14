import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import SensorCard from "./SensorCard";
import CreateSensor from "./CreateSensor";
import SensorChart from "./Sensor_Chart";
import { getDashboard, getSensor } from "../api/dashboard";
import { deleteSensor as deleteSensorApi } from "../api/sensor";

function Dashboard(){

    const navigate = useNavigate();

    const [sensors, setSensors] = useState([]);
    const [selectedSensor, setSelectedSensor] = useState(null);


    useEffect(()=>{

        loadDashboard();

        const interval = setInterval(loadDashboard,5000);

        return ()=>clearInterval(interval);
    },[]);



    async function loadDashboard(){
        try {
            const res = await getDashboard();

            if(res.status === 401){
                logout();
                return;
            }

            const data = await res.json();

            if(data){
                setSensors(data);
            }
        }
        catch(error){
            console.log(error);
        }
    }


    async function openHistory(id){

        try{
            const res = await getSensor(id);

            if(res.status === 401){
                logout();
                return;
            }

            if(!res.ok){
                alert("Impossible de récupérer le capteur");
                return;
            }

            const json = await res.json();

            // backend returns { sensor: ..., latest_measure: ... }
            const sensor = json.sensor;

            // attach latest measure if present
            if(json.latest_measure){
                sensor.measure = json.latest_measure;
            }

            setSelectedSensor(sensor);

        }catch(e){
            console.error(e);
            alert("Erreur réseau lors de la récupération du capteur");
        }

    }



    async function deleteSensor(id){

        const token = localStorage.getItem("token");

        const oldSensors = [...sensors];

        setSensors(
            sensors.filter(sensor=>sensor.id!==id)
        );

        const response = await deleteSensorApi(id);

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

                                onOpenHistory={openHistory}

                            />

                        ))

                    }

                </div>

                {selectedSensor && (
                    <SensorChart
                        sensor={selectedSensor}
                        onClose={() => setSelectedSensor(null)}
                    />
                )}

            </div>

        </>

    );

}

export default Dashboard;