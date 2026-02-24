import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-mono",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Cofounder — AI Codebase Orchestrator",
  description:
    "Design-First, Code-Second. Transform your ideas into production-ready code through AI-powered architecture planning and sandboxed execution.",
  keywords: [
    "AI",
    "code generation",
    "architecture",
    "orchestrator",
    "Mermaid.js",
    "design-first",
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${jetbrainsMono.variable} font-[var(--font-inter)] antialiased`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
