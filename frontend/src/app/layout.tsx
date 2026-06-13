import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Template Next.js",
  description: "FastAPI + Next.js template frontend",
};

type RootLayoutProps = {
  children: React.ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
