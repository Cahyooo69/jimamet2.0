"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import styles from "./ahli-gizi.module.css";


export default function AhliGiziDashboard() {
  const [user, setUser] = useState<{ full_name?: string; spesialisasi?: string } | null>(null);
  const [today, setToday] = useState("");

  useEffect(() => {
    const stored = localStorage.getItem("jimamet_user");
    if (stored) {
      try { setUser(JSON.parse(stored)); } catch {}
    }
    setToday(new Date().toLocaleDateString("id-ID", {
      weekday: "long", day: "numeric", month: "long", year: "numeric"
    }));
  }, []);

  let firstName = "Ahli Gizi";
  if (user?.full_name) {
    const parts = user.full_name.split(" ");
    firstName = parts.length > 1 && parts[0].toLowerCase().includes("dr") ? `${parts[0]} ${parts[1]}` : parts[0];
  }

  return (
    <div>
      {/* ── Page Header ── */}
      <div className={styles.pageHeader}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <h1>Halo, {firstName}! 👋</h1>
            <p>Selamat datang di Portal Ahli Gizi Jimamet.</p>
          </div>
          <span style={{
            fontSize: 13, color: "var(--ag-outline)", background: "var(--ag-surface-low)",
            padding: "6px 14px", borderRadius: "var(--ag-radius)", border: "1px solid var(--ag-border)"
          }}>
            📅 {today}
          </span>
        </div>
      </div>

      {/* ── Quick Actions ── */}
      <div style={{ marginBottom: 24 }}>
        <div className={styles.sectionHeader}>
          <h2>Aksi Cepat</h2>
        </div>
        <div className={styles.actionGrid}>
          <Link href="/ahli-gizi/pasien" className={styles.actionCard}>
            <div className={styles.actionIcon}>
              <span className="material-symbols-outlined">medical_services</span>
            </div>
            <div>
              <div className={styles.actionTitle}>Konsultasi Pasien</div>
              <div className={styles.actionDesc}>Tinjau permintaan konsultasi dan balas pesan pasien.</div>
            </div>
          </Link>
          <div className={styles.actionCard} style={{ cursor: "default", opacity: 0.7 }}>
            <div className={styles.actionIcon}>
              <span className="material-symbols-outlined">analytics</span>
            </div>
            <div>
              <div className={styles.actionTitle}>Laporan Klinikal (Segera)</div>
              <div className={styles.actionDesc}>Lihat statistik dan tren konsumsi pasien.</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
