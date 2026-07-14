import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid
} from "recharts";

function getTickFormatter(period) {
    return (value) => {
        const date = new Date(value);
        if (isNaN(date.getTime())) {
            return value;
        }

        if (period === "today") {
            return `${date.getHours().toString().padStart(2, "0")}h`;
        }

        if (period === "week") {
            return date.toLocaleDateString("fr-FR", { weekday: "short" });
        }

        return date.toLocaleDateString("fr-FR", { day: "2-digit", month: "short" });
    };
}

function Chart({ title, data, dataKey, color, period }) {
    const tickFormatter = getTickFormatter(period);

    return (
        <div className="sensor-chart-section">
            <h4>{title}</h4>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 8, right: 20, left: 0, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" tick={{ fontSize: 11 }} tickFormatter={tickFormatter} />
                    <YAxis />
                    <Tooltip labelFormatter={t => new Date(t).toLocaleString()} />
                    <Line type="monotone" dataKey={dataKey} stroke={color} dot={false} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}

export default Chart;
