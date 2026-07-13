function SensorCard({ sensor }) {

    return (

        <div className="sensor-card">

            <h2>
                {sensor.name}
            </h2>


            <p className="room">
                📍 {sensor.room}
            </p>


            <p className="type">
                Type : {sensor.sensor_type}
            </p>


            {sensor.measure ? (

                <>

                    <p className="value">
                        🌡️ Température : {sensor.measure.temperature} °C
                    </p>


                    <p className="value">
                        💧 Humidité : {sensor.measure.humidity} %
                    </p>


                    <p className="value">
                        🔋 Batterie : {sensor.measure.battery} %
                    </p>

                </>

            ) : (

                <p>
                    Aucune mesure disponible
                </p>

            )}

        </div>

    );

}


export default SensorCard;