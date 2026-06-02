"use client";

import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import styles from "./ahli-gizi.module.css";

export default function AhliGiziLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<{ full_name?: string; spesialisasi?: string } | null>(null);

  useEffect(() => {
    const role = localStorage.getItem("jimamet_role");
    const storedUser = localStorage.getItem("jimamet_user");
    if (role !== "ahli_gizi") {
      router.replace("/login");
      return;
    }
    if (storedUser) {
      try { setUser(JSON.parse(storedUser)); } catch { }
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("jimamet_token");
    localStorage.removeItem("jimamet_user");
    localStorage.removeItem("jimamet_role");
    router.replace("/login");
  };

  const navItems = [
    { href: "/ahli-gizi", icon: "dashboard", label: "Ringkasan" },
    { href: "/ahli-gizi/pasien", icon: "medical_services", label: "Konsultasi Pasien" },
  ];

  return (
    <div className={styles.shell}>
      {/* ── Sidebar ── */}
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <span className={styles.brandIcon}>
            <Image src="/jimamet_logo.webp" alt="Jimamet Logo" width={48} height={48} style={{ objectFit: 'contain' }} />
          </span>
          <div>
            <div className={styles.brandName}>Jimamet Expert</div>
            <div className={styles.brandSub}>Portal Ahli Gizi</div>
          </div>
        </div>

        <nav className={styles.nav}>
          {navItems.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`${styles.navItem} ${active ? styles.navActive : ""}`}
              >
                <span className="material-symbols-outlined">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.agProfile}>
            <div className={styles.agAvatar}>
              {user?.full_name?.[0]?.toUpperCase() ?? "A"}
            </div>
            <div>
              <div className={styles.agName}>{user?.full_name ?? "Ahli Gizi"}</div>
              <div className={styles.agSpec}>{user?.spesialisasi ?? "Gizi Klinik"}</div>
            </div>
          </div>
          <button className={styles.logoutBtn} onClick={handleLogout}>
            <span className="material-symbols-outlined">logout</span>
            Keluar
          </button>
        </div>
      </aside>

      {/* ── Main Content ── */}
      <main className={styles.main}>{children}</main>
    </div>
  );
}
