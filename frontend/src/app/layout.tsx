import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Jimamet — Medical Nutrition Platform",
  description:
    "Transformasikan kesehatan Anda dengan analisis nutrisi berbasis AI yang presisi. Pantau asupan makanan secara klinis dan profesional.",
  keywords: [
    "nutrisi",
    "medical nutrition",
    "AI food analysis",
    "diet tracking",
    "kesehatan",
    "jimamet",
  ],
  authors: [{ name: "Jimamet Team" }],
  openGraph: {
    title: "Jimamet — Medical Nutrition Platform",
    description:
      "Analisis nutrisi berbasis AI dengan presisi klinis.",
    type: "website",
    locale: "id_ID",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id">
      <body>{children}</body>
    </html>
  );
}
