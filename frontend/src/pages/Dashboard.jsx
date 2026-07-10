import { useEffect, useState } from "react";


function Dashboard() {

    const [measure, setMeasure] = useState(null);


    useEffect(() => {

        fetch("http://localhost:8000/measures/latest")
            .then((response) => response.json())
            .then((data) => {
                setMeasure(data);
            })
            .catch((error) => {
                console.error(error);
            });


    }, []);



    return (

        <div className="dashboard">


            <h1>
                Secure IoT Dashboard
            </h1>


            {
                measure ? (

                    <div className="sensor-card">


                        <h2>
                            Capteur {measure.sensor_id}
                        </h2>


                        <p className="value">
                            🌡️ Température :
                            {measure.temperature} °C
                        </p>


                        <p className="value">
                            💧 Humidité :
                            {measure.humidity} %
                        </p>


                        <p className="value">
                            🔋 Batterie :
                            {measure.battery} %
                        </p>


                    </div>


                ) : (

                    <p>
                        Chargement...
                    </p>

                )
            }


        </div>

    );
}


export default Dashboard;