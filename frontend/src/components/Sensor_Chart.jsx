import { useEffect, useState } from "react";
import { getSensorHistory } from "../api/sensor";
import Chart from "./Chart";
import "./SensorChart.css";

function SensorChart({ sensor, onClose }){

    const [period, setPeriod] = useState("today");
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [autoRefresh, setAutoRefresh] = useState(true);
    const [refreshInterval, setRefreshInterval] = useState(5); // seconds
    const [lastUpdated, setLastUpdated] = useState(null);

    useEffect(()=>{

        if(!sensor) return;

        fetchData();

    },[sensor, period]);

    async function fetchData(){

        setLoading(true);

            try{
            const res = await getSensorHistory(sensor.id, period);

            if(res.status === 401){
                localStorage.removeItem("token");
                window.location = "/";
                return;
            }

            const json = await res.json();

            const mapped = json.map(m => ({
                time: m.timestamp,
                temperature: m.temperature,
                humidity: m.humidity,
                battery: m.battery
            }));

            // reverse so older -> newer for charts
            const raw = mapped.reverse();

            // use raw points (no aggregation)
            setData(raw);

        }catch(e){
            console.error(e);
        }finally{
            setLoading(false);
            setLastUpdated(new Date());
        }

    }


    useEffect(()=>{
        if(!sensor) return;

        if(!autoRefresh) return;

        const id = setInterval(()=>{
            fetchData();
        }, refreshInterval * 1000);

        return ()=>clearInterval(id);

    },[sensor, period, autoRefresh, refreshInterval]);


    

    return (

        <div className="sensor-chart-overlay">

            <div className="sensor-chart-panel">

                <div className="sensor-chart-header">
                    <h3>{sensor.name} — Historique</h3>
                    <div className="sensor-chart-controls">
                        <label>Période:</label>
                        <select value={period} onChange={e => setPeriod(e.target.value)}>
                            <option value="today">Aujourd'hui</option>
                            <option value="week">7 jours</option>
                            <option value="month">30 jours</option>
                        </select>
                        <button className="sensor-chart-close" onClick={onClose}>Fermer</button>
                    </div>
                </div>

                {loading && (
                    <div className="sensor-chart-loading">
                        <div className="spinner" />
                        <span>Chargement...</span>
                    </div>
                )}

                {!loading && data.length === 0 && <p>Aucune mesure pour cette période.</p>}

                {!loading && data.length > 0 && (

                    <>
                        <Chart title="Température (°C)" data={data} dataKey="temperature" color="#ff7300" period={period} />
                        <Chart title="Humidité (%)" data={data} dataKey="humidity" color="#00b894" period={period} />
                        <Chart title="Batterie (%)" data={data} dataKey="battery" color="#0984e3" period={period} />
                    </>

                )}

            </div>

        </div>

    );

}

export default SensorChart;
