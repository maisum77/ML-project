import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "SocialPulse AI — Real-Time Misinformation & Trend Analyzer",
  description: "ML-powered platform for detecting hot topics, analyzing sentiment, and identifying fake news in real-time.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="font-body antialiased">{children}</body>
    </html>
  );
}