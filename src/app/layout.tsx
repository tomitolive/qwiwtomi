import type { Metadata } from "next";
import { Inter, Outfit, Tajawal } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/Navbar";
import { ThemeProvider } from "@/components/ThemeProvider";
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
  title: "TOMITO — مشاهدة أفلام ومسلسلات أون لاين",
  description: "أفضل موقع لمشاهدة وتحميل الأفلام والمسلسلات الحصرية بجودة عالية وبدون إعلانات.",
  icons: {
    icon: "/favicon.ico",
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
        <Script 
          src="https://pl29663723.effectivecpmnetwork.com/6e/78/14/6e781401b81579a741ac7074d6fe77eb.js"
          strategy="afterInteractive"
        />
      </head>
      <body>
        <ThemeProvider>
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
