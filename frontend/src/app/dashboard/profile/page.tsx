"use client";

import { useState, useEffect } from "react";
import styles from "./profile.module.css";
import { apiGetProfile, apiUpdateProfile, apiDashboardSummary } from "@/lib/api";

export default function ProfilePage() {
  const [profile, setProfile] = useState({
    fullName: "",
    email: "",
    username: "",
    age: "",
    weight: "",
    height: "",
    gender: "male",
    activityLevel: "moderate",
    goal: "maintain",
  });
  const [todayCalories, setTodayCalories] = useState(0);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([apiGetProfile(), apiDashboardSummary()]).then(([profRes, sumRes]) => {
      if (profRes.ok && profRes.data) {
        setProfile({
          fullName: profRes.data.full_name || "",
          email: profRes.data.email || "",
          username: profRes.data.username || "",
          age: profRes.data.age?.toString() || "",
          weight: profRes.data.weight?.toString() || "",
          height: profRes.data.height?.toString() || "",
          gender: profRes.data.gender || "male",
          activityLevel: profRes.data.activity_level || "moderate",
          goal: profRes.data.goal || "maintain",
        });
      }
      if (sumRes.ok && sumRes.data) {
        setTodayCalories(sumRes.data.total_calories || 0);
      }
      setLoading(false);
    });
  }, []);

  const handleChange = (field: string, value: string) => {
    setProfile((prev) => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  const handleSave = async () => {
    setSaving(true);
    const { ok } = await apiUpdateProfile({
      full_name: profile.fullName,
      age: profile.age ? parseInt(profile.age) : null,
      weight: profile.weight ? parseFloat(profile.weight) : null,
      height: profile.height ? parseFloat(profile.height) : null,
      gender: profile.gender,
      activity_level: profile.activityLevel,
      goal: profile.goal,
    });
    setSaving(false);
    if (ok) {
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    }
  };

  // BMI
  const bmi = profile.weight && profile.height
    ? (parseFloat(profile.weight) / ((parseFloat(profile.height) / 100) ** 2)).toFixed(1)
    : "—";

  const bmiCategory = () => {
    const v = parseFloat(bmi);
    if (isNaN(v)) return { label: "—", color: "#888" };
    if (v < 18.5) return { label: "Kurus", color: "#2196f3" };
    if (v < 25) return { label: "Normal", color: "#2e7d32" };
    if (v < 30) return { label: "Overweight", color: "#ff9800" };
    return { label: "Obesitas", color: "#f44336" };
  };

  // Estimated daily calories
  const estimateCalories = () => {
    const w = parseFloat(profile.weight), h = parseFloat(profile.height), a = parseFloat(profile.age);
    if (!w || !h || !a) return "—";
    let bmr = profile.gender === "male"
      ? 10 * w + 6.25 * h - 5 * a + 5
      : 10 * w + 6.25 * h - 5 * a - 161;
    const factors: Record<string, number> = { sedentary: 1.2, light: 1.375, moderate: 1.55, active: 1.725, veryActive: 1.9 };
    const tdee = bmr * (factors[profile.activityLevel] || 1.55);
    if (profile.goal === "lose") return Math.round(tdee - 400);
    if (profile.goal === "gain") return Math.round(tdee + 400);
    return Math.round(tdee);
  };

  if (loading) {
    return (
      <div className={styles.page}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: "4rem", color: "var(--outline)" }}>
          Memuat profil...
        </div>
      </div>
    );
  }

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Kelola Profil</h1>
          <p className={styles.subtitle}>Atur informasi pribadi dan target kesehatan Anda.</p>
        </div>
      </div>

      <div className={styles.content}>
        {/* LEFT: Form */}
        <div className={styles.formSection}>
          {/* Personal Info */}
          <div className={styles.card}>
            <h3 className={styles.cardTitle}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg>
              Informasi Pribadi
            </h3>
            <div className={styles.fieldGrid}>
              <div className={styles.field}>
                <label>Nama Lengkap</label>
                <input type="text" value={profile.fullName} onChange={(e) => handleChange("fullName", e.target.value)} />
              </div>
              <div className={styles.field}>
                <label>Email</label>
                <input type="email" value={profile.email} onChange={(e) => handleChange("email", e.target.value)} />
              </div>
              <div className={styles.field}>
                <label>Username</label>
                <input type="text" value={profile.username} onChange={(e) => handleChange("username", e.target.value)} />
              </div>
              <div className={styles.field}>
                <label>Usia</label>
                <div className={styles.inputUnit}>
                  <input type="number" value={profile.age} onChange={(e) => handleChange("age", e.target.value)} />
                  <span>tahun</span>
                </div>
              </div>
            </div>
          </div>

          {/* Body Metrics */}
          <div className={styles.card}>
            <h3 className={styles.cardTitle}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /></svg>
              Metrik Tubuh
            </h3>
            <div className={styles.fieldGrid}>
              <div className={styles.field}>
                <label>Berat Badan</label>
                <div className={styles.inputUnit}>
                  <input type="number" value={profile.weight} onChange={(e) => handleChange("weight", e.target.value)} />
                  <span>kg</span>
                </div>
              </div>
              <div className={styles.field}>
                <label>Tinggi Badan</label>
                <div className={styles.inputUnit}>
                  <input type="number" value={profile.height} onChange={(e) => handleChange("height", e.target.value)} />
                  <span>cm</span>
                </div>
              </div>
              <div className={styles.field}>
                <label>Jenis Kelamin</label>
                <select value={profile.gender} onChange={(e) => handleChange("gender", e.target.value)}>
                  <option value="male">Laki-laki</option>
                  <option value="female">Perempuan</option>
                </select>
              </div>
              <div className={styles.field}>
                <label>Tingkat Aktivitas</label>
                <select value={profile.activityLevel} onChange={(e) => handleChange("activityLevel", e.target.value)}>
                  <option value="sedentary">Tidak aktif (duduk terus)</option>
                  <option value="light">Ringan (1-3x olahraga/minggu)</option>
                  <option value="moderate">Sedang (3-5x olahraga/minggu)</option>
                  <option value="active">Aktif (6-7x olahraga/minggu)</option>
                  <option value="veryActive">Sangat Aktif (atlet)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Goal */}
          <div className={styles.card}>
            <h3 className={styles.cardTitle}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" /></svg>
              Target Kesehatan
            </h3>
            <div className={styles.goalOptions}>
              {[
                { value: "lose", label: "Turunkan Berat", icon: "📉", desc: "Defisit 400 kkal/hari" },
                { value: "maintain", label: "Pertahankan", icon: "⚖️", desc: "Kalori seimbang" },
                { value: "gain", label: "Naikkan Berat", icon: "📈", desc: "Surplus 400 kkal/hari" },
              ].map((g) => (
                <button
                  key={g.value}
                  className={`${styles.goalCard} ${profile.goal === g.value ? styles.goalCardActive : ""}`}
                  onClick={() => handleChange("goal", g.value)}
                >
                  <span className={styles.goalIcon}>{g.icon}</span>
                  <span className={styles.goalLabel}>{g.label}</span>
                  <span className={styles.goalDesc}>{g.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Save */}
          <div className={styles.saveBar}>
            <button onClick={handleSave} className={styles.saveBtn} disabled={saving}>
              {saving ? "Menyimpan..." : saved ? "✓ Tersimpan!" : "Simpan Perubahan"}
            </button>
          </div>
        </div>

        {/* RIGHT: Summary */}
        <div className={styles.sidebar}>
          {/* Avatar Card */}
          <div className={styles.avatarCard}>
            <div className={styles.avatarBig}>
              <span>{profile.fullName.charAt(0).toUpperCase()}</span>
            </div>
            <h3>{profile.fullName}</h3>
            <p>@{profile.username}</p>
          </div>

          {/* BMI Card */}
          <div className={styles.bmiCard}>
            <h4>Indeks Massa Tubuh (BMI)</h4>
            <div className={styles.bmiValue} style={{ color: bmiCategory().color }}>
              {bmi}
            </div>
            <span className={styles.bmiLabel} style={{ background: `${bmiCategory().color}15`, color: bmiCategory().color }}>
              {bmiCategory().label}
            </span>
            <div className={styles.bmiScale}>
              <div className={styles.bmiBar}>
                <div className={styles.bmiIndicator} style={{ left: `${Math.min(Math.max(((parseFloat(bmi) - 15) / 25) * 100, 0), 100)}%` }} />
              </div>
              <div className={styles.bmiLabels}>
                <span>15</span><span>18.5</span><span>25</span><span>30</span><span>40</span>
              </div>
            </div>
          </div>

          {/* Calorie Target */}
          <div className={styles.calorieCard}>
            <h4>Target Kalori Harian</h4>
            <div className={styles.calorieValue}>
              <span style={{ fontSize: "0.7em", color: "var(--on-surface-variant)" }}>{todayCalories} / </span>
              {estimateCalories()}
            </div>
            <span className={styles.calorieUnit}>kkal / hari</span>
            <p className={styles.calorieNote}>
              Berdasarkan metrik tubuh, tingkat aktivitas, dan target kesehatan Anda.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
