import { useEffect, useState } from "react";
import SensorCard from "./SensorCard";

function Dashboard() {

    const [sensors, setSensors] = useState([]);

    useEffect(() => {

        loadDashboard();

        const interval = setInterval(loadDashboard, 5000);

        return () => clearInterval(interval);

    }, []);


    function loadDashboard() {

        fetch("http://localhost:8000/dashboard")
            .then((response) => response.json())
            .then((data) => {

                setSensors(data);

            })
            .catch((error) => {

                console.error(error);

            });

    }


    return (

        <div className="dashboard">

            <h1>Secure IoT Dashboard</h1>

            <h2>Nombre de capteurs : {sensors.length}</h2>

            <div className="sensor-card">

                {sensors.map((sensor) => (

                    <SensorCard

                        key={sensor.id}

                        sensor={sensor}

                    />

                ))}

            </div>

        </div>

    );

}

export default Dashboard;