"use client";

import { useState, useRef, useEffect, FormEvent, useCallback } from "react";
import styles from "./nutricoach-popup.module.css";
import { apiCreateKonsultasi, apiListChat, apiSendChat } from "@/lib/api";

interface ChatMessage {
  role: "ai" | "user";
  text: string;
  time: string;
  showKonsultasiBtn?: boolean;
}

interface ChatMsg {
  id_chat: string;
  pengirim: "user" | "ahli_gizi";
  pesan: string;
  tanggal: string;
}

const quickReplies = [
  "Analisis nutrisi hari ini",
  "Rekomendasi makan malam",
  "Tips diet sehat",
];

function getTimeStr() {
  return new Date().toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });
}

const KONSULTASI_TRIGGERS = [
  "diabetes", "hipertensi", "tekanan darah", "kolesterol",
  "hamil", "menyusui", "obesitas", "kurus sekali", "penyakit",
  "tidak nafsu makan", "alergi", "ginjal", "jantung",
  "dokter", "ahli gizi", "konsultasi", "gangguan makan",
];

function shouldSuggestKonsultasi(text: string): boolean {
  const lower = text.toLowerCase();
  return KONSULTASI_TRIGGERS.some((kw) => lower.includes(kw));
}

export default function NutriCoachPopup() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [hasNewMessage, setHasNewMessage] = useState(true);
  const [konsultasiStatus, setKonsultasiStatus] = useState<"idle" | "loading" | "sent" | "error">("idle");

  // Chat state setelah rujukan dikirim
  const [konsultasiId, setKonsultasiId] = useState<string | null>(null);
  const [chatMode, setChatMode] = useState(false); // true = tampil panel chat live
  const [chatMsgs, setChatMsgs] = useState<ChatMsg[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatSending, setChatSending] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    setMessages([
      {
        role: "ai",
        text: "Halo! 👋 Saya NutriCoach AI. Ada yang bisa saya bantu tentang nutrisi Anda hari ini?",
        time: getTimeStr(),
      },
    ]);
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  useEffect(() => {
    if (isOpen) setHasNewMessage(false);
  }, [isOpen]);

  const sendMessage = (text: string) => {
    if (!text.trim()) return;

    const userMsg: ChatMessage = { role: "user", text, time: getTimeStr() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    setTimeout(() => {
      const responses: Record<string, string> = {
        "Analisis nutrisi hari ini":
          "📊 Berdasarkan data hari ini:\n\n• Kalori: 1,430 / 2,000 kkal (71.5%)\n• Protein: 28g / 35g (80%) ✅\n• Karbohidrat: 45g / 50g (90%) ✅\n• Lemak: 22g / 25g (88%) ✅\n• Serat: 8g / 15g (53%) ⚠️\n\nSerat Anda masih kurang. Coba tambahkan sayuran hijau atau buah-buahan untuk makan malam.",
        "Rekomendasi makan malam":
          "🍽️ Untuk makan malam, saya rekomendasikan:\n\n1. **Sup Sayur + Tempe Goreng** (~350 kkal)\n   Kaya serat dan protein nabati\n\n2. **Ayam Panggang + Brokoli** (~420 kkal)\n   Tinggi protein untuk recovery\n\n3. **Pecel Lele + Lalapan** (~380 kkal)\n   Seimbang dengan sayuran segar",
        "Tips diet sehat":
          "💡 Tips diet sehat:\n\n1. Makan teratur — 3 makan utama + 2 snack\n2. Perbanyak serat — target 15g/hari\n3. Hidrasi cukup — minum 2.5L air per hari\n4. Protein seimbang — kombinasi hewani & nabati\n5. Batasi gula — maksimal 25g gula tambahan/hari",
      };

      const needsKonsultasi = shouldSuggestKonsultasi(text);

      const aiText =
        responses[text] ||
        (needsKonsultasi
          ? `Terima kasih sudah berbagi kondisi Anda. 🤔\n\nBerdasarkan yang Anda ceritakan, saya menyarankan untuk berkonsultasi langsung dengan Ahli Gizi kami agar mendapatkan penanganan yang lebih tepat dan personal.\n\nKlik tombol di bawah untuk menghubungi Ahli Gizi sekarang.`
          : `Terima kasih untuk pertanyaannya! 🤔\n\nBerdasarkan profil nutrisi Anda hari ini, asupan sudah cukup baik. Saya sarankan untuk fokus menambah serat dan air minum untuk mencapai target harian.\n\nAda pertanyaan lain?`);

      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: aiText,
          time: getTimeStr(),
          showKonsultasiBtn: needsKonsultasi && !responses[text],
        },
      ]);
      setIsTyping(false);
    }, 1200 + Math.random() * 800);
  };

  // Poll chat messages every 5 seconds when in chat mode
  const pollChat = useCallback(async (kId: string) => {
    const { ok, data } = await apiListChat(kId);
    if (ok && Array.isArray(data)) {
      setChatMsgs(data);
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, []);

  useEffect(() => {
    if (chatMode && konsultasiId) {
      pollChat(konsultasiId);
      pollRef.current = setInterval(() => pollChat(konsultasiId), 5000);
    }
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [chatMode, konsultasiId, pollChat]);

  const handleKirimKonsultasi = async (pesanUser: string) => {
    setKonsultasiStatus("loading");
    const pesanCoachbot = `Pasien membutuhkan konsultasi terkait: "${pesanUser}". Sistem NutriCoach AI menyarankan penanganan langsung dari ahli gizi untuk kondisi ini.`;

    const { ok, data } = await apiCreateKonsultasi(pesanCoachbot);

    if (ok) {
      const newId = data?.id_konsultasi ?? null;
      setKonsultasiId(newId);
      setKonsultasiStatus("sent");
      // Kirim pesan pembuka ke chat sebagai pesan user pertama
      if (newId) {
        await apiSendChat(newId, pesanUser, "user");
        setChatMode(true);
      }
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: "✅ Permintaan konsultasi terkirim! Sekarang kamu bisa langsung chat dengan Ahli Gizi di bawah ini. Ahli Gizi akan segera merespons.",
          time: getTimeStr(),
        },
      ]);
    } else {
      setKonsultasiStatus("error");
      setMessages((prev) => [
        ...prev,
        {
          role: "ai",
          text: "❌ Gagal mengirim permintaan. Pastikan Anda sudah login dan coba lagi.",
          time: getTimeStr(),
        },
      ]);
    }
  };

  const handleSendChat = async (e: FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || !konsultasiId || chatSending) return;
    setChatSending(true);
    const text = chatInput.trim();
    setChatInput("");
    await apiSendChat(konsultasiId, text, "user");
    await pollChat(konsultasiId);
    setChatSending(false);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

  // Cari pesan user terakhir untuk konteks konsultasi
  const lastUserMessage = [...messages].reverse().find((m) => m.role === "user")?.text ?? "";

  return (
    <>
      {/* ── Floating Button ── */}
      <button
        className={`${styles.fab} ${isOpen ? styles.fabHidden : ""}`}
        onClick={() => setIsOpen(true)}
        aria-label="Open NutriCoach AI"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" width="26" height="26">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        {hasNewMessage && <span className={styles.fabBadge}>1</span>}
        <span className={styles.fabPulse} />
      </button>

      {/* ── Chat Popup ── */}
      <div className={`${styles.popup} ${isOpen ? styles.popupOpen : ""}`}>
        {/* Header */}
        <div className={styles.popupHeader}>
          <div className={styles.popupHeaderLeft}>
            <div className={styles.aiAvatarSmall}>
              <svg viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" width="18" height="18">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <div>
              <h4>NutriCoach AI</h4>
              <span className={styles.onlineStatus}>● Online</span>
            </div>
          </div>
          <button className={styles.closeBtn} onClick={() => setIsOpen(false)} aria-label="Close chat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        {/* Messages */}
        <div className={styles.messages}>
          {messages.map((msg, i) => (
            <div key={i} className={`${styles.msgRow} ${msg.role === "user" ? styles.msgRowUser : ""}`}>
              <div className={`${styles.bubble} ${msg.role === "user" ? styles.bubbleUser : styles.bubbleAi}`}>
                <p style={{ whiteSpace: "pre-line" }}>{msg.text}</p>
                <span className={styles.msgTime}>{msg.time}</span>

                {/* Tombol Konsultasi Ahli Gizi — hanya muncul pada pesan AI yang relevan */}
                {msg.showKonsultasiBtn && konsultasiStatus !== "sent" && (
                  <button
                    onClick={() => handleKirimKonsultasi(lastUserMessage)}
                    disabled={konsultasiStatus === "loading"}
                    style={{
                      marginTop: 10,
                      display: "flex",
                      alignItems: "center",
                      gap: 6,
                      padding: "8px 14px",
                      background: konsultasiStatus === "loading" ? "#ccc" : "linear-gradient(135deg, #2e7d32, #4caf50)",
                      color: "#fff",
                      border: "none",
                      borderRadius: 20,
                      fontSize: 12,
                      fontWeight: 700,
                      cursor: konsultasiStatus === "loading" ? "wait" : "pointer",
                      width: "100%",
                      justifyContent: "center",
                      letterSpacing: "0.02em",
                      boxShadow: "0 2px 8px rgba(46,125,50,0.3)",
                      transition: "opacity 0.2s",
                    }}
                  >
                    🩺 {konsultasiStatus === "loading" ? "Mengirim..." : "Hubungi Ahli Gizi Sekarang"}
                  </button>
                )}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className={styles.msgRow}>
              <div className={`${styles.bubble} ${styles.bubbleAi}`}>
                <div className={styles.typingDots}>
                  <span /><span /><span />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Replies */}
        {messages.length <= 2 && !chatMode && (
          <div className={styles.quickReplies}>
            {quickReplies.map((q) => (
              <button key={q} className={styles.quickBtn} onClick={() => sendMessage(q)}>
                {q}
              </button>
            ))}
            <button
              className={styles.quickBtn}
              onClick={() => sendMessage("Saya punya kondisi khusus dan butuh konsultasi dokter")}
              style={{ borderColor: "#2e7d32", color: "#2e7d32" }}
            >
              🩺 Konsultasi Ahli Gizi
            </button>
          </div>
        )}

        {/* ── Live Chat Panel (muncul setelah konsultasi dibuat) ── */}
        {chatMode && (
          <div style={{
            borderTop: "2px solid #e8f5e9",
            background: "#f1f8e9",
            display: "flex",
            flexDirection: "column",
            maxHeight: 240,
          }}>
            {/* Chat header */}
            <div style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "8px 12px", background: "#2e7d32",
            }}>
              <span style={{ fontSize: 16 }}>🩺</span>
              <span style={{ color: "#fff", fontSize: 13, fontWeight: 700 }}>Chat dengan Ahli Gizi</span>
              <span style={{
                marginLeft: "auto", fontSize: 10, background: "rgba(255,255,255,0.2)",
                color: "#fff", padding: "2px 8px", borderRadius: 999, fontWeight: 600,
              }}>
                Live
              </span>
            </div>

            {/* Chat messages */}
            <div style={{
              flex: 1, overflowY: "auto", padding: "10px 12px",
              display: "flex", flexDirection: "column", gap: 8,
              maxHeight: 160,
            }}>
              {chatMsgs.length === 0 ? (
                <div style={{ textAlign: "center", fontSize: 12, color: "#666", padding: 12 }}>
                  Menunggu balasan dari Ahli Gizi... 🕐
                </div>
              ) : (
                chatMsgs.map((m) => (
                  <div
                    key={m.id_chat}
                    style={{
                      display: "flex",
                      flexDirection: "column",
                      alignItems: m.pengirim === "user" ? "flex-end" : "flex-start",
                    }}
                  >
                    <div style={{
                      maxWidth: "80%",
                      padding: "7px 11px",
                      borderRadius: m.pengirim === "user" ? "14px 14px 2px 14px" : "14px 14px 14px 2px",
                      background: m.pengirim === "user" ? "#2e7d32" : "#fff",
                      color: m.pengirim === "user" ? "#fff" : "#1a1c1c",
                      fontSize: 13,
                      lineHeight: 1.5,
                      boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
                    }}>
                      {m.pengirim === "ahli_gizi" && (
                        <div style={{ fontSize: 10, fontWeight: 700, color: "#2e7d32", marginBottom: 3 }}>
                          🩺 Ahli Gizi
                        </div>
                      )}
                      {m.pesan}
                    </div>
                    <span style={{ fontSize: 10, color: "#888", marginTop: 2 }}>
                      {formatTime(m.tanggal)}
                    </span>
                  </div>
                ))
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Chat input */}
            <form onSubmit={handleSendChat} style={{
              display: "flex", gap: 6, padding: "6px 10px",
              borderTop: "1px solid #c8e6c9", background: "#fff",
            }}>
              <input
                type="text"
                placeholder="Ketik pesan untuk ahli gizi..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                disabled={chatSending}
                style={{
                  flex: 1, padding: "7px 12px", fontSize: 13, border: "1px solid #c8e6c9",
                  borderRadius: 20, outline: "none", fontFamily: "inherit",
                }}
              />
              <button
                type="submit"
                disabled={!chatInput.trim() || chatSending}
                style={{
                  width: 34, height: 34, borderRadius: "50%", border: "none",
                  background: chatInput.trim() ? "#2e7d32" : "#ccc",
                  color: "#fff", cursor: chatInput.trim() ? "pointer" : "default",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  flexShrink: 0, transition: "background 0.2s",
                }}
              >
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="16" height="16">
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              </button>
            </form>
          </div>
        )}

        {/* Input CoachBot (sembunyikan saat chat mode aktif) */}
        {!chatMode && (
          <form onSubmit={handleSubmit} className={styles.inputBar}>
            <input
              type="text"
              placeholder="Ketik pertanyaan nutrisi..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className={styles.chatInput}
            />
            <button type="submit" className={styles.sendBtn} disabled={!input.trim() || isTyping}>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="18" height="18">
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </form>
        )}
      </div>
    </>
  );
}
