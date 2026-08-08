import type { Metadata } from "next";
import { Inter, Outfit, Tajawal } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import { ThemeProvider } from "@/components/ThemeProvider";
import AdblockDetector from "@/components/AdblockDetector";
import SocialBar from "@/components/SocialBar";

import { cookies } from "next/headers";
import { headers } from "next/headers";
import Script from "next/script";

const interStatic = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const outfitStatic = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  display: "swap",
});

const tajawalStatic = Tajawal({
  subsets: ["arabic"],
  weight: ["400", "500", "700", "800", "900"],
  variable: "--font-tajawal",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Tomito | توميتو مشاهدة وتحميل الأفلام والمسلسلات مترجمة بجودة 4K بدون إعلانات",
  description: "أفضل موقع لمشاهدة وتحميل الأفلام والمسلسلات الحصرية بجودة عالية وبدون إعلانات.",
  icons: {
    icon: "/favicon.ico",
    apple: "/favicon.ico",
    other: [
      { rel: "msapplication-TileImage", url: "/favicon.ico" },
    ],
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: "https://tomito.xyz",
  },
  openGraph: {
    siteName: "TOMITO",
    locale: "ar_SA",
    type: "website",
    url: "https://tomito.xyz",
    title: "Tomito | توميتو – مشاهدة أفلام ومسلسلات مترجمة 4K بدون إعلانات",
    description: "أفضل موقع لمشاهدة وتحميل الأفلام والمسلسلات الحصرية بجودة عالية وبدون إعلانات.",
    images: [{ url: "https://tomito.xyz/og-default.jpg", width: 1200, height: 630, alt: "Tomito" }],
  },
  twitter: {
    card: "summary_large_image",
    site: "@tomito_xyz",
    creator: "@tomito_xyz",
    title: "Tomito | توميتو – مشاهدة أفلام ومسلسلات مترجمة 4K بدون إعلانات",
    description: "أفضل موقع لمشاهدة وتحميل الأفلام والمسلسلات الحصرية بجودة عالية وبدون إعلانات.",
    images: ["https://tomito.xyz/og-default.jpg"],
  },
  other: {
    "Content-Language": "ar",
    "rating": "General",
    "revisit-after": "3 days",
    "msapplication-TileColor": "#000000",
    "apple-mobile-web-app-capable": "yes",
    "apple-mobile-web-app-status-bar-style": "black-translucent",
    "apple-mobile-web-app-title": "TOMITO",
    "resource-type": "document",
    "Cache-Control": "max-age=3600, must-revalidate",
  },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const cookieStore = await cookies();
  const locale = cookieStore.get("NEXT_LOCALE")?.value || "ar";
  const dir = locale === "ar" ? "rtl" : "ltr";
  
  // Check if current path is movie or TV detail page to hide navbar
  const headersList = await headers();
  const pathname = headersList.get('x-pathname') || '';
  const isDetailPage = /^\/(movie|tv)\/\d+/.test(pathname);

  return (
    <html lang={locale} dir={dir} className={`${interStatic.variable} ${outfitStatic.variable} ${tajawalStatic.variable}`} suppressHydrationWarning>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
        <meta name="theme-color" content="#000" />
        <meta name="yandex-verification" content="fbd3e913244fb343" />
        
        {/* Preconnect to ad networks for faster loading */}
        <link rel="preconnect" href="https://pl30597637.effectivecpmnetwork.com" />
        <link rel="preconnect" href="https://pl30598106.effectivecpmnetwork.com" />
        <link rel="preconnect" href="https://pl30598123.effectivecpmnetwork.com" />
        <link rel="preconnect" href="https://pl30597533.effectivecpmnetwork.com" />
        
        {/* Google Analytics */}
        <Script 
          src="https://www.googletagmanager.com/gtag/js?id=G-PRCQVS90BX"
          strategy="afterInteractive"
        />
        <Script id="google-analytics" strategy="afterInteractive">
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-PRCQVS90BX');
          `}
        </Script>
        
        {/* Ad Scripts - Preload for faster loading */}
        <Script 
          src="https://pl30597637.effectivecpmnetwork.com/08370281e563742f6dcb56530f5e8082/invoke.js"
          strategy="afterInteractive"
          data-cfasync="false"
        />
        <Script 
          src="https://pl30598106.effectivecpmnetwork.com/7853b06f071ef8a725aee4957098eae1/invoke.js"
          strategy="afterInteractive"
          data-cfasync="false"
        />
        <Script 
          src="https://pl30598123.effectivecpmnetwork.com/74473a481e12f32fea68225a3cc97eed/invoke.js"
          strategy="afterInteractive"
          data-cfasync="false"
        />
        <Script 
          src="https://pl30597533.effectivecpmnetwork.com/b6/9d/a7/b69da7c3ee677ac42178f0d30e42047b.js"
          strategy="afterInteractive"
          data-cfasync="false"
        />
      </head>
      <body style={{ background: "rgba(0,0,0,0.7) url('/background.jpeg') center/cover no-repeat fixed" }}>
        <ThemeProvider>

          {/* ───── ADBLOCK DETECTOR ───── */}
          <AdblockDetector />

          {/* ───── SOCIAL BAR ───── */}
          <SocialBar />

          {/* ───── NAVBAR ───── */}
          {!isDetailPage && <Navbar />}

          {/* ───── MAIN ───── */}
          <main className="min-h-screen">
            {children}
          </main>

          {/* ───── FOOTER ───── */}
          <footer className="premium-footer">
            <div className="footer-logo" style={{ fontFamily: 'var(--font-outfit)' }}>TOMITO</div>
            <p>© 2026 جميع الحقوق محفوظة — أفلام ومسلسلات بجودة عالية</p>
          </footer>
        </ThemeProvider>
      </body>
    </html>
  );
}
