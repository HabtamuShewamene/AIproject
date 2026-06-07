import "./globals.css";
import ClientShell from "@/components/layout/ClientShell";

export const metadata = {
  title: "SentiAI — AI Sentiment Analysis Platform",
  description:
    "Production-grade AI sentiment analysis dashboard. Analyze emotions from X/Twitter posts and custom text in real-time.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
      </head>
      <body>
        <ClientShell>{children}</ClientShell>
      </body>
    </html>
  );
}
