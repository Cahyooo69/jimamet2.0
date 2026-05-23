"use client";

import { useState, useEffect, useRef } from "react";
import styles from "./dashboard.module.css";

/* ── Dummy Data ── */
const calorieData = [
  { day: "Sen", value: 1850, target: 2000 },
  { day: "Sel", value: 2100, target: 2000 },
  { day: "Rab", value: 1750, target: 2000 },
  { day: "Kam", value: 1950, target: 2000 },
  { day: "Jum", value: 2200, target: 2000 },
  { day: "Sab", value: 1680, target: 2000 },
  { day: "Min", value: 1920, target: 2000 },
];

const macroData = [
  { name: "Protein", value: 28, target: 35, color: "#2e7d32", unit: "g" },
  { name: "Karbo", value: 45, target: 50, color: "#4caf50", unit: "g" },
  { name: "Lemak", value: 22, target: 25, color: "#a5d6a7", unit: "g" },
  { name: "Serat", value: 8, target: 15, color: "#1b6d24", unit: "g" },
];

const todayMeals = [
  { time: "07:30", name: "Nasi Goreng Ayam", cal: 450, img: "🍚" },
  { time: "10:00", name: "Smoothie Bayam & Pisang", cal: 180, img: "🥤" },
  { time: "12:30", name: "Salmon Panggang + Sayur", cal: 520, img: "🐟" },
  { time: "15:00", name: "Alpukat Toast", cal: 280, img: "🥑" },
];

const nutrientDonut = [
  { name: "Protein", pct: 28, color: "#2e7d32" },
  { name: "Karbohidrat", pct: 45, color: "#4caf50" },
  { name: "Lemak", pct: 22, color: "#a5d6a7" },
  { name: "Serat", pct: 5, color: "#1b6d24" },
];

/* ── Simple Bar Chart (SVG) ── */
function BarChart() {
  const dataMax = Math.max(...calorieData.map((d) => Math.max(d.value, d.target)));
  const maxVal = Math.ceil(dataMax / 100) * 100 + 200; // headroom above tallest bar
  const barW = 36;
  const gap = 20;
  const chartH = 180;
  const chartW = calorieData.length * (barW + gap);

  return (
    <svg viewBox={`0 0 ${chartW + 40} ${chartH + 40}`} className={styles.chartSvg}>
      {/* Grid lines */}
      {[0, 0.25, 0.5, 0.75, 1].map((pct) => (
        <g key={pct}>
          <line
            x1="36" y1={chartH - chartH * pct + 12}
            x2={chartW + 36} y2={chartH - chartH * pct + 12}
            stroke="var(--surface-container-high)" strokeWidth="1"
          />
          <text x="0" y={chartH - chartH * pct + 16} fill="var(--outline)" fontSize="10" fontFamily="Inter">
            {Math.round(maxVal * pct)}
          </text>
        </g>
      ))}
      {/* Target line */}
      <line
        x1="36" y1={chartH - (2000 / maxVal) * chartH + 12}
        x2={chartW + 36} y2={chartH - (2000 / maxVal) * chartH + 12}
        stroke="#ff9800" strokeWidth="1.5" strokeDasharray="6 4"
      />
      {/* Bars */}
      {calorieData.map((d, i) => {
        const h = (d.value / maxVal) * chartH;
        const x = 40 + i * (barW + gap);
        const overTarget = d.value > d.target;
        return (
          <g key={d.day}>
            <rect
              x={x} y={chartH - h + 12} width={barW} height={h}
              rx="6" ry="6"
              fill={overTarget ? "url(#barOver)" : "url(#barNormal)"}
              className={styles.bar}
            />
            <text x={x + barW / 2} y={chartH + 30} textAnchor="middle" fill="var(--on-surface-variant)" fontSize="12" fontFamily="Inter" fontWeight="500">
              {d.day}
            </text>
            <text x={x + barW / 2} y={chartH - h + 6} textAnchor="middle" fill="var(--on-surface-variant)" fontSize="10" fontFamily="Inter">
              {d.value}
            </text>
          </g>
        );
      })}
      <defs>
        <linearGradient id="barNormal" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#4caf50" />
          <stop offset="100%" stopColor="#2e7d32" />
        </linearGradient>
        <linearGradient id="barOver" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#ff9800" />
          <stop offset="100%" stopColor="#f57c00" />
        </linearGradient>
      </defs>
    </svg>
  );
}

/* ── Donut Chart ── */
function DonutChart() {
  const size = 160;
  const cx = size / 2;
  const cy = size / 2;
  const r = 60;
  const circumference = 2 * Math.PI * r;
  let offset = 0;

  return (
    <div className={styles.donutWrapper}>
      <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size}>
        {nutrientDonut.map((seg) => {
          const dash = (seg.pct / 100) * circumference;
          const gapSize = 4;
          const el = (
            <circle
              key={seg.name}
              cx={cx} cy={cy} r={r}
              fill="none"
              stroke={seg.color}
              strokeWidth="20"
              strokeDasharray={`${dash - gapSize} ${circumference - dash + gapSize}`}
              strokeDashoffset={-offset}
              strokeLinecap="butt"
              transform={`rotate(-90 ${cx} ${cy})`}
              className={styles.donutSegment}
            />
          );
          offset += dash;
          return el;
        })}
        <text x={cx} y={cy - 6} textAnchor="middle" fill="var(--on-surface)" fontSize="22" fontWeight="700" fontFamily="Plus Jakarta Sans">
          1,430
        </text>
        <text x={cx} y={cy + 12} textAnchor="middle" fill="var(--on-surface-variant)" fontSize="11" fontFamily="Inter">
          / 2,000 kkal
        </text>
      </svg>
      <div className={styles.donutLegend}>
        {nutrientDonut.map((seg) => (
          <div key={seg.name} className={styles.legendItem}>
            <span className={styles.legendDot} style={{ background: seg.color }} />
            <span className={styles.legendLabel}>{seg.name}</span>
            <span className={styles.legendValue}>{seg.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Macro Progress ── */
function MacroProgress({ data }: { data: typeof macroData[0] }) {
  const pct = Math.min((data.value / data.target) * 100, 100);
  return (
    <div className={styles.macroItem}>
      <div className={styles.macroTop}>
        <span className={styles.macroName}>{data.name}</span>
        <span className={styles.macroValue}>{data.value}{data.unit} <span className={styles.macroTarget}>/ {data.target}{data.unit}</span></span>
      </div>
      <div className={styles.macroTrack}>
        <div className={styles.macroFill} style={{ width: `${pct}%`, background: data.color }} />
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════
   DASHBOARD PAGE
   ═══════════════════════════════════════════════════ */
export default function DashboardPage() {
  const [greeting, setGreeting] = useState("Selamat Pagi");

  useEffect(() => {
    const h = new Date().getHours();
    if (h >= 5 && h < 11) setGreeting("Selamat Pagi");
    else if (h >= 11 && h < 15) setGreeting("Selamat Siang");
    else if (h >= 15 && h < 18) setGreeting("Selamat Sore");
    else setGreeting("Selamat Malam");
  }, []);

  return (
    <div className={styles.dashboard}>
      {/* ── Header ── */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.greeting}>{greeting}, User! 👋</h1>
          <p className={styles.subtitle}>Pantau asupan nutrisi harian Anda untuk mencapai target kesehatan.</p>
        </div>
        <div className={styles.headerActions}>
          <span className={styles.dateBadge}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
            {new Date().toLocaleDateString("id-ID", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
          </span>
        </div>
      </div>

      {/* ── Stat Cards ── */}
      <div className={styles.statCards}>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: "rgba(46,125,50,0.08)", color: "#2e7d32" }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M12 2a4 4 0 0 1 4 4c0 1.95-1.4 3.58-3.25 3.93L12 22M12 2a4 4 0 0 0-4 4c0 1.95 1.4 3.58 3.25 3.93" strokeLinecap="round" strokeLinejoin="round" /></svg>
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Kalori Hari Ini</span>
            <span className={styles.statValue}>1,430</span>
            <span className={styles.statMeta}>/ 2,000 kkal</span>
          </div>
          <div className={styles.statProgress}><div style={{ width: "71.5%", background: "linear-gradient(90deg, #2e7d32, #4caf50)" }} /></div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: "rgba(76,175,80,0.08)", color: "#4caf50" }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Protein</span>
            <span className={styles.statValue}>28g</span>
            <span className={styles.statMeta}>/ 35g target</span>
          </div>
          <div className={styles.statProgress}><div style={{ width: "80%", background: "linear-gradient(90deg, #4caf50, #a5d6a7)" }} /></div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: "rgba(255,152,0,0.08)", color: "#ff9800" }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><path d="M8 14s1.5 2 4 2 4-2 4-2" /><line x1="9" y1="9" x2="9.01" y2="9" /><line x1="15" y1="9" x2="15.01" y2="9" /></svg>
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Mood Nutrisi</span>
            <span className={styles.statValue}>Baik</span>
            <span className={styles.statMeta}>Seimbang hari ini</span>
          </div>
          <div className={styles.statProgress}><div style={{ width: "85%", background: "linear-gradient(90deg, #ff9800, #ffb74d)" }} /></div>
        </div>

        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: "rgba(33,150,243,0.08)", color: "#2196f3" }}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" /></svg>
          </div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Air Minum</span>
            <span className={styles.statValue}>1.6L</span>
            <span className={styles.statMeta}>/ 2.5L target</span>
          </div>
          <div className={styles.statProgress}><div style={{ width: "64%", background: "linear-gradient(90deg, #2196f3, #64b5f6)" }} /></div>
        </div>
      </div>

      {/* ── Charts Row ── */}
      <div className={styles.chartsRow}>
        {/* Bar Chart */}
        <div className={styles.chartCard}>
          <div className={styles.chartHeader}>
            <div>
              <h3>Tren Kalori 7 Hari Terakhir</h3>
              <p>Target harian: 2,000 kkal</p>
            </div>
            <div className={styles.chartLegendInline}>
              <span><span className={styles.legendDotInline} style={{ background: "#2e7d32" }} /> Normal</span>
              <span><span className={styles.legendDotInline} style={{ background: "#ff9800" }} /> Over</span>
              <span className={styles.targetLine}>--- Target</span>
            </div>
          </div>
          <BarChart />
        </div>

        {/* Donut Chart */}
        <div className={styles.chartCard}>
          <div className={styles.chartHeader}>
            <div>
              <h3>Distribusi Nutrisi Hari Ini</h3>
              <p>Rasio makronutrien harian</p>
            </div>
          </div>
          <DonutChart />
        </div>
      </div>

      {/* ── Bottom Row ── */}
      <div className={styles.bottomRow}>
        {/* Today Meals */}
        <div className={styles.mealsCard}>
          <div className={styles.chartHeader}>
            <div>
              <h3>Riwayat Makan Hari Ini</h3>
              <p>{todayMeals.length} makanan tercatat</p>
            </div>
            <a href="/dashboard/food-analysis" className={styles.addBtn}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
              Tambah
            </a>
          </div>
          <div className={styles.mealsList}>
            {todayMeals.map((meal, i) => (
              <div key={i} className={styles.mealItem}>
                <span className={styles.mealEmoji}>{meal.img}</span>
                <div className={styles.mealInfo}>
                  <span className={styles.mealName}>{meal.name}</span>
                  <span className={styles.mealTime}>{meal.time}</span>
                </div>
                <span className={styles.mealCal}>{meal.cal} kkal</span>
              </div>
            ))}
          </div>
        </div>

        {/* Macro Progress */}
        <div className={styles.macroCard}>
          <div className={styles.chartHeader}>
            <div>
              <h3>Progress Makronutrien</h3>
              <p>Target harian Anda</p>
            </div>
          </div>
          <div className={styles.macroList}>
            {macroData.map((m) => (
              <MacroProgress key={m.name} data={m} />
            ))}
          </div>
        </div>


      </div>
    </div>
  );
}
