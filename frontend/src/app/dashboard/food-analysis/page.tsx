"use client";

import { useState, useRef, useCallback } from "react";
import styles from "./food-analysis.module.css";
import { apiCreateFoodRecord } from "@/lib/api";

interface NutrientResult {
  name: string;
  value: number;
  unit: string;
  pct: number;
  color: string;
}

interface AnalysisResult {
  foodName: string;
  confidence: number;
  calories: number;
  portion: string;
  nutrients: NutrientResult[];
  tags: string[];
  recommendation: string;
}


export default function FoodAnalysisPage() {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [fileName, setFileName] = useState("");
  const [isAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const [saveStatus, setSaveStatus] = useState<"" | "saving" | "saved">("");

  const handleFile = useCallback((file: File) => {
    if (!file.type.startsWith("image/")) return;
    setFileName(file.name);
    const reader = new FileReader();
    reader.onload = (e) => {
      setSelectedImage(e.target?.result as string);
      setResult(null);
    };
    reader.readAsDataURL(file);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragActive(false);
      if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
    },
    [handleFile]
  );

  const analyzeImage = () => {
    if (!selectedImage) return;
    // Fitur analisis AI belum terhubung ke backend.
    // Set result ke null agar UI menampilkan empty state yang jujur.
    setResult(null);
    alert("Fitur analisis AI sedang dalam pengembangan. Silakan input data nutrisi secara manual melalui Riwayat.");
  };

  const resetAll = () => {
    setSelectedImage(null);
    setFileName("");
    setResult(null);
    setSaveStatus("");
  };

  const saveToHistory = async () => {
    if (!result) return;
    setSaveStatus("saving");
    const { ok } = await apiCreateFoodRecord({
      food_name: result.foodName,
      calories: result.calories,
      protein: result.nutrients.find((n) => n.name === "Protein")?.value || 0,
      carbs: result.nutrients.find((n) => n.name === "Karbohidrat")?.value || 0,
      fat: result.nutrients.find((n) => n.name === "Lemak")?.value || 0,
      fiber: result.nutrients.find((n) => n.name === "Serat")?.value || 0,
      sugar: result.nutrients.find((n) => n.name === "Gula")?.value || 0,
      sodium: result.nutrients.find((n) => n.name === "Sodium")?.value || 0,
      portion: result.portion,
      emoji: "🍽️",
      confidence: result.confidence,
      tags: result.tags,
      recommendation: result.recommendation,
    });
    setSaveStatus(ok ? "saved" : "");
  };

  return (
    <div className={styles.page}>
      {/* ── Header ── */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Analisis Makanan</h1>
          <p className={styles.subtitle}>
            Upload atau foto makanan Anda untuk mendapatkan analisis nutrisi AI secara instan.
          </p>
        </div>
      </div>

      <div className={styles.content}>
        {/* ── LEFT: Upload Area ── */}
        <div className={styles.uploadSection}>
          {!selectedImage ? (
            /* Drop Zone */
            <div
              className={`${styles.dropZone} ${dragActive ? styles.dropZoneActive : ""}`}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className={styles.dropIcon}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>
              <h3>Drag & Drop Foto Makanan</h3>
              <p>atau klik untuk memilih file</p>
              <span className={styles.dropFormats}>JPG, PNG, WEBP — Maks 10MB</span>
            </div>
          ) : (
            /* Preview */
            <div className={styles.previewCard}>
              <div className={styles.previewImageWrapper}>
                <img src={selectedImage} alt="Food preview" className={styles.previewImage} />
                {isAnalyzing && (
                  <div className={styles.scanOverlay}>
                    <div className={styles.scanLine} />
                    <span className={styles.scanText}>Menganalisis...</span>
                  </div>
                )}
              </div>
              <div className={styles.previewInfo}>
                <span className={styles.previewName}>{fileName}</span>
                <div className={styles.previewActions}>
                  {!result && !isAnalyzing && (
                    <button onClick={analyzeImage} className={styles.analyzeBtn}>
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                      </svg>
                      Analisis Nutrisi
                    </button>
                  )}
                  <button onClick={resetAll} className={styles.resetBtn}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="1 4 1 10 7 10" />
                      <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
                    </svg>
                    Foto Lain
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Buttons Row */}
          {!selectedImage && (
            <div className={styles.uploadButtons}>
              <button className={styles.uploadBtn} onClick={() => fileInputRef.current?.click()}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
                  <circle cx="8.5" cy="8.5" r="1.5" />
                  <polyline points="21 15 16 10 5 21" />
                </svg>
                Pilih dari Galeri
              </button>
              <button className={styles.cameraBtn} onClick={() => cameraInputRef.current?.click()}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
                  <circle cx="12" cy="13" r="4" />
                </svg>
                Ambil Foto
              </button>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            hidden
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            hidden
            onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
          />
        </div>

        {/* ── RIGHT: Results ── */}
        <div className={styles.resultSection}>
          {!result && !isAnalyzing && (
            <div className={styles.emptyResult}>
              <div className={styles.emptyIcon}>
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                </svg>
              </div>
              <h3>Hasil Analisis</h3>
              <p>Upload foto makanan lalu klik &quot;Analisis Nutrisi&quot; untuk melihat komposisi nutrisi secara detail.</p>
            </div>
          )}

          {isAnalyzing && (
            <div className={styles.analyzingState}>
              <div className={styles.analyzingSpinner}>
                <div className={styles.spinRing} />
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" width="28" height="28" className={styles.spinIcon}>
                  <path d="M12 2a4 4 0 0 1 4 4c0 1.95-1.4 3.58-3.25 3.93L12 22M12 2a4 4 0 0 0-4 4c0 1.95 1.4 3.58 3.25 3.93" />
                </svg>
              </div>
              <h3>AI sedang menganalisis...</h3>
              <p>Mengidentifikasi makanan dan menghitung nutrisi</p>
              <div className={styles.analyzingSteps}>
                <span className={styles.stepDone}>✓ Deteksi gambar</span>
                <span className={styles.stepDone}>✓ Identifikasi makanan</span>
                <span className={styles.stepActive}>⟳ Kalkulasi nutrisi...</span>
              </div>
            </div>
          )}

          {result && (
            <div className={styles.resultCard}>
              {/* Food Header */}
              <div className={styles.resultHeader}>
                <div>
                  <h2 className={styles.foodName}>{result.foodName}</h2>
                  <span className={styles.portion}>{result.portion}</span>
                </div>
                <div className={styles.confidenceBadge}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                    <polyline points="22 4 12 14.01 9 11.01" />
                  </svg>
                  {result.confidence}% akurat
                </div>
              </div>

              {/* Calorie Ring */}
              <div className={styles.calorieSection}>
                <div className={styles.calorieRing}>
                  <svg viewBox="0 0 120 120" width="120" height="120">
                    <circle cx="60" cy="60" r="50" fill="none" stroke="var(--surface-container)" strokeWidth="10" />
                    <circle
                      cx="60" cy="60" r="50" fill="none"
                      stroke="url(#calGrad)" strokeWidth="10"
                      strokeDasharray={`${(result.calories / 800) * 314} 314`}
                      strokeLinecap="round"
                      transform="rotate(-90 60 60)"
                    />
                    <defs>
                      <linearGradient id="calGrad" x1="0" y1="0" x2="1" y2="1">
                        <stop offset="0%" stopColor="#2e7d32" />
                        <stop offset="100%" stopColor="#4caf50" />
                      </linearGradient>
                    </defs>
                    <text x="60" y="56" textAnchor="middle" fontSize="24" fontWeight="700" fill="var(--on-surface)" fontFamily="Plus Jakarta Sans">{result.calories}</text>
                    <text x="60" y="72" textAnchor="middle" fontSize="11" fill="var(--outline)" fontFamily="Inter">kkal</text>
                  </svg>
                </div>
                <div className={styles.tags}>
                  {result.tags.map((tag) => (
                    <span
                      key={tag}
                      className={`${styles.tag} ${tag.includes("Perhatian") ? styles.tagWarn : ""}`}
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>

              {/* Nutrients */}
              <div className={styles.nutrientsList}>
                <h4>Detail Nutrisi</h4>
                {result.nutrients.map((n) => (
                  <div key={n.name} className={styles.nutrientRow}>
                    <span className={styles.nutrientName}>{n.name}</span>
                    <div className={styles.nutrientBar}>
                      <div style={{ width: `${n.pct}%`, background: n.color }} />
                    </div>
                    <span className={styles.nutrientVal}>
                      {n.value}{n.unit}
                    </span>
                  </div>
                ))}
              </div>

              {/* Recommendation */}
              <div className={styles.recoCard}>
                <div className={styles.recoIcon}>💡</div>
                <div>
                  <h4>Rekomendasi NutriCoach</h4>
                  <p>{result.recommendation}</p>
                </div>
              </div>

              {/* Action buttons */}
              <div className={styles.resultActions}>
                <button
                  className={styles.saveBtn}
                  onClick={saveToHistory}
                  disabled={saveStatus !== ""}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z" />
                    <polyline points="17 21 17 13 7 13 7 21" />
                    <polyline points="7 3 7 8 15 8" />
                  </svg>
                  {saveStatus === "saving" ? "Menyimpan..." : saveStatus === "saved" ? "✓ Tersimpan!" : "Simpan ke Riwayat"}
                </button>
                <button onClick={resetAll} className={styles.newBtn}>
                  Analisis Baru
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
