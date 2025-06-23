// import "../styles/globals.css";
// import type { Metadata } from "next";

// export const metadata: Metadata = {
//   title: "CryptoVerse – Криптобиржа нового поколения",
//   description: "Покупайте и торгуйте криптовалютой с минимальными комиссиями и удобным интерфейсом.",
//   keywords: ["криптовалюта", "биржа", "crypto", "торговля", "bitcoin"],
//   openGraph: {
//     title: "CryptoVerse",
//     description: "Торгуйте криптой на современной платформе",
//     type: "website",
//     url: "http://localhost:3000",
//     images: [
//       {
//         url: "/logo.png",
//         width: 800,
//         height: 600,
//         alt: "CryptoVerse",
//       },
//     ],
//   },
// };

// app/layout.tsx

// import "../styles/globals.css";
// import type { Metadata } from "next";

// export const metadata: Metadata = {
//   title: "CryptoVerse",
//   description: "Криптобиржа нового поколения",
// };

// export default function RootLayout({ children }: { children: React.ReactNode }) {
//   return (
//     <html lang="ru">
//       <body>{children}</body>
//     </html>
//   );
// }


import "../styles/globals.css";
import type { Metadata } from "next";
import { Sofia_Sans_Condensed } from "next/font/google";

const sofia = Sofia_Sans_Condensed({
  subsets: ["latin", "cyrillic"],
  weight: ["400", "500", "600", "700", "800"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "CryptoVerse – Криптобиржа нового поколения",
  description: "Покупайте и торгуйте криптовалютой с минимальными комиссиями и удобным интерфейсом.",
  keywords: ["криптовалюта", "биржа", "crypto", "торговля", "bitcoin"],
  openGraph: {
    title: "CryptoVerse",
    description: "Торгуйте криптой на современной платформе",
    type: "website",
    url: "http://localhost:3000",
    images: [
      {
        url: "/logo.svg",
        width: 800,
        height: 600,
        alt: "CryptoVerse",
      },
    ],
  },
  icons: {
    icon: "/favicon.png",
  },
  metadataBase: new URL("http://localhost:3000"),
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <head />
      <body className={`${sofia.className} antialiased bg-white text-black`}>{children}</body>
    </html>
  );
}
