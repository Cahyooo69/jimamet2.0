"use client";

import { useState, useEffect, useCallback, useRef, FormEvent } from "react";
import styles from "../ahli-gizi.module.css";
import { apiListKonsultasi, apiUpdateKonsultasi, apiListChat, apiSendChat, apiDeleteChat, apiDeleteKonsultasi } from "@/lib/api";

interface ChatMsg {
  id_chat: string;
  pengirim: "user" | "ahli_gizi";
  pesan: string;
  tanggal: string;
}

interface Konsultasi {
  id_konsultasi: string;
  id_user: string;
  nama_pasien: string;
  email_pasien: string;
  pesan_coachbot: string;
  status: "menunggu" | "selesai" | "dibatalkan";
  catatan_ahli_gizi: string;
  tanggal: string;
}

function formatDate(iso: string) {
  if (!iso) return "—";
  return new Date(iso).toLocaleDateString("id-ID", {
    day: "numeric", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

const statusStyle = {
  menunggu:   { bg: "#fff3cd", color: "#856404", label: "Menunggu" },
  selesai:    { bg: "rgba(76,175,80,0.12)", color: "#2e7d32", label: "Selesai" },
  dibatalkan: { bg: "#f5f5f5", color: "#707a6c", label: "Dibatalkan" },
};

export default function KonsultasiPage() {
  const [items, setItems] = useState<Konsultasi[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<"semua" | "menunggu" | "selesai">("semua");
  const [selected, setSelected] = useState<Konsultasi | null>(null);
  const [catatan, setCatatan] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  // Live Chat state
  const [chatMsgs, setChatMsgs] = useState<ChatMsg[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatSending, setChatSending] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const pollChat = useCallback(async (kId: string) => {
    const { ok, data } = await apiListChat(kId);
    if (ok && Array.isArray(data)) {
      setChatMsgs(data);
    }
  }, []);

  // Set up polling for chat messages when a consultation is selected
  useEffect(() => {
    if (selected && selected.status === "menunggu") {
      pollChat(selected.id_konsultasi);
      pollRef.current = setInterval(() => pollChat(selected.id_konsultasi), 5000);
    } else {
      setChatMsgs([]);
    }
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [selected, pollChat]);

  // Scroll to bottom when messages change
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMsgs]);

  const fetchData = useCallback(async () => {
    setLoading(true);
    const { ok, data } = await apiListKonsultasi();
    if (ok && Array.isArray(data)) {
      setItems(data);
    } else {
      setError("Gagal memuat data konsultasi.");
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  const handleOpenDetail = (item: Konsultasi) => {
    setSelected(item);
    setCatatan(item.catatan_ahli_gizi || "");
    setChatInput("");
  };

  const handleSendChat = async (e: FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || !selected || chatSending) return;
    
    setChatSending(true);
    const text = chatInput.trim();
    setChatInput(""); // Clear input immediately for better UX
    
    const { ok } = await apiSendChat(selected.id_konsultasi, text, "ahli_gizi");
    if (ok) {
      await pollChat(selected.id_konsultasi);
    }
    setChatSending(false);
  };

  const handleDeleteChat = async (chatId: string) => {
    if (!confirm("Apakah Anda yakin ingin menghapus pesan ini?")) return;
    
    const { ok } = await apiDeleteChat(chatId);
    if (ok && selected) {
      await pollChat(selected.id_konsultasi);
    } else {
      alert("Gagal menghapus pesan chat.");
    }
  };

  const handleUpdate = async (status: "selesai" | "dibatalkan") => {
    if (!selected) return;
    setSaving(true);
    const { ok } = await apiUpdateKonsultasi(selected.id_konsultasi, {
      status,
      catatan_ahli_gizi: catatan,
    });
    if (ok) {
      setItems((prev) =>
        prev.map((i) =>
          i.id_konsultasi === selected.id_konsultasi
            ? { ...i, status, catatan_ahli_gizi: catatan }
            : i
        )
      );
      setSelected(null);
    }
    setSaving(false);
  };

  const handleDeleteKonsultasi = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Mencegah membuka detail saat tombol hapus diklik
    if (!confirm("Apakah Anda yakin ingin menghapus data konsultasi ini beserta seluruh chatnya?")) return;
    
    setLoading(true);
    const { ok } = await apiDeleteKonsultasi(id);
    if (ok) {
      setItems((prev) => prev.filter((i) => i.id_konsultasi !== id));
      if (selected?.id_konsultasi === id) {
        setSelected(null);
      }
    } else {
      alert("Gagal menghapus konsultasi.");
    }
    setLoading(false);
  };

  const displayed = items.filter((i) =>
    filter === "semua" ? true : i.status === filter
  );

  const countMenunggu = items.filter((i) => i.status === "menunggu").length;
  const countSelesai  = items.filter((i) => i.status === "selesai").length;

  return (
    <div>
      {/* ── Header ── */}
      <div className={styles.pageHeader}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <h1>Konsultasi Pasien</h1>
            <p>Daftar pasien yang diarahkan CoachBot untuk berkonsultasi dengan Anda.</p>
          </div>
          <button
            onClick={fetchData}
            className={styles.btnSecondary}
            style={{ display: "flex", alignItems: "center", gap: 6 }}
          >
            <span className="material-symbols-outlined" style={{ fontSize: 18 }}>refresh</span>
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div style={{ background: "#ffdad6", color: "#ba1a1a", padding: "12px 16px", borderRadius: 8, marginBottom: 16, fontSize: 14 }}>
          {error}
        </div>
      )}

      {/* ── Stat mini ── */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 16, marginBottom: 20 }}>
        {[
          { label: "Total Masuk", count: items.length, color: "#0d631b" },
          { label: "Menunggu",    count: countMenunggu, color: "#f57c00" },
          { label: "Selesai",     count: countSelesai,  color: "#2e7d32" },
        ].map(({ label, count, color }) => (
          <div key={label} className={styles.statCard}>
            <div className={styles.statLabel}>{label}</div>
            <div style={{ fontSize: 32, fontWeight: 700, color, fontFamily: "Plus Jakarta Sans", lineHeight: 1 }}>{count}</div>
          </div>
        ))}
      </div>

      {/* ── Filter tabs ── */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        {(["semua", "menunggu", "selesai"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              padding: "7px 16px", borderRadius: 8, fontSize: 13, fontWeight: 600, cursor: "pointer",
              border: filter === f ? "2px solid var(--ag-primary-dark)" : "1px solid var(--ag-border)",
              background: filter === f ? "rgba(46,125,50,0.08)" : "#fff",
              color: filter === f ? "var(--ag-primary-dark)" : "var(--ag-on-variant)",
            }}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
      </div>

      {/* ── List ── */}
      {loading ? (
        <div className={styles.loading}>
          <span className="material-symbols-outlined" style={{ fontSize: 32, marginRight: 10 }}>hourglass_top</span>
          Memuat data konsultasi...
        </div>
      ) : displayed.length === 0 ? (
        <div className={styles.card} style={{ textAlign: "center", padding: 48 }}>
          <span className="material-symbols-outlined" style={{ fontSize: 48, color: "var(--ag-border)", display: "block", marginBottom: 12 }}>
            inbox
          </span>
          <div style={{ color: "var(--ag-outline)", fontSize: 15 }}>
            {filter === "semua"
              ? "Belum ada pasien yang dirujuk CoachBot."
              : `Tidak ada konsultasi berstatus "${filter}".`}
          </div>
        </div>
      ) : (
        <div className={styles.card}>
          <div className={styles.sectionHeader} style={{ marginBottom: 12 }}>
            <h2>Daftar Konsultasi ({displayed.length})</h2>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 0 }}>
            {displayed.map((item) => {
              const s = statusStyle[item.status];
              return (
                <div
                  key={item.id_konsultasi}
                  onClick={() => handleOpenDetail(item)}
                  style={{
                    display: "flex", alignItems: "flex-start", gap: 16,
                    padding: "16px 0", borderBottom: "1px solid var(--ag-border)",
                    cursor: "pointer", transition: "background 0.1s",
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = "var(--ag-surface-low)")}
                  onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                >
                  {/* Avatar */}
                  <div style={{
                    width: 42, height: 42, borderRadius: "50%", flexShrink: 0,
                    background: "rgba(46,125,50,0.12)", display: "flex",
                    alignItems: "center", justifyContent: "center",
                    fontSize: 18, fontWeight: 700, color: "var(--ag-primary-dark)",
                    fontFamily: "Plus Jakarta Sans",
                  }}>
                    {item.nama_pasien?.[0]?.toUpperCase() ?? "?"}
                  </div>

                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 4 }}>
                      <span style={{ fontWeight: 600, fontSize: 14, color: "var(--ag-on-surface)" }}>
                        {item.nama_pasien}
                      </span>
                      <span style={{ fontSize: 12, color: "var(--ag-outline)" }}>
                        {formatDate(item.tanggal)}
                      </span>
                    </div>
                    <div style={{ fontSize: 13, color: "var(--ag-on-variant)", marginBottom: 6, lineHeight: 1.5,
                      overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      🤖 {item.pesan_coachbot}
                    </div>
                    <span style={{ background: s.bg, color: s.color, padding: "2px 10px", borderRadius: 999, fontSize: 11, fontWeight: 600 }}>
                      {s.label}
                    </span>
                  </div>

                  <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
                    <button
                      onClick={(e) => handleDeleteKonsultasi(item.id_konsultasi, e)}
                      title="Hapus Konsultasi"
                      style={{
                        background: "transparent", border: "none", color: "#d32f2f", cursor: "pointer",
                        padding: 8, display: "flex", alignItems: "center", justifyContent: "center",
                        borderRadius: "50%", transition: "background 0.2s"
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(211,47,47,0.1)")}
                      onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: 20 }}>delete</span>
                    </button>
                    <span className="material-symbols-outlined" style={{ fontSize: 20, color: "var(--ag-outline)" }}>
                      chevron_right
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Detail Modal ── */}
      {selected && (
        <div
          style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.45)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}
          onClick={() => setSelected(null)}
        >
          <div
            style={{ background: "#fff", borderRadius: 16, padding: 32, width: 560, maxWidth: "90vw", boxShadow: "0 20px 60px rgba(0,0,0,0.15)", maxHeight: "85vh", overflowY: "auto" }}
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal header */}
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
              <div>
                <h3 style={{ fontFamily: "Plus Jakarta Sans", fontSize: 18, fontWeight: 700, color: "var(--ag-on-surface)", margin: "0 0 4px" }}>
                  Detail Konsultasi
                </h3>
                <p style={{ fontSize: 13, color: "var(--ag-outline)", margin: 0 }}>
                  {selected.nama_pasien} · {selected.email_pasien}
                </p>
              </div>
              <span style={{ background: statusStyle[selected.status].bg, color: statusStyle[selected.status].color, padding: "3px 12px", borderRadius: 999, fontSize: 12, fontWeight: 700 }}>
                {statusStyle[selected.status].label}
              </span>
            </div>

            {/* Pesan CoachBot */}
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 11, fontWeight: 700, color: "var(--ag-outline)", letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: 8 }}>
                Pesan dari CoachBot
              </div>
              <div style={{ background: "rgba(46,125,50,0.06)", border: "1px solid rgba(46,125,50,0.2)", borderRadius: 10, padding: 14, fontSize: 14, color: "var(--ag-on-surface)", lineHeight: 1.7 }}>
                🤖 {selected.pesan_coachbot}
              </div>
            </div>

            {/* Waktu */}
            <div style={{ fontSize: 12, color: "var(--ag-outline)", marginBottom: 16 }}>
              📅 Dikirim: {formatDate(selected.tanggal)}
            </div>

            {/* Chat Ahli Gizi */}
            {selected.status === "menunggu" ? (
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "var(--ag-outline)", letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: 8 }}>
                  Live Chat dengan Pasien
                </div>
                <div style={{
                  border: "1px solid var(--ag-border)",
                  borderRadius: 8,
                  display: "flex",
                  flexDirection: "column",
                  maxHeight: 300,
                  overflow: "hidden"
                }}>
                  {/* Daftar pesan */}
                  <div style={{
                    flex: 1, overflowY: "auto", padding: 12, background: "#fafafa",
                    display: "flex", flexDirection: "column", gap: 8, maxHeight: 200
                  }}>
                    {chatMsgs.length === 0 ? (
                      <div style={{ textAlign: "center", fontSize: 12, color: "#888", padding: 20 }}>
                        Belum ada pesan chat.
                      </div>
                    ) : (
                      chatMsgs.map((m) => (
                        <div key={m.id_chat} style={{
                          display: "flex", flexDirection: "column",
                          alignItems: m.pengirim === "ahli_gizi" ? "flex-end" : "flex-start",
                          position: "relative"
                        }}>
                          <div style={{
                            display: "flex", alignItems: "center", gap: 6,
                            flexDirection: m.pengirim === "ahli_gizi" ? "row-reverse" : "row"
                          }}>
                            <div style={{
                              maxWidth: "100%", padding: "8px 12px",
                              borderRadius: m.pengirim === "ahli_gizi" ? "14px 14px 2px 14px" : "14px 14px 14px 2px",
                              background: m.pengirim === "ahli_gizi" ? "#2e7d32" : "#fff",
                              color: m.pengirim === "ahli_gizi" ? "#fff" : "#1a1c1c",
                              border: m.pengirim === "user" ? "1px solid #eee" : "none",
                              fontSize: 13, lineHeight: 1.5, boxShadow: "0 1px 2px rgba(0,0,0,0.05)"
                            }}>
                              {m.pengirim === "user" && (
                                <div style={{ fontSize: 10, fontWeight: 700, color: "#666", marginBottom: 3 }}>
                                  👤 Pasien
                                </div>
                              )}
                              {m.pesan}
                            </div>
                            
                            {/* Tombol Hapus (ikon trash) */}
                            <button
                              onClick={() => handleDeleteChat(m.id_chat)}
                              title="Hapus pesan"
                              style={{
                                background: "transparent", border: "none", color: "#d32f2f", cursor: "pointer",
                                padding: 4, display: "flex", alignItems: "center", justifyContent: "center",
                                opacity: 0.6, transition: "opacity 0.2s"
                              }}
                              onMouseEnter={(e) => (e.currentTarget.style.opacity = "1")}
                              onMouseLeave={(e) => (e.currentTarget.style.opacity = "0.6")}
                            >
                              <span className="material-symbols-outlined" style={{ fontSize: 16 }}>delete</span>
                            </button>
                          </div>
                          
                          <span style={{ fontSize: 10, color: "#888", marginTop: 2 }}>{formatDate(m.tanggal).split(' ')[1]}</span>
                        </div>
                      ))
                    )}
                    <div ref={chatEndRef} />
                  </div>
                  
                  {/* Input Chat Ahli Gizi */}
                  <form onSubmit={handleSendChat} style={{
                    display: "flex", gap: 8, padding: "8px 12px", background: "#fff", borderTop: "1px solid var(--ag-border)"
                  }}>
                    <input
                      type="text"
                      placeholder="Balas pesan pasien..."
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      disabled={chatSending}
                      style={{
                        flex: 1, padding: "8px 12px", fontSize: 13, border: "1px solid var(--ag-border)",
                        borderRadius: 20, outline: "none", fontFamily: "inherit"
                      }}
                    />
                    <button
                      type="submit"
                      disabled={!chatInput.trim() || chatSending}
                      style={{
                        padding: "0 16px", borderRadius: 20, border: "none",
                        background: chatInput.trim() ? "#2e7d32" : "#ccc",
                        color: "#fff", cursor: chatInput.trim() ? "pointer" : "default",
                        fontSize: 13, fontWeight: 600, transition: "background 0.2s"
                      }}
                    >
                      Kirim
                    </button>
                  </form>
                </div>
              </div>
            ) : selected.catatan_ahli_gizi ? (
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "var(--ag-outline)", letterSpacing: "0.05em", textTransform: "uppercase", marginBottom: 8 }}>
                  Catatan Ahli Gizi
                </div>
                <div style={{ background: "var(--ag-surface-low)", borderRadius: 8, padding: 12, fontSize: 14, color: "var(--ag-on-surface)", lineHeight: 1.6 }}>
                  {selected.catatan_ahli_gizi}
                </div>
              </div>
            ) : null}

            {/* Actions */}
            <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
              <button className={styles.btnSecondary} onClick={() => setSelected(null)} disabled={saving}>Tutup</button>
              {selected.status === "menunggu" && (
                <>
                  <button className={styles.btnReject} onClick={() => handleUpdate("dibatalkan")} disabled={saving}>
                    Batalkan
                  </button>
                  <button className={styles.btnPrimary} onClick={() => handleUpdate("selesai")} disabled={saving}>
                    {saving ? "Menyimpan..." : "✓ Tandai Selesai"}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
