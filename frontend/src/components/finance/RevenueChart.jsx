import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { formatCurrency, formatDate } from '../../utils/format';

/**
 * Renders a `revenue_series`/`sales_series` list from the finance API —
 * [{ bucket, revenue|sales, orders }, ...] — as a filled area chart.
 * `valueKey` picks which field to plot (admin's is `revenue`, vendor's is
 * `sales`) so this one component serves both dashboards.
 */
export function RevenueChart({ data, valueKey = 'revenue' }) {
  if (!data || data.length === 0) {
    return <p className="py-16 text-center text-sm text-ink-500">No activity in this period.</p>;
  }

  const chartData = data.map((point) => ({
    date: point.bucket,
    value: Number(point[valueKey] ?? 0),
  }));

  return (
    <ResponsiveContainer width="100%" height={260}>
      <AreaChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="financeAreaFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#FF5A1F" stopOpacity={0.35} />
            <stop offset="95%" stopColor="#FF5A1F" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="#DDE1EC" vertical={false} />
        <XAxis
          dataKey="date"
          tickFormatter={(value) => formatDate(value)}
          tick={{ fontSize: 11, fill: '#5F6B93' }}
          axisLine={false}
          tickLine={false}
          minTickGap={24}
        />
        <YAxis
          tickFormatter={(value) => formatCurrency(value)}
          tick={{ fontSize: 11, fill: '#5F6B93' }}
          axisLine={false}
          tickLine={false}
          width={84}
        />
        <Tooltip
          formatter={(value) => formatCurrency(value)}
          labelFormatter={(value) => formatDate(value)}
          contentStyle={{ borderRadius: 8, border: '1px solid #DDE1EC', fontSize: 12 }}
        />
        <Area type="monotone" dataKey="value" stroke="#FF5A1F" strokeWidth={2} fill="url(#financeAreaFill)" />
      </AreaChart>
    </ResponsiveContainer>
  );
}