"use client";

import { useState, useEffect } from "react";
import styles from "./history.module.css";
import { apiListFoodRecords } from "@/lib/api";

interface MealRecord {
  id: string;
  date: string;
  time: string;
  name: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  emoji: string;
}


function formatDate(isoStr: string): string {
  const d = new Date(isoStr);
  const months = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
  return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;
}

function formatTime(isoStr: string): string {
  const d = new Date(isoStr);
  return d.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });
}

function isToday(dateStr: string): boolean {
  const today = new Date();
  const months = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
  const todayFormatted = `${today.getDate()} ${months[today.getMonth()]} ${today.getFullYear()}`;
  return dateStr === todayFormatted;
}

function isThisWeek(dateStr: string): boolean {
  const parts = dateStr.split(" ");
  const months = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"];
  const d = new Date(parseInt(parts[2]), months.indexOf(parts[1]), parseInt(parts[0]));
  const now = new Date();
  const diff = now.getTime() - d.getTime();
  return diff >= 0 && diff <= 7 * 24 * 60 * 60 * 1000;
}

export default function HistoryPage() {
  const [filter, setFilter] = useState<"all" | "today" | "week">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [allData, setAllData] = useState<MealRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiListFoodRecords().then(({ ok, data }) => {
      if (ok && Array.isArray(data) && data.length > 0) {
        const mapped: MealRecord[] = data.map((r: Record<string, unknown>) => ({
          id: (r.id_analysis as string) || (r.id as string) || Math.random().toString(),
          date: formatDate((r.tanggal as string) || (r.recorded_at as string)),
          time: formatTime((r.tanggal as string) || (r.recorded_at as string)),
          name: (r.nama_makanan as string) || (r.food_name as string) || "Makanan",
          calories: (r.kalori as number) || (r.calories as number) || 0,
          protein: (r.protein as number) || 0,
          carbs: (r.karbohidrat as number) || (r.carbs as number) || 0,
          fat: (r.lemak as number) || (r.fat as number) || 0,
          emoji: "🍽️",
        }));
        setAllData(mapped);
      }
      setLoading(false);
    });
  }, []);

  const filteredData = allData.filter((item) => {
    const itemName = item.name || "";
    const matchesSearch = itemName.toLowerCase().includes(searchQuery.toLowerCase());
    if (filter === "today") return matchesSearch && isToday(item.date);
    if (filter === "week") return matchesSearch && isThisWeek(item.date);
    return matchesSearch;
  });

  const grouped = filteredData.reduce<Record<string, MealRecord[]>>((acc, item) => {
    if (!acc[item.date]) acc[item.date] = [];
    acc[item.date].push(item);
    return acc;
  }, {});

  const totalCal = filteredData.reduce((s, i) => s + i.calories, 0);
  const totalProtein = filteredData.reduce((s, i) => s + i.protein, 0);
  const totalCarbs = filteredData.reduce((s, i) => s + i.carbs, 0);
  const totalFat = filteredData.reduce((s, i) => s + i.fat, 0);

  return (
    <div className={styles.page}>
      {/* Header */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Histori Konsumsi</h1>
          <p className={styles.subtitle}>Lihat riwayat asupan makanan Anda.</p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className={styles.summaryCards}>
        <div className={styles.summaryCard}>
          <span className={styles.summaryLabel}>Total Kalori</span>
          <span className={styles.summaryValue}>{totalCal.toLocaleString()}</span>
          <span className={styles.summaryUnit}>kkal</span>
        </div>
        <div className={styles.summaryCard}>
          <span className={styles.summaryLabel}>Protein</span>
          <span className={styles.summaryValue}>{totalProtein}</span>
          <span className={styles.summaryUnit}>gram</span>
        </div>
        <div className={styles.summaryCard}>
          <span className={styles.summaryLabel}>Karbohidrat</span>
          <span className={styles.summaryValue}>{totalCarbs}</span>
          <span className={styles.summaryUnit}>gram</span>
        </div>
        <div className={styles.summaryCard}>
          <span className={styles.summaryLabel}>Lemak</span>
          <span className={styles.summaryValue}>{totalFat}</span>
          <span className={styles.summaryUnit}>gram</span>
        </div>
      </div>

      {/* Filters */}
      <div className={styles.toolbar}>
        <div className={styles.filterTabs}>
          {(["all", "today", "week"] as const).map((f) => (
            <button
              key={f}
              className={`${styles.filterTab} ${filter === f ? styles.filterTabActive : ""}`}
              onClick={() => setFilter(f)}
            >
              {f === "all" ? "Semua" : f === "today" ? "Hari Ini" : "7 Hari"}
            </button>
          ))}
        </div>
        <div className={styles.searchWrapper}>
          <svg className={styles.searchIcon} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="11" cy="11" r="8" />
            <line x1="21" y1="21" x2="16.65" y2="16.65" />
          </svg>
          <input
            type="text"
            placeholder="Cari makanan..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={styles.searchInput}
          />
        </div>
      </div>

      {/* History List */}
      <div className={styles.historyList}>
        {Object.entries(grouped).map(([date, meals]) => (
          <div key={date} className={styles.dateGroup}>
            <div className={styles.dateHeader}>
              <span className={styles.dateBadge}>{date}</span>
              <span className={styles.dateCal}>
                {meals.reduce((s, m) => s + m.calories, 0).toLocaleString()} kkal
              </span>
            </div>
            <div className={styles.mealsTable}>
              {meals.map((meal) => (
                <div key={meal.id} className={styles.mealRow}>
                  <span className={styles.mealEmoji}>{meal.emoji}</span>
                  <div className={styles.mealInfo}>
                    <span className={styles.mealName}>{meal.name}</span>
                    <span className={styles.mealTime}>{meal.time}</span>
                  </div>
                  <div className={styles.mealNutrients}>
                    <span className={styles.nutrientPill} style={{ background: "rgba(46,125,50,0.08)", color: "#2e7d32" }}>P: {meal.protein}g</span>
                    <span className={styles.nutrientPill} style={{ background: "rgba(76,175,80,0.08)", color: "#4caf50" }}>K: {meal.carbs}g</span>
                    <span className={styles.nutrientPill} style={{ background: "rgba(255,152,0,0.08)", color: "#f57c00" }}>L: {meal.fat}g</span>
                  </div>
                  <span className={styles.mealCal}>{meal.calories} kkal</span>
                </div>
              ))}
            </div>
          </div>
        ))}
        {filteredData.length === 0 && (
          <div className={styles.emptyState}>
            <p>Tidak ada data yang cocok.</p>
          </div>
        )}
      </div>
    </div>
  );
}
