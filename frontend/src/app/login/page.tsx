"use client";

import { useState, FormEvent, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import styles from "./login.module.css";
import { apiLogin, apiRegister } from "@/lib/api";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = searchParams.get("tab") === "register" ? "register" : "login";
  const [activeTab, setActiveTab] = useState<"login" | "register">(initialTab);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  /* ── Login State ── */
  const [loginData, setLoginData] = useState({ username: "", password: "" });

  /* ── Register State ── */
  const [registerData, setRegisterData] = useState({
    full_name: "",
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
    age: "",
    weight: "",
    height: "",
    activity_level: "moderate",
  });

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      const { ok, data } = await apiLogin(loginData);
      if (ok) {
        // Store role in localStorage for routing
        if (data.role === "ahli_gizi") {
          localStorage.setItem("jimamet_role", "ahli_gizi");
          setSuccess("Login berhasil! Mengalihkan ke Portal Ahli Gizi...");
          setTimeout(() => router.push("/ahli-gizi"), 1000);
        } else {
          localStorage.setItem("jimamet_role", "user");
          setSuccess("Login berhasil! Mengalihkan...");
          setTimeout(() => router.push("/dashboard"), 1000);
        }
      } else {
        setError(data.error || data.detail || (data && JSON.stringify(data)) || "Login gagal. Periksa kredensial Anda.");
      }
    } catch {
      setError("Tidak dapat terhubung ke server.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegister = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    if (registerData.password !== registerData.confirmPassword) {
      setError("Password tidak cocok.");
      setIsLoading(false);
      return;
    }

    if (registerData.password.length < 8) {
      setError("Password minimal 8 karakter.");
      setIsLoading(false);
      return;
    }

    try {
      const { ok, data } = await apiRegister({
        full_name: registerData.full_name,
        email: registerData.email,
        username: registerData.username,
        password: registerData.password,
        age: registerData.age ? parseInt(registerData.age) : undefined,
        weight: registerData.weight ? parseFloat(registerData.weight) : undefined,
        height: registerData.height ? parseFloat(registerData.height) : undefined,
        activity_level: registerData.activity_level,
      });

      if (ok) {
        setSuccess("Registrasi berhasil! Silakan login.");
        setActiveTab("login");
        setLoginData({ username: registerData.username, password: "" });
        setRegisterData({
          full_name: "",
          email: "",
          username: "",
          password: "",
          confirmPassword: "",
          age: "",
          weight: "",
          height: "",
          activity_level: "moderate",
        });
      } else {
        setError(data.error || data.detail || (data && JSON.stringify(data)) || "Registrasi gagal.");
      }
    } catch {
      setError("Tidak dapat terhubung ke server.");
    } finally {
      setIsLoading(false);
    }
  };

  const switchTab = (tab: "login" | "register") => {
    setActiveTab(tab);
    setError("");
    setSuccess("");
  };

  return (
    <div className={styles.page}>
      {/* ── LEFT PANEL — Hero Image ── */}
      <div className={styles.leftPanel}>
        <div className={styles.leftOverlay} />
        <img
          src="/hero-nutrition.png"
          alt="Healthy nutritious food"
          className={styles.leftImage}
        />
        <div className={styles.leftContent}>
          <Link href="/" className={styles.leftLogo}>
            <svg viewBox="0 0 32 32" fill="none" width="32" height="32">
              <circle cx="16" cy="16" r="14" fill="white" fillOpacity="0.2" />
              <circle cx="16" cy="16" r="12" fill="white" fillOpacity="0.3" />
              <path
                d="M16 8c-2 0-4 1-5 3s-1 4.5 0 6.5c1.5 3 5 6.5 5 6.5s3.5-3.5 5-6.5c1-2 1-4.5 0-6.5s-3-3-5-3z"
                fill="white"
                fillOpacity="0.9"
              />
              <path d="M16 10v10" stroke="#2e7d32" strokeWidth="1.2" />
            </svg>
            <span>Jimamet</span>
          </Link>
          <div className={styles.leftText}>
            <h1>Nutrisi Klinis di Ujung Jari Anda</h1>
            <p>
              Platform analisis nutrisi berbasis AI dengan presisi klinis untuk
              pemantauan kesehatan yang lebih baik.
            </p>
          </div>
          <div className={styles.leftStats}>
            <div className={styles.leftStat}>
              <span className={styles.leftStatValue}>98.5%</span>
              <span className={styles.leftStatLabel}>Akurasi AI</span>
            </div>
            <div className={styles.leftStatDivider} />
            <div className={styles.leftStat}>
              <span className={styles.leftStatValue}>500+</span>
              <span className={styles.leftStatLabel}>Jenis Makanan</span>
            </div>
            <div className={styles.leftStatDivider} />
            <div className={styles.leftStat}>
              <span className={styles.leftStatValue}>24/7</span>
              <span className={styles.leftStatLabel}>AI Tersedia</span>
            </div>
          </div>
        </div>
      </div>

      {/* ── RIGHT PANEL — Form ── */}
      <div className={styles.rightPanel}>
        <div className={styles.formContainer}>
          {/* Header */}
          <div className={styles.formHeader}>
            <h2 className={styles.formTitle}>Selamat Datang</h2>
            <p className={styles.formSubtitle}>
              Silakan masuk atau daftar untuk melanjutkan.
            </p>
          </div>

          {/* Tabs */}
          <div className={styles.tabs}>
            <button
              className={`${styles.tab} ${activeTab === "login" ? styles.tabActive : ""}`}
              onClick={() => switchTab("login")}
            >
              Login
            </button>
            <button
              className={`${styles.tab} ${activeTab === "register" ? styles.tabActive : ""}`}
              onClick={() => switchTab("register")}
            >
              Registrasi
            </button>
          </div>

          {/* Messages */}
          {error && (
            <div className={styles.alertError}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="15" y1="9" x2="9" y2="15" />
                <line x1="9" y1="9" x2="15" y2="15" />
              </svg>
              {error}
            </div>
          )}
          {success && (
            <div className={styles.alertSuccess}>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
              </svg>
              {success}
            </div>
          )}

          {/* ── LOGIN FORM ── */}
          {activeTab === "login" && (
            <form onSubmit={handleLogin} className={styles.form}>
              <div className={styles.inputGroup}>
                <label htmlFor="login-username">Username</label>
                <div className={styles.inputWrapper}>
                  <svg className={styles.inputIcon} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                  <input
                    id="login-username"
                    type="text"
                    placeholder="Masukkan username"
                    value={loginData.username}
                    onChange={(e) => setLoginData({ ...loginData, username: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className={styles.inputGroup}>
                <label htmlFor="login-password">Password</label>
                <div className={styles.inputWrapper}>
                  <svg className={styles.inputIcon} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                  </svg>
                  <input
                    id="login-password"
                    type="password"
                    placeholder="Masukkan password"
                    value={loginData.password}
                    onChange={(e) => setLoginData({ ...loginData, password: e.target.value })}
                    required
                  />
                </div>
              </div>

              <button
                type="submit"
                className={styles.submitBtn}
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className={styles.spinner} />
                ) : (
                  <>
                    Masuk
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="5" y1="12" x2="19" y2="12" />
                      <polyline points="12 5 19 12 12 19" />
                    </svg>
                  </>
                )}
              </button>
            </form>
          )}

          {/* ── REGISTER FORM ── */}
          {activeTab === "register" && (
            <form onSubmit={handleRegister} className={styles.form}>
              <div className={styles.inputGroup}>
                <label htmlFor="reg-fullname">Nama Lengkap</label>
                <div className={styles.inputWrapper}>
                  <svg className={styles.inputIcon} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                  <input
                    id="reg-fullname"
                    type="text"
                    placeholder="Nama lengkap Anda"
                    value={registerData.full_name}
                    onChange={(e) => setRegisterData({ ...registerData, full_name: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className={styles.inputGroup}>
                <label htmlFor="reg-email">Email</label>
                <div className={styles.inputWrapper}>
                  <svg className={styles.inputIcon} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                    <polyline points="22,6 12,13 2,6" />
                  </svg>
                  <input
                    id="reg-email"
                    type="email"
                    placeholder="nama@email.com"
                    value={registerData.email}
                    onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className={styles.inputGroup}>
                <label htmlFor="reg-username">Username</label>
                <div className={styles.inputWrapper}>
                  <svg className={styles.inputIcon} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                  <input
                    id="reg-username"
                    type="text"
                    placeholder="Pilih username"
                    value={registerData.username}
                    onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div className={styles.inputRow}>
                <div className={styles.inputGroup}>
                  <label htmlFor="reg-password">Password</label>
                  <div className={styles.inputWrapper}>
                    <svg className={styles.inputIcon} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                    </svg>
                    <input
                      id="reg-password"
                      type="password"
                      placeholder="Min. 8 karakter"
                      value={registerData.password}
                      onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })}
                      required
                      minLength={8}
                    />
                  </div>
                </div>
                <div className={styles.inputGroup}>
                  <label htmlFor="reg-confirm">Konfirmasi</label>
                  <div className={styles.inputWrapper}>
                    <svg className={styles.inputIcon} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                      <polyline points="22 4 12 14.01 9 11.01" />
                    </svg>
                    <input
                      id="reg-confirm"
                      type="password"
                      placeholder="Ulangi password"
                      value={registerData.confirmPassword}
                      onChange={(e) => setRegisterData({ ...registerData, confirmPassword: e.target.value })}
                      required
                      minLength={8}
                    />
                  </div>
                </div>
              </div>

              {/* Data Fisik */}
              <div className={styles.inputRow}>
                <div className={styles.inputGroup}>
                  <label htmlFor="reg-age">Usia (thn)</label>
                  <div className={styles.inputWrapper}>
                    <input
                      id="reg-age"
                      type="number"
                      placeholder="Mis: 25"
                      value={registerData.age}
                      onChange={(e) => setRegisterData({ ...registerData, age: e.target.value })}
                      style={{ paddingLeft: 16 }}
                      required
                    />
                  </div>
                </div>
                <div className={styles.inputGroup}>
                  <label htmlFor="reg-weight">Berat (kg)</label>
                  <div className={styles.inputWrapper}>
                    <input
                      id="reg-weight"
                      type="number"
                      step="0.1"
                      placeholder="Mis: 65"
                      value={registerData.weight}
                      onChange={(e) => setRegisterData({ ...registerData, weight: e.target.value })}
                      style={{ paddingLeft: 16 }}
                      required
                    />
                  </div>
                </div>
                <div className={styles.inputGroup}>
                  <label htmlFor="reg-height">Tinggi (cm)</label>
                  <div className={styles.inputWrapper}>
                    <input
                      id="reg-height"
                      type="number"
                      step="0.1"
                      placeholder="Mis: 170"
                      value={registerData.height}
                      onChange={(e) => setRegisterData({ ...registerData, height: e.target.value })}
                      style={{ paddingLeft: 16 }}
                      required
                    />
                  </div>
                </div>
              </div>

              <div className={styles.inputGroup}>
                <label htmlFor="reg-activity">Tingkat Aktivitas</label>
                <div className={styles.inputWrapper}>
                  <select
                    id="reg-activity"
                    value={registerData.activity_level}
                    onChange={(e) => setRegisterData({ ...registerData, activity_level: e.target.value })}
                    style={{
                      width: "100%",
                      padding: "12px 16px",
                      borderRadius: "12px",
                      border: "1px solid var(--ag-border)",
                      background: "var(--ag-surface)",
                      fontSize: "14px",
                      color: "var(--ag-on-surface)",
                      outline: "none",
                      appearance: "none",
                      cursor: "pointer",
                    }}
                    required
                  >
                    <option value="sedentary">Sangat Jarang Olahraga</option>
                    <option value="light">Jarang Olahraga (1-3 hari/minggu)</option>
                    <option value="moderate">Normal Olahraga (3-5 hari/minggu)</option>
                    <option value="active">Sering Olahraga (6-7 hari/minggu)</option>
                    <option value="very_active">Sangat Sering Olahraga</option>
                  </select>
                  <svg className={styles.inputIcon} style={{ right: 16, left: "auto", color: "var(--ag-outline)", pointerEvents: "none" }} width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="6 9 12 15 18 9" />
                  </svg>
                </div>
              </div>
              <button
                type="submit"
                className={styles.submitBtn}
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className={styles.spinner} />
                ) : (
                  <>
                    Daftar Sekarang
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="5" y1="12" x2="19" y2="12" />
                      <polyline points="12 5 19 12 12 19" />
                    </svg>
                  </>
                )}
              </button>
            </form>
          )}

          {/* Footer Links */}
          <div className={styles.formFooter}>
            <a href="#">Lupa Password?</a>
            <span className={styles.footerDot}>·</span>
            <a href="#">Butuh bantuan?</a>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}
