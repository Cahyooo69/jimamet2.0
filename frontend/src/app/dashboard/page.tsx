"use client";

import { useState, useEffect } from "react";
import styles from "./dashboard.module.css";
import { apiDashboardSummary } from "@/lib/api";

export default function DashboardPage() {
  const [greeting, setGreeting] = useState("Selamat Pagi");
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<{ full_name?: string; username?: string } | null>(null);

  const [summary, setSummary] = useState({
    total_calories: 0,
    target_calories: 2000,
    total_protein: 0,
    total_carbs: 0,
    total_fat: 0,
    meals: [] as any[],
  });

  useEffect(() => {
    const stored = localStorage.getItem("jimamet_user");
    if (stored) {
      try { setUser(JSON.parse(stored)); } catch {}
    }

    const h = new Date().getHours();
    if (h >= 5 && h < 11) setGreeting("Selamat Pagi");
    else if (h >= 11 && h < 15) setGreeting("Selamat Siang");
    else if (h >= 15 && h < 18) setGreeting("Selamat Sore");
    else setGreeting("Selamat Malam");

    apiDashboardSummary().then((res) => {
      if (res.ok) {
        setSummary(res.data);
      }
      setLoading(false);
    });
  }, []);

  // Format Time Helper
  const formatTime = (iso: string) => {
    return new Date(iso).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });
  };

  // Target nutrisi harian (standar umum — bisa diambil dari profil user di iterasi berikutnya)
  const DEFAULT_CALORIE_TARGET = 2000;
  const DEFAULT_PROTEIN_TARGET = 60;  // gram
  const DEFAULT_CARB_TARGET = 200;    // gram
  const DEFAULT_FAT_TARGET = 60;      // gram
  const DEFAULT_FIBER_TARGET = 25;    // gram

  const target = summary.target_calories || DEFAULT_CALORIE_TARGET;
  const cals = summary.total_calories || 0;
  const calPct = Math.min((cals / target) * 100, 100);

  const prot = Number(summary.total_protein) || 0;
  const protPct = Math.min((prot / DEFAULT_PROTEIN_TARGET) * 100, 100);

  const carbs = Number(summary.total_carbs) || 0;
  const fat = Number(summary.total_fat) || 0;

  const macroData = [
    { name: "Protein", value: prot, target: DEFAULT_PROTEIN_TARGET, color: "#2e7d32", unit: "g" },
    { name: "Karbo", value: carbs, target: DEFAULT_CARB_TARGET, color: "#4caf50", unit: "g" },
    { name: "Lemak", value: fat, target: DEFAULT_FAT_TARGET, color: "#a5d6a7", unit: "g" },
    { name: "Serat", value: 0, target: DEFAULT_FIBER_TARGET, color: "#1b6d24", unit: "g" },
  ];

  const totalMacros = prot + carbs + fat || 1;
  const nutrientDonut = [
    { name: "Protein", pct: Math.round((prot / totalMacros) * 100), color: "#2e7d32" },
    { name: "Karbohidrat", pct: Math.round((carbs / totalMacros) * 100), color: "#4caf50" },
    { name: "Lemak", pct: Math.round((fat / totalMacros) * 100), color: "#a5d6a7" },
  ];

  // Chart kalori: hanya hari ini dengan data real
  const calorieData = [{ day: "Hari Ini", value: cals, target }];

  function DonutChart() {
    const size = 160, cx = size / 2, cy = size / 2, r = 60;
    const circumference = 2 * Math.PI * r;
    let offset = 0;

    return (
      <div className={styles.donutWrapper}>
        <svg viewBox={`0 0 ${size} ${size}`} width={size} height={size}>
          {nutrientDonut.map((seg) => {
            const dash = (seg.pct / 100) * circumference;
            const el = (
              <circle
                key={seg.name} cx={cx} cy={cy} r={r} fill="none"
                stroke={seg.color} strokeWidth="20"
                strokeDasharray={`${dash - 4} ${circumference - dash + 4}`}
                strokeDashoffset={-offset}
                transform={`rotate(-90 ${cx} ${cy})`}
                className={styles.donutSegment}
              />
            );
            offset += dash;
            return el;
          })}
          <text x={cx} y={cy - 6} textAnchor="middle" fill="var(--on-surface)" fontSize="22" fontWeight="700" fontFamily="Plus Jakarta Sans">
            {cals}
          </text>
          <text x={cx} y={cy + 12} textAnchor="middle" fill="var(--on-surface-variant)" fontSize="11" fontFamily="Inter">
            / {target} kkal
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

  function BarChart() {
    const maxVal = 2500, barW = 36, gap = 20, chartH = 180;
    const chartW = calorieData.length * (barW + gap);

    return (
      <svg viewBox={`0 0 ${chartW + 40} ${chartH + 40}`} className={styles.chartSvg}>
        {[0, 0.25, 0.5, 0.75, 1].map((pct) => (
          <g key={pct}>
            <line x1="36" y1={chartH - chartH * pct + 12} x2={chartW + 36} y2={chartH - chartH * pct + 12} stroke="var(--surface-container-high)" strokeWidth="1" />
            <text x="0" y={chartH - chartH * pct + 16} fill="var(--outline)" fontSize="10">{Math.round(maxVal * pct)}</text>
          </g>
        ))}
        <line x1="36" y1={chartH - (target / maxVal) * chartH + 12} x2={chartW + 36} y2={chartH - (target / maxVal) * chartH + 12} stroke="#ff9800" strokeWidth="1.5" strokeDasharray="6 4" />
        {calorieData.map((d, i) => {
          const h = (d.value / maxVal) * chartH;
          const x = 40 + i * (barW + gap);
          return (
            <g key={d.day}>
              <rect x={x} y={chartH - h + 12} width={barW} height={h} rx="6" ry="6" fill={d.value > d.target ? "url(#barOver)" : "url(#barNormal)"} className={styles.bar} />
              <text x={x + barW / 2} y={chartH + 30} textAnchor="middle" fill="var(--on-surface-variant)" fontSize="12">{d.day}</text>
              <text x={x + barW / 2} y={chartH - h + 6} textAnchor="middle" fill="var(--on-surface-variant)" fontSize="10">{d.value}</text>
            </g>
          );
        })}
        <defs>
          <linearGradient id="barNormal" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#4caf50" /><stop offset="100%" stopColor="#2e7d32" /></linearGradient>
          <linearGradient id="barOver" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#ff9800" /><stop offset="100%" stopColor="#f57c00" /></linearGradient>
        </defs>
      </svg>
    );
  }

  if (loading) return <div style={{ padding: 40, textAlign: "center" }}>Memuat Dashboard...</div>;

  return (
    <div className={styles.dashboard}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.greeting}>{greeting}, {user?.username || user?.full_name?.split(" ")[0] || "User"}! 👋</h1>
          <p className={styles.subtitle}>Pantau asupan nutrisi harian Anda untuk mencapai target kesehatan.</p>
        </div>
        <div className={styles.headerActions}>
          <span className={styles.dateBadge}>
            📅 {new Date().toLocaleDateString("id-ID", { weekday: "long", day: "numeric", month: "long", year: "numeric" })}
          </span>
        </div>
      </div>

      <div className={styles.statCards}>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: "rgba(46,125,50,0.08)", color: "#2e7d32" }}>🔥</div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Kalori Hari Ini</span>
            <span className={styles.statValue}>{cals}</span>
            <span className={styles.statMeta}>/ {target} kkal</span>
          </div>
          <div className={styles.statProgress}><div style={{ width: `${calPct}%`, background: "linear-gradient(90deg, #2e7d32, #4caf50)" }} /></div>
        </div>
        <div className={styles.statCard}>
          <div className={styles.statIcon} style={{ background: "rgba(76,175,80,0.08)", color: "#4caf50" }}>🥩</div>
          <div className={styles.statInfo}>
            <span className={styles.statLabel}>Protein</span>
            <span className={styles.statValue}>{prot}g</span>
            <span className={styles.statMeta}>/ {DEFAULT_PROTEIN_TARGET}g target</span>
          </div>
          <div className={styles.statProgress}><div style={{ width: `${protPct}%`, background: "linear-gradient(90deg, #4caf50, #a5d6a7)" }} /></div>
        </div>
      </div>

      <div className={styles.chartsRow}>
        <div className={styles.chartCard}>
          <div className={styles.chartHeader}>
            <div><h3>Tren Kalori 7 Hari Terakhir</h3></div>
          </div>
          <BarChart />
        </div>
        <div className={styles.chartCard}>
          <div className={styles.chartHeader}>
            <div><h3>Distribusi Nutrisi Hari Ini</h3></div>
          </div>
          <DonutChart />
        </div>
      </div>

      <div className={styles.bottomRow}>
        <div className={styles.mealsCard}>
          <div className={styles.chartHeader}>
            <div>
              <h3>Riwayat Makan Hari Ini</h3>
              <p>{summary.meals.length} makanan tercatat</p>
            </div>
            <a href="/dashboard/food-analysis" className={styles.addBtn}>+ Tambah</a>
          </div>
          <div className={styles.mealsList}>
            {summary.meals.length === 0 ? (
              <p style={{ textAlign: "center", padding: 20, color: "gray" }}>Belum ada makanan tercatat hari ini.</p>
            ) : (
              summary.meals.map((meal, i) => (
                <div key={i} className={styles.mealItem}>
                  <span className={styles.mealEmoji}>🍽️</span>
                  <div className={styles.mealInfo}>
                    <span className={styles.mealName}>{meal.nama_makanan}</span>
                    <span className={styles.mealTime}>{formatTime(meal.tanggal)}</span>
                  </div>
                  <span className={styles.mealCal}>{meal.kalori} kkal</span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className={styles.macroCard}>
          <div className={styles.chartHeader}>
            <div><h3>Progress Makronutrien</h3></div>
          </div>
          <div className={styles.macroList}>
            {macroData.map((m) => (
              <div key={m.name} className={styles.macroItem}>
                <div className={styles.macroTop}>
                  <span className={styles.macroName}>{m.name}</span>
                  <span className={styles.macroValue}>{m.value}{m.unit} <span className={styles.macroTarget}>/ {m.target}{m.unit}</span></span>
                </div>
                <div className={styles.macroTrack}>
                  <div className={styles.macroFill} style={{ width: `${Math.min((m.value/m.target)*100, 100)}%`, background: m.color }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
