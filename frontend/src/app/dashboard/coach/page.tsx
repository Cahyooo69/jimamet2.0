"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import styles from "./coach.module.css";
import {
  apiListCoachSessions,
  apiGetCoachSession,
  apiCreateCoachSession,
  apiDeleteCoachSession,
  apiSendCoachMessage,
  apiCreateConsultation,
  apiSendChat,
  apiListConsultations,
  apiListChat,
} from "@/lib/api";

interface CoachSession {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface ChatMessage {
  id: string;
  session_id: string;
  sender: "user" | "ai";
  message: string;
  needs_consultation: boolean;
  sent_at: string;
}

interface Consultation {
  id: string;
  user_id: string;
  coach_message: string;
  status: "pending" | "completed" | "cancelled";
  created_at: string;
}

interface ConsultationChat {
  id: string;
  consultation_id: string;
  sender: "user" | "nutritionist";
  message: string;
  sent_at: string;
}

function formatTime(iso: string) {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

function formatRelativeTime(iso: string) {
  try {
    const d = new Date(iso);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMins = Math.round(diffMs / 60000);
    const diffHours = Math.round(diffMins / 60);
    const diffDays = Math.round(diffHours / 24);

    if (diffMins < 60) return `${diffMins || 1}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return "Yesterday";
    return `${diffDays}d ago`;
  } catch {
    return "";
  }
}

const quickReplies = [
  "Analisis nutrisi hari ini",
  "Rekomendasi makan malam",
  "Tips diet sehat",
  "Saya punya keluhan kesehatan",
];

const statusLabels: Record<string, { label: string; color: string }> = {
  pending: { label: "Menunggu", color: "#f59e0b" },
  completed: { label: "Selesai", color: "#22c55e" },
  cancelled: { label: "Dibatalkan", color: "#9ca3af" },
};

type ViewMode = "coach" | "consultation";

export default function NutriCoachPage() {
  // Coach AI state
  const [sessions, setSessions] = useState<CoachSession[]>([]);
  const [activeSession, setActiveSession] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  // Consultation state
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [consultationsLoaded, setConsultationsLoaded] = useState(false);
  const [activeConsultation, setActiveConsultation] = useState<string | null>(null);
  const [consultationChats, setConsultationChats] = useState<ConsultationChat[]>([]);
  const [consultationInput, setConsultationInput] = useState("");
  const [consultationSending, setConsultationSending] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Shared state
  const [viewMode, setViewMode] = useState<ViewMode>("coach");
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [konsultasiStatus, setKonsultasiStatus] = useState<Record<string, "idle" | "loading" | "sent" | "error">>({});
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping, consultationChats]);

  // ── Coach Sessions ──
  const loadSessions = async () => {
    setIsLoading(true);
    try {
      const { ok, data } = await apiListCoachSessions();
      if (ok && Array.isArray(data)) {
        setSessions(data);
        if (data.length > 0 && !activeSession) {
          selectSession(data[0].id);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const selectSession = async (sessionId: string) => {
    setViewMode("coach");
    setActiveSession(sessionId);
    setActiveConsultation(null);
    setSidebarOpen(false);
    try {
      const { ok, data } = await apiGetCoachSession(sessionId);
      if (ok) {
        setMessages(data.messages || []);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleNewSession = async () => {
    try {
      const { ok, data } = await apiCreateCoachSession("New Consultation");
      if (ok && data) {
        setSessions([data, ...sessions]);
        setActiveSession(data.id);
        setActiveConsultation(null);
        setViewMode("coach");
        setMessages([]);
        setSidebarOpen(false);
      } else {
        alert(data?.error || "Gagal membuat sesi baru. Periksa backend.");
      }
    } catch (e) {
      console.error(e);
      alert("Terjadi kesalahan jaringan.");
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    if (!confirm("Hapus sesi konsultasi ini?")) return;
    try {
      const { ok } = await apiDeleteCoachSession(sessionId);
      if (ok) {
        setSessions(sessions.filter((s) => s.id !== sessionId));
        if (activeSession === sessionId) {
          setActiveSession(null);
          setMessages([]);
        }
      }
    } catch (e) {
      console.error(e);
    }
  };

  // ── Coach Chat ──
  const sendMessage = async (text: string) => {
    if (!text.trim() || !activeSession) return;

    const userMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      session_id: activeSession,
      sender: "user",
      message: text,
      needs_consultation: false,
      sent_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      const res = await apiSendCoachMessage(activeSession, text);
      if (res.ok) {
        const aiMsg: ChatMessage = {
          id: `temp-ai-${Date.now()}`,
          session_id: activeSession,
          sender: "ai",
          message: res.data.reply,
          needs_consultation: res.data.needs_consultation,
          sent_at: new Date().toISOString(),
        };
        setMessages((prev) => [...prev, aiMsg]);

        if (res.data.session) {
          setSessions((prev) =>
            prev.map(s => s.id === activeSession ? res.data.session : s)
          );
        }
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: `temp-err-${Date.now()}`,
            session_id: activeSession,
            sender: "ai",
            message: "Maaf, sistem AI sedang mengalami kendala. Silakan coba beberapa saat lagi.",
            needs_consultation: false,
            sent_at: new Date().toISOString(),
          },
        ]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleKirimKonsultasi = async (msgId: string, contextMsgText: string) => {
    setKonsultasiStatus(prev => ({ ...prev, [msgId]: "loading" }));
    const pesanCoachbot = `Pasien membutuhkan konsultasi terkait riwayat percakapan. Sistem NutriCoach AI menyarankan penanganan langsung dari ahli gizi untuk kondisi ini. Konteks: "${contextMsgText.substring(0, 50)}..."`;

    try {
      const { ok, data } = await apiCreateConsultation(pesanCoachbot);
      if (ok && data?.id) {
        await apiSendChat(data.id, "Halo Ahli Gizi, saya diarahkan oleh NutriCoach AI untuk berkonsultasi.", "user");
        setKonsultasiStatus(prev => ({ ...prev, [msgId]: "sent" }));
        // Refresh consultations list
        await loadConsultations();
        alert("Permintaan konsultasi berhasil dikirim! Klik tab 'Konsultasi Ahli Gizi' di sidebar untuk melihat balasan.");
      } else {
        throw new Error("Failed to create consultation");
      }
    } catch (e) {
      setKonsultasiStatus(prev => ({ ...prev, [msgId]: "error" }));
      alert("Gagal mengirim permintaan konsultasi.");
    }
  };

  // ── Consultations (lazy load — hanya saat user butuh) ──
  const loadConsultations = async () => {
    try {
      const { ok, data } = await apiListConsultations();
      if (ok && Array.isArray(data)) {
        setConsultations(data);
        setConsultationsLoaded(true);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleShowConsultations = async () => {
    if (!consultationsLoaded) {
      await loadConsultations();
    }
  };

  const selectConsultation = async (consultationId: string) => {
    setViewMode("consultation");
    setActiveConsultation(consultationId);
    setActiveSession(null);
    setSidebarOpen(false);
    await loadConsultationChat(consultationId);
  };

  const loadConsultationChat = async (consultationId: string) => {
    try {
      const { ok, data } = await apiListChat(consultationId);
      if (ok && Array.isArray(data)) {
        setConsultationChats(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Refresh: manual button — tidak pakai polling
  const handleRefreshChat = async () => {
    if (!activeConsultation || refreshing) return;
    setRefreshing(true);
    await loadConsultationChat(activeConsultation);
    setRefreshing(false);
  };

  const handleSendConsultationChat = async (e: FormEvent) => {
    e.preventDefault();
    if (!consultationInput.trim() || !activeConsultation || consultationSending) return;

    setConsultationSending(true);
    const text = consultationInput.trim();
    setConsultationInput("");

    try {
      const { ok } = await apiSendChat(activeConsultation, text, "user");
      if (ok) {
        // Refresh chat setelah kirim — satu kali saja
        await loadConsultationChat(activeConsultation);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setConsultationSending(false);
    }
  };

  return (
    <div className={styles.layout}>
      {sidebarOpen && (
        <div className={styles.sidebarOverlay} onClick={() => setSidebarOpen(false)} />
      )}

      {/* Sidebar */}
      <aside className={`${styles.sidebar} ${sidebarOpen ? styles.sidebarOpen : ""}`}>
        <div className={styles.sidebarHeader}>
          <h2>NutriCoach AI</h2>
          <button className={styles.newSessionBtn} onClick={handleNewSession}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            Sesi Baru
          </button>
        </div>
        <div className={styles.sessionList}>
          {sessions.length === 0 ? (
            <div className={styles.emptySidebar}>Belum ada sesi AI</div>
          ) : (
            sessions.map((s) => (
              <div
                key={s.id}
                className={`${styles.sessionItem} ${viewMode === "coach" && activeSession === s.id ? styles.activeSession : ""}`}
                onClick={() => selectSession(s.id)}
              >
                <div className={styles.sessionItemContent}>
                  <div className={styles.sessionTitle}>🤖 {s.title}</div>
                  <div className={styles.sessionTime}>{formatRelativeTime(s.updated_at)}</div>
                </div>
                <button
                  className={styles.deleteSessionBtn}
                  onClick={(e) => handleDeleteSession(e, s.id)}
                  title="Hapus sesi"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>

        {/* Consultation Section — lazy loaded */}
        <div className={styles.sidebarDivider} onClick={handleShowConsultations} style={{ cursor: "pointer" }}>
          <span>🩺 Konsultasi Ahli Gizi {!consultationsLoaded && "(klik untuk muat)"}</span>
        </div>
        {consultationsLoaded && (
          <div className={styles.sessionList}>
            {consultations.length === 0 ? (
              <div className={styles.emptySidebar}>Belum ada konsultasi</div>
            ) : (
              consultations.map((c) => {
                const st = statusLabels[c.status] || statusLabels.pending;
                return (
                  <div
                    key={c.id}
                    className={`${styles.sessionItem} ${viewMode === "consultation" && activeConsultation === c.id ? styles.activeSession : ""}`}
                    onClick={() => selectConsultation(c.id)}
                  >
                    <div className={styles.sessionItemContent}>
                      <div className={styles.sessionTitle}>🩺 Konsultasi</div>
                      <div className={styles.sessionTime}>
                        <span className={styles.statusBadge} style={{ color: st.color }}>● {st.label}</span>
                        {" · "}
                        {formatRelativeTime(c.created_at)}
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        )}
      </aside>

      {/* Main Chat Area */}
      <main className={styles.main}>
        <header className={styles.chatHeader}>
          <button className={styles.menuBtn} onClick={() => setSidebarOpen(true)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>
          {viewMode === "coach" ? (
            <>
              <div className={styles.aiAvatar}>
                <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.5">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
                </svg>
              </div>
              <div className={styles.headerInfo}>
                <h2>NutriCoach AI</h2>
                <span className={styles.onlineStatus}>
                  <span className={styles.onlineDot}></span> Online
                </span>
              </div>
            </>
          ) : (
            <>
              <div className={styles.doctorAvatar}>🩺</div>
              <div className={styles.headerInfo}>
                <h2>Chat Ahli Gizi</h2>
                <span className={styles.onlineStatus}>
                  <span className={styles.onlineDotYellow}></span> Konsultasi
                </span>
              </div>
              <button
                className={styles.refreshBtn}
                onClick={handleRefreshChat}
                disabled={refreshing}
                title="Muat pesan terbaru"
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className={refreshing ? styles.spinning : ""}>
                  <polyline points="23 4 23 10 17 10"></polyline>
                  <polyline points="1 20 1 14 7 14"></polyline>
                  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                </svg>
                {refreshing ? "Memuat..." : "Refresh"}
              </button>
            </>
          )}
        </header>

        <div className={styles.messagesContainer}>
          {/* ── COACH AI VIEW ── */}
          {viewMode === "coach" && (
            <>
              {!activeSession ? (
                <div className={styles.emptyState}>
                  <div className={styles.emptyIcon}>🤖</div>
                  <h3>Selamat Datang di NutriCoach AI</h3>
                  <p>Mulai sesi baru untuk berkonsultasi tentang gizi dan kesehatan Anda.</p>
                  <button className={styles.startBtn} onClick={handleNewSession}>
                    Mulai Sesi Pertama
                  </button>
                </div>
              ) : (
                <>
                  {messages.length === 0 && (
                    <div className={styles.welcomeState}>
                      <p>Halo! 👋 Saya NutriCoach AI. Ada yang bisa saya bantu?</p>
                      <div className={styles.quickReplies}>
                        {quickReplies.map((q) => (
                          <button key={q} className={styles.quickBtn} onClick={() => sendMessage(q)}>
                            {q}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}

                  {messages.map((msg, i) => (
                    <div key={msg.id || i} className={`${styles.msgRow} ${msg.sender === "user" ? styles.msgRowUser : styles.msgRowAi}`}>
                      <div className={`${styles.bubble} ${msg.sender === "user" ? styles.bubbleUser : styles.bubbleAi}`}>
                        <p>{msg.message}</p>
                        <span className={styles.msgTime}>{formatTime(msg.sent_at)}</span>

                        {msg.needs_consultation && konsultasiStatus[msg.id] !== "sent" && (
                          <button
                            onClick={() => handleKirimKonsultasi(msg.id, msg.message)}
                            disabled={konsultasiStatus[msg.id] === "loading"}
                            className={styles.konsultasiBtn}
                          >
                            🩺 {konsultasiStatus[msg.id] === "loading" ? "Mengirim..." : "Hubungi Ahli Gizi Sekarang"}
                          </button>
                        )}
                        {msg.needs_consultation && konsultasiStatus[msg.id] === "sent" && (
                          <div className={styles.konsultasiSent}>✅ Permintaan terkirim — cek sidebar &quot;Konsultasi Ahli Gizi&quot;</div>
                        )}
                      </div>
                    </div>
                  ))}

                  {isTyping && (
                    <div className={`${styles.msgRow} ${styles.msgRowAi}`}>
                      <div className={`${styles.bubble} ${styles.bubbleAi}`}>
                        <div className={styles.typingDots}>
                          <span /><span /><span />
                        </div>
                      </div>
                    </div>
                  )}
                </>
              )}
            </>
          )}

          {/* ── CONSULTATION VIEW ── */}
          {viewMode === "consultation" && (
            <>
              {!activeConsultation ? (
                <div className={styles.emptyState}>
                  <div className={styles.emptyIcon}>🩺</div>
                  <h3>Konsultasi Ahli Gizi</h3>
                  <p>Pilih sesi konsultasi di sidebar untuk melihat percakapan.</p>
                </div>
              ) : (
                <>
                  {consultationChats.length === 0 && (
                    <div className={styles.welcomeState}>
                      <p>Menunggu balasan dari ahli gizi... 🩺</p>
                      <p style={{ fontSize: "0.85rem", color: "#999", marginTop: "0.5rem" }}>
                        Klik tombol &quot;Refresh&quot; di atas untuk melihat pesan terbaru.
                      </p>
                    </div>
                  )}

                  {consultationChats.map((msg, i) => (
                    <div
                      key={msg.id || i}
                      className={`${styles.msgRow} ${msg.sender === "user" ? styles.msgRowUser : styles.msgRowAi}`}
                    >
                      <div
                        className={`${styles.bubble} ${msg.sender === "user" ? styles.bubbleUser : styles.bubbleDoctor}`}
                      >
                        {msg.sender === "nutritionist" && (
                          <div className={styles.senderLabel}>🩺 Ahli Gizi</div>
                        )}
                        <p>{msg.message}</p>
                        <span className={styles.msgTime}>{formatTime(msg.sent_at)}</span>
                      </div>
                    </div>
                  ))}
                </>
              )}
            </>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        {viewMode === "coach" && activeSession && (
          <form onSubmit={handleSubmit} className={styles.inputArea}>
            <input
              type="text"
              placeholder="Ketik pertanyaan tentang gizi..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className={styles.inputField}
              disabled={isTyping}
            />
            <button type="submit" className={styles.sendBtn} disabled={!input.trim() || isTyping}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </form>
        )}

        {viewMode === "consultation" && activeConsultation && (
          <form onSubmit={handleSendConsultationChat} className={styles.inputArea}>
            <input
              type="text"
              placeholder="Balas pesan ahli gizi..."
              value={consultationInput}
              onChange={(e) => setConsultationInput(e.target.value)}
              className={styles.inputField}
              disabled={consultationSending}
            />
            <button type="submit" className={styles.sendBtn} disabled={!consultationInput.trim() || consultationSending}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </form>
        )}
      </main>
    </div>
  );
}
