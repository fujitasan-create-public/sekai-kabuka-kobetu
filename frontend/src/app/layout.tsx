import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "世界の株価 個別",
  description: "株価ダッシュボード - 準リアルタイム更新",
};

type RootLayoutProps = {
  children: React.ReactNode;
};

export default function RootLayout({ children }: RootLayoutProps) {
  return (
    <html lang="ja" suppressHydrationWarning>
      <body className="min-h-screen transition-colors duration-200">{children}</body>
    </html>
  );
}
