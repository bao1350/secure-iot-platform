function SensorCard({ sensor, deleteSensor, onOpenHistory }) {

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


            <button

                className="delete-button"

                onClick={() => {
                    if (window.confirm("Voulez-vous supprimer ce capteur ?")) {
                        deleteSensor(sensor.id);
                    }
                }}

            >

                Supprimer le capteur

            </button>

            <button

                className="history-button"

                onClick={()=>onOpenHistory(sensor.id)}

            >

                Voir l'historique

            </button>

        </div>

    );

}

export default SensorCard;