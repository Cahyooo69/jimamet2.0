"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import styles from "./page.module.css";

/* ───────── Intersection Observer Hook ───────── */
function useInView(threshold = 0.15) {
  const nodeRef = useRef<HTMLDivElement>(null);
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    const el = nodeRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
          obs.unobserve(el);
        }
      },
      { threshold }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [threshold]);

  return { nodeRef, isInView };
}

/* ───────── Animated Counter ───────── */
function Counter({ end, suffix = "", duration = 2000 }: { end: number; suffix?: string; duration?: number }) {
  const [count, setCount] = useState(0);
  const { ref, isInView } = useInView();

  useEffect(() => {
    if (!isInView) return;
    let start = 0;
    const step = end / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start * 10) / 10);
      }
    }, 16);
    return () => clearInterval(timer);
  }, [isInView, end, duration]);

  return <span ref={ref}>{count}{suffix}</span>;
}

/* ───────── Feature Data ───────── */
const features = [
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z" />
        <circle cx="12" cy="13" r="4" />
      </svg>
    ),
    title: "Analisis Gambar AI",
    desc: "Ambil foto makanan Anda dan biarkan AI kami menghitung nutrisinya secara instan. Mengidentifikasi ratusan jenis bahan makanan dengan presisi tinggi.",
    color: "#2e7d32",
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
    title: "Pelacakan Presisi",
    desc: "Pantau kalori, makronutrien, dan serat dengan akurasi standar klinis. Dashboard interaktif untuk visualisasi data nutrisi harian.",
    color: "#4caf50",
  },
  {
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        <path d="M8 10h.01M12 10h.01M16 10h.01" />
      </svg>
    ),
    title: "NutriCoach AI",
    desc: "Konsultasi nutrisi kapan saja dengan asisten AI cerdas yang memahami riwayat kesehatan Anda dan memberikan rekomendasi personal.",
    color: "#1b6d24",
  },
];

const steps = [
  {
    num: "01",
    title: "Foto Makanan",
    desc: "Gunakan kamera smartphone Anda untuk memotret makanan di piring.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
        <circle cx="8.5" cy="8.5" r="1.5" />
        <polyline points="21 15 16 10 5 21" />
      </svg>
    ),
  },
  {
    num: "02",
    title: "Analisis AI",
    desc: "Sistem klinis kami mengidentifikasi komponen makanan secara otomatis.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2a4 4 0 0 1 4 4c0 1.95-1.4 3.58-3.25 3.93L12 22" />
        <path d="M12 2a4 4 0 0 0-4 4c0 1.95 1.4 3.58 3.25 3.93" />
        <path d="M8.56 13a8 8 0 0 0-2.3 3.5" />
        <path d="M15.44 13a8 8 0 0 1 2.3 3.5" />
      </svg>
    ),
  },
  {
    num: "03",
    title: "Lihat Laporan",
    desc: "Dapatkan rincian nutrisi akurat langsung di dashboard Anda.",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
        <polyline points="10 9 9 9 8 9" />
      </svg>
    ),
  },
];

const stats = [
  { value: 98.5, suffix: "%", label: "Akurasi Analisis" },
  { value: 500, suffix: "+", label: "Jenis Makanan" },
  { value: 10, suffix: "rb+", label: "Pengguna Aktif" },
  { value: 24, suffix: "/7", label: "AI Tersedia" },
];

/* ═══════════════════════════════════════════════════
   MAIN COMPONENT
   ═══════════════════════════════════════════════════ */
export default function LandingPage() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const featuresSection = useInView(0.1);
  const stepsSection = useInView(0.1);
  const statsSection = useInView(0.1);
  const ctaSection = useInView(0.1);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className={styles.page}>
      {/* ── NAVBAR ── */}
      <header className={`${styles.navbar} ${scrolled ? styles.navScrolled : ""}`}>
        <div className={`${styles.navInner} container`}>
          <a href="#" className={styles.logo}>
            <div className={styles.logoIcon}>
              <svg viewBox="0 0 32 32" fill="none">
                <circle cx="16" cy="16" r="14" fill="#2e7d32" />
                <path d="M16 8c-2 0-4 1-5 3s-1 4.5 0 6.5c1.5 3 5 6.5 5 6.5s3.5-3.5 5-6.5c1-2 1-4.5 0-6.5s-3-3-5-3z" fill="#a3f69c" />
                <path d="M16 10v10" stroke="#2e7d32" strokeWidth="1.2" />
                <path d="M13 14c1.5 0.5 3 0.5 3 0" stroke="#2e7d32" strokeWidth="1" fill="none" />
                <path d="M19 13c-1.5 0.5-3 0.5-3 0" stroke="#2e7d32" strokeWidth="1" fill="none" />
              </svg>
            </div>
            <span className={styles.logoText}>Jimamet</span>
          </a>

          <nav className={`${styles.navLinks} ${mobileMenuOpen ? styles.navOpen : ""}`}>
            <a href="#features" onClick={() => setMobileMenuOpen(false)}>Fitur</a>
            <a href="#how-it-works" onClick={() => setMobileMenuOpen(false)}>Cara Kerja</a>
            <a href="#stats" onClick={() => setMobileMenuOpen(false)}>Data Klinis</a>
            <a href="/login" className={styles.navCta}>Masuk</a>
          </nav>

          <button
            className={styles.hamburger}
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            aria-label="Toggle menu"
          >
            <span className={mobileMenuOpen ? styles.hamburgerOpen : ""} />
          </button>
        </div>
      </header>

      {/* ── HERO ── */}
      <section className={styles.hero}>
        <div className={styles.heroBg}>
          <div className={styles.heroOrb1} />
          <div className={styles.heroOrb2} />
          <div className={styles.heroOrb3} />
        </div>
        <div className={`${styles.heroInner} container`}>
          <div className={styles.heroContent}>
            <span className={`${styles.heroBadge} animate-fade-up`}>
              <span className={styles.heroBadgeDot} />
              Clinical Nutrition AI Platform
            </span>
            <h1 className={`display-lg animate-fade-up delay-100`}>
              Nutrisi Klinis<br />
              di <span className={styles.heroGradient}>Ujung Jari</span> Anda
            </h1>
            <p className={`body-lg animate-fade-up delay-200`} style={{ color: "var(--on-surface-variant)", maxWidth: 540 }}>
              Transformasikan kesehatan Anda dengan analisis nutrisi berbasis AI yang presisi.
              Jimamet membantu Anda memantau asupan makanan secara klinis dan profesional.
            </p>
            <div className={`${styles.heroActions} animate-fade-up delay-300`}>
              <a href="/register" className={styles.btnPrimary}>
                Mulai Gratis
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </a>
              <a href="#how-it-works" className={styles.btnOutline}>
                Lihat Demo
              </a>
            </div>
          </div>
          <div className={`${styles.heroImage} animate-slide-right delay-300`}>
            <div className={styles.heroImageWrapper}>
              <Image
                src="/hero-nutrition.png"
                alt="Healthy nutritious food for medical nutrition analysis"
                width={600}
                height={450}
                priority
                className={styles.heroImg}
              />
              <div className={styles.heroFloatingCard}>
                <div className={styles.floatingCardIcon}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="#2e7d32" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
                  </svg>
                </div>
                <div>
                  <div className={styles.floatingCardLabel}>Kalori Terdeteksi</div>
                  <div className={styles.floatingCardValue}>324 kkal</div>
                </div>
              </div>
              <div className={styles.heroFloatingCard2}>
                <div className={styles.floatingCardIcon}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="#4caf50" strokeWidth="2">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" strokeLinecap="round" strokeLinejoin="round" />
                    <polyline points="22 4 12 14.01 9 11.01" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
                <div>
                  <div className={styles.floatingCardLabel}>Protein</div>
                  <div className={styles.floatingCardValue}>28g ✓</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className={styles.heroWave}>
          <svg viewBox="0 0 1440 100" preserveAspectRatio="none">
            <path d="M0,40 C360,100 720,0 1080,60 C1260,90 1380,50 1440,40 L1440,100 L0,100 Z" fill="var(--surface)" />
          </svg>
        </div>
      </section>

      {/* ── FEATURES ── */}
      <section id="features" className={styles.features} ref={featuresSection.nodeRef}>
        <div className="container">
          <div className={styles.sectionHeader}>
            <span className={`label-md ${styles.sectionTag}`}>FITUR UNGGULAN</span>
            <h2 className="headline-lg">
              Fitur Unggulan <span className={styles.textGreen}>Jimamet</span>
            </h2>
            <p className="body-lg" style={{ color: "var(--on-surface-variant)", maxWidth: 600 }}>
              Teknologi kelas medis yang didesain untuk kemudahan penggunaan sehari-hari,
              memberikan wawasan nutrisi mendalam tanpa kerumitan.
            </p>
          </div>

          <div className={styles.featuresGrid}>
            {features.map((f, i) => (
              <div
                key={f.title}
                className={`${styles.featureCard} ${featuresSection.isInView ? "animate-fade-up" : ""}`}
                style={{ animationDelay: `${(i + 1) * 150}ms`, opacity: featuresSection.isInView ? undefined : 0 }}
              >
                <div className={styles.featureIcon} style={{ background: `${f.color}14`, color: f.color }}>
                  {f.icon}
                </div>
                <h3 className="title-lg">{f.title}</h3>
                <p className="body-md" style={{ color: "var(--on-surface-variant)" }}>{f.desc}</p>
                <a href="#" className={styles.featureLink}>
                  Pelajari lebih lanjut
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="5" y1="12" x2="19" y2="12" />
                    <polyline points="12 5 19 12 12 19" />
                  </svg>
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section id="how-it-works" className={styles.howItWorks} ref={stepsSection.nodeRef}>
        <div className="container">
          <div className={styles.sectionHeader}>
            <span className={`label-md ${styles.sectionTag}`}>CARA KERJA</span>
            <h2 className="headline-lg">
              Cara Kerja yang <span className={styles.textGreen}>Sederhana</span>
            </h2>
            <p className="body-lg" style={{ color: "var(--on-surface-variant)", maxWidth: 560 }}>
              Tiga langkah mudah menuju pemantauan nutrisi yang lebih baik.
            </p>
          </div>

          <div className={styles.stepsGrid}>
            {steps.map((s, i) => (
              <div
                key={s.num}
                className={`${styles.stepCard} ${stepsSection.isInView ? "animate-fade-up" : ""}`}
                style={{ animationDelay: `${(i + 1) * 200}ms`, opacity: stepsSection.isInView ? undefined : 0 }}
              >
                <div className={styles.stepNum}>{s.num}</div>
                <div className={styles.stepIcon}>{s.icon}</div>
                <h3 className="title-lg">{s.title}</h3>
                <p className="body-md" style={{ color: "var(--on-surface-variant)" }}>{s.desc}</p>
                {i < steps.length - 1 && <div className={styles.stepConnector} />}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── STATS ── */}
      <section id="stats" className={styles.stats} ref={statsSection.nodeRef}>
        <div className="container">
          <div className={styles.statsGrid}>
            {stats.map((s, i) => (
              <div
                key={s.label}
                className={`${styles.statCard} ${statsSection.isInView ? "animate-scale-in" : ""}`}
                style={{ animationDelay: `${(i + 1) * 100}ms`, opacity: statsSection.isInView ? undefined : 0 }}
              >
                <div className={styles.statValue}>
                  <Counter end={s.value} suffix={s.suffix} />
                </div>
                <div className={styles.statLabel}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ── */}
      <section className={styles.cta} ref={ctaSection.nodeRef}>
        <div className="container">
          <div className={`${styles.ctaCard} ${ctaSection.isInView ? "animate-scale-in" : ""}`} style={{ opacity: ctaSection.isInView ? undefined : 0 }}>
            <div className={styles.ctaOrb} />
            <h2 className="headline-lg" style={{ color: "white", position: "relative" }}>
              Mulai Perjalanan Sehat Anda Hari Ini
            </h2>
            <p className="body-lg" style={{ color: "rgba(255,255,255,0.85)", maxWidth: 560, position: "relative" }}>
              Bergabunglah dengan ribuan tenaga medis dan pasien yang telah
              mempercayakan manajemen nutrisi mereka pada Jimamet.
            </p>
            <div className={styles.ctaActions} style={{ position: "relative" }}>
              <a href="/register" className={styles.btnWhite}>
                Daftar Sekarang — Gratis
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ── FOOTER ── */}
      <footer className={styles.footer}>
        <div className="container">
          <div className={styles.footerTop}>
            <div className={styles.footerBrand}>
              <div className={styles.logo}>
                <div className={styles.logoIcon}>
                  <svg viewBox="0 0 32 32" fill="none">
                    <circle cx="16" cy="16" r="14" fill="#2e7d32" />
                    <path d="M16 8c-2 0-4 1-5 3s-1 4.5 0 6.5c1.5 3 5 6.5 5 6.5s3.5-3.5 5-6.5c1-2 1-4.5 0-6.5s-3-3-5-3z" fill="#a3f69c" />
                    <path d="M16 10v10" stroke="#2e7d32" strokeWidth="1.2" />
                  </svg>
                </div>
                <span className={styles.logoText}>Jimamet</span>
              </div>
              <p className="body-sm" style={{ color: "rgba(255, 255, 255, 0.9)", maxWidth: 320, marginTop: 12 }}>
                Clinical precision in every byte. Platform nutrisi medis berbasis AI
                untuk pemantauan kesehatan yang lebih baik.
              </p>
            </div>

            <div className={styles.footerLinks}>
              <div className={styles.footerCol}>
                <h4 className="label-md" style={{ marginBottom: 16 }}>Platform</h4>
                <a href="#features">Fitur</a>
                <a href="#how-it-works">Cara Kerja</a>
                <a href="#stats">Data Klinis</a>
                <a href="#">Pricing</a>
              </div>
              <div className={styles.footerCol}>
                <h4 className="label-md" style={{ marginBottom: 16 }}>Legal</h4>
                <a href="#">Privacy Policy</a>
                <a href="#">Terms of Service</a>
                <a href="#">HIPAA Compliance</a>
              </div>
              <div className={styles.footerCol}>
                <h4 className="label-md" style={{ marginBottom: 16 }}>Support</h4>
                <a href="#">Contact Support</a>
                <a href="#">Research Papers</a>
                <a href="#">Documentation</a>
              </div>
            </div>
          </div>

          <div className={styles.footerBottom}>
            <p className="body-sm" style={{ color: "var(--outline)" }}>
              © 2024 Jimamet Medical Nutrition. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
