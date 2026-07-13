import { useEffect, useState } from "react";
import "./App.css";
import SensorCard from "./components/SensorCard";

function App() {

    const [sensors, setSensors] = useState([]);

    useEffect(() => {

        loadDashboard();

        const interval = setInterval(loadDashboard, 5000);

        return () => clearInterval(interval);

    }, []);

    function loadDashboard() {

        fetch("http://localhost:8000/dashboard")
            .then(response => response.json())
            .then(data => setSensors(data))
            .catch(error => console.log(error));

    }

    return (

      <><div className="title ">
        <h1>Secure IoT Dashboard</h1>
      </div><div className="container">

          <h3>Nombre de capteurs : {sensors.length}</h3>

          <div className="grid">

            {sensors.map(sensor => (

              <SensorCard
                key={sensor.id}
                sensor={sensor} />

            ))}

          </div>

        </div></>

    );

}

export default App;