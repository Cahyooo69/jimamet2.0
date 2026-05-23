"use client";

import { useState, useRef, useEffect, FormEvent } from "react";
import styles from "./nutricoach-popup.module.css";

interface ChatMessage {
  role: "ai" | "user";
  text: string;
  time: string;
}

const quickReplies = [
  "Analisis nutrisi hari ini",
  "Rekomendasi makan malam",
  "Tips diet sehat",
];

function getTimeStr() {
  return new Date().toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" });
}

export default function NutriCoachPopup() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [hasNewMessage, setHasNewMessage] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize the greeting message on client only to avoid hydration mismatch
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

    setMessages((prev) => [...prev, { role: "user", text, time: getTimeStr() }]);
    setInput("");
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const responses: Record<string, string> = {
        "Analisis nutrisi hari ini":
          "📊 Berdasarkan data hari ini:\n\n• Kalori: 1,430 / 2,000 kkal (71.5%)\n• Protein: 28g / 35g (80%) ✅\n• Karbohidrat: 45g / 50g (90%) ✅\n• Lemak: 22g / 25g (88%) ✅\n• Serat: 8g / 15g (53%) ⚠️\n\nSerat Anda masih kurang. Coba tambahkan sayuran hijau atau buah-buahan untuk makan malam.",
        "Rekomendasi makan malam":
          "🍽️ Untuk makan malam, saya rekomendasikan:\n\n1. **Sup Sayur + Tempe Goreng** (~350 kkal)\n   Kaya serat dan protein nabati\n\n2. **Ayam Panggang + Brokoli** (~420 kkal)\n   Tinggi protein untuk recovery\n\n3. **Pecel Lele + Lalapan** (~380 kkal)\n   Seimbang dengan sayuran segar\n\nSemua opsi akan membantu memenuhi target serat harian Anda.",
        "Tips diet sehat":
          "💡 Tips diet sehat untuk Anda:\n\n1. **Makan teratur** — 3 makan utama + 2 snack\n2. **Perbanyak serat** — target 15g/hari dari sayur & buah\n3. **Hidrasi cukup** — minum 2.5L air per hari\n4. **Protein seimbang** — kombinasi hewani & nabati\n5. **Batasi gula** — maksimal 25g gula tambahan/hari",
      };

      const aiText =
        responses[text] ||
        `Terima kasih untuk pertanyaannya! 🤔\n\nBerdasarkan profil nutrisi Anda hari ini, asupan sudah cukup baik dengan total 1,430 kkal. Saya sarankan untuk fokus menambah serat dan air minum untuk mencapai target harian.\n\nAda pertanyaan lain?`;

      setMessages((prev) => [
        ...prev,
        { role: "ai", text: aiText, time: getTimeStr() },
      ]);
      setIsTyping(false);
    }, 1200 + Math.random() * 800);
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };

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
              </div>
            </div>
          ))}
          {isTyping && (
            <div className={styles.msgRow}>
              <div className={`${styles.bubble} ${styles.bubbleAi}`}>
                <div className={styles.typingDots}>
                  <span />
                  <span />
                  <span />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Replies */}
        {messages.length <= 2 && (
          <div className={styles.quickReplies}>
            {quickReplies.map((q) => (
              <button key={q} className={styles.quickBtn} onClick={() => sendMessage(q)}>
                {q}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
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
      </div>
    </>
  );
}
