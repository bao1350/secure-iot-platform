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
            const labels = ["Dim", "Lun", "Mar", "Mer", "Jeu", "Ven", "Sam"];
            const dayIndex = date.getDay();
            return labels[dayIndex];
        }

        return date.getDate().toString();
    };
}

function getTicks(period) {
    const now = new Date();

    if (period === "today") {
        const start = new Date(now);
        start.setHours(0, 0, 0, 0);
        return [0, 6, 12, 18, 24].map((hour) => {
            const tick = new Date(start);
            tick.setHours(hour, 0, 0, 0);
            return tick.getTime();
        });
    }

    if (period === "week") {
        const day = now.getDay();
        const monday = new Date(now);
        monday.setDate(now.getDate() - ((day + 6) % 7));
        monday.setHours(0, 0, 0, 0);
        return Array.from({ length: 7 }, (_, index) => {
            const tick = new Date(monday);
            tick.setDate(monday.getDate() + index);
            return tick.getTime();
        });
    }

    const start = new Date(now);
    start.setDate(1);
    start.setHours(0, 0, 0, 0);
    return [1, 5, 10, 15, 20, 25, 30].map((dayNumber) => {
        const tick = new Date(start);
        tick.setDate(dayNumber);
        return tick.getTime();
    });
}

function Chart({ title, data, dataKey, color, period }) {
    const tickFormatter = getTickFormatter(period);
    const ticks = getTicks(period);

    const domain = ticks.length > 0 ? [ticks[0], ticks[ticks.length - 1]] : ["dataMin", "dataMax"];

    return (
        <div className="sensor-chart-section">
            <h4>{title}</h4>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data} margin={{ top: 8, right: 20, left: 0, bottom: 8 }}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                        type="number"
                        dataKey="time"
                        tick={{ fontSize: 11 }}
                        tickFormatter={tickFormatter}
                        ticks={ticks}
                        domain={domain}
                        interval={0}
                    />
                    <YAxis />
                    <Tooltip labelFormatter={t => new Date(t).toLocaleString()} />
                    <Line type="monotone" dataKey={dataKey} stroke={color} dot={false} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}

export default Chart;
