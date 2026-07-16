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
    const [liveMeasure, setLiveMeasure] = useState(null);


    useEffect(()=>{

        loadDashboard();

        const interval = setInterval(loadDashboard, 5000);

        const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
        const wsProtocol = apiUrl.startsWith("https") ? "wss" : "ws";
        const wsUrl = `${wsProtocol}://${new URL(apiUrl).host}/ws/dashboard`;
        const ws = new WebSocket(wsUrl);

        ws.onmessage = (event) => {
            try {
                const update = JSON.parse(event.data);

                setSensors(prev => prev.map(sensor =>
                    sensor.id === update.sensor_id
                        ? {
                            ...sensor,
                            measure: {
                                ...(sensor.measure || {}),
                                ...update,
                            },
                        }
                        : sensor
                ));

                const newSelected = selectedSensor && selectedSensor.id === update.sensor_id
                    ? {
                        ...selectedSensor,
                        measure: {
                            ...(selectedSensor.measure || {}),
                            ...update,
                        },
                    }
                    : selectedSensor;

                if (newSelected) {
                    setSelectedSensor(newSelected);
                }

                setLiveMeasure(update);
            }
            catch (error) {
                console.error("Erreur WebSocket :", error);
            }
        };

        ws.onopen = () => {
            console.log("WebSocket connecté", wsUrl);
        };

        ws.onclose = () => {
            console.log("WebSocket déconnecté");
        };

        ws.onerror = (error) => {
            console.error("WebSocket error", error);
        };

        return () => {
            clearInterval(interval);
            ws.close();
        };
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
                        liveMeasure={liveMeasure}
                        onClose={() => setSelectedSensor(null)}
                    />
                )}

            </div>

        </>

    );

}

export default Dashboard;