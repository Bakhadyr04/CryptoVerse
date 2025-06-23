"use client";

import React from "react";
import { useState, ChangeEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Download, Smartphone } from "lucide-react";
import { motion } from "framer-motion";
import Accordion from "@/components/ui/accordion";
import Link from "next/link";
import { FaApple, FaWindows, FaLinux } from "react-icons/fa";
import CryptoVolumeWidget from "./cryptocurrencies/CryptoVolumeWidget";
import PromotionsWidget from "./promotions/PromotionsWidget";
import RecentUsersMarquee from "./users/RecentUsersMarquee";

export default function Page(): JSX.Element {
  const [email, setEmail] = useState<string>("");

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
  };

  return (
    <div className="bg-blue-800 text-white min-h-screen">
      {/* Header */}
      <header role="banner" className="flex flex-col md:flex-row justify-between items-center p-6 md:p-10 max-w-7xl mx-auto gap-4">
        <a href="/" className="flex items-center gap-2">
          <img src="/logo.svg" alt="CryptoVerse logo" className="w-10 h-10" />
          <span className="text-yellow-400 font-bold text-3xl">CryptoVerse</span>
        </a>
        <nav role="navigation" className="flex flex-wrap justify-center gap-4 md:gap-6 text-2xl">
          <a href="/crypto" className="hover:text-yellow-400">Купить криптовалюту</a>
          <a href="#" className="hover:text-yellow-400">Рынки</a>
          <a href="#" className="hover:text-yellow-400">Торговля</a>
          <a href="/user-promotions" className="hover:text-yellow-400">Новости</a>
        </nav>
        <div className="flex gap-2">
          <Link href="/login">
            <Button className="bg-yellow-400 w-20 text-black hover:bg-gray-200 text-xl" aria-label="Вход в аккаунт">Вход</Button>
          </Link>
          <Link href="/register">
            <Button className="bg-yellow-400 w-40 text-black hover:bg-gray-200 text-xl" aria-label="Регистрация нового пользователя">Регистрация</Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main role="main">
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="py-20 px-4 max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-12"
        >
          <div className="text-white text-center md:text-left flex-1">
            <h1 className="text-4xl md:text-8xl font-bold leading-tight">
              Покупайте крипту с низкими комиссиями на <br />
              <span className="text-yellow-400">CryptoVerse</span>
            </h1>
            <div className="mt-6 flex flex-col sm:flex-row justify-center md:justify-start items-center gap-4">
              <label htmlFor="email" className="sr-only">Email или телефон</label>
              <Input
                id="email"
                type="email"
                placeholder="Электронная почта / номер телефона"
                value={email}
                onChange={handleInputChange}
                className="w-full sm:w-80 h-11 px-4 text-xl text-black shadow-sm"
              />
              <Link href="/register">
                <Button className="bg-yellow-400 text-xl text-black hover:bg-yellow-500 w-full sm:w-40" aria-label="Начать регистрацию">Начать</Button>
              </Link>
            </div>
          </div>
          <div className="flex-1 flex justify-center">
            <img src="/main-illustration.svg" alt="Crypto illustration" className="max-w-xs md:max-w-md" />
          </div>
        </motion.section>

        <RecentUsersMarquee />

        {/* App Section */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="bg-blue-800 py-20 px-4"
        >
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-12">
            <div className="flex-1 flex justify-center">
              <img src="/phone-illustration.svg" alt="Интерфейс мобильного приложения" className="max-w-[250px] md:max-w-sm" />
            </div>
            <div className="flex-1 text-center md:text-left">
              <h2 className="text-white text-4xl md:text-6xl font-semibold leading-tight mb-4">
                Торгуйте на ходу <br /> Где и когда угодно
              </h2>
              <div className="flex flex-col sm:flex-row pt-10 items-center justify-center md:justify-start gap-6">
                <img src="/qr-code.svg" alt="QR-код для загрузки приложения" className="w-32 h-32 md:w-40 md:h-40" />
                <p className="text-xl text-blue-200">
                  Отсканируйте QR-код, <br /> чтобы скачать приложение <br /> CryptoVerse
                </p>
              </div>
              <div className="flex flex-wrap gap-6 pt-10 text-white text-xl items-center justify-center md:justify-start">
                <a href="https://www.apple.com/macos" target="_blank" rel="noopener noreferrer" className="flex gap-4 items-center" aria-label="Скачать для MacOS">
                  <FaApple size={45} aria-hidden="true" /> MacOS
                </a>
                <a href="https://www.microsoft.com/windows" target="_blank" rel="noopener noreferrer" className="flex gap-4 items-center" aria-label="Скачать для Windows">
                  <FaWindows size={40} aria-hidden="true" /> Windows
                </a>
                <a href="https://www.linux.org/" target="_blank" rel="noopener noreferrer" className="flex gap-4 items-center" aria-label="Скачать для Linux">
                  <FaLinux size={40} aria-hidden="true" /> Linux
                </a>
              </div>
            </div>
          </div>
        </motion.section>

        <CryptoVolumeWidget />

        <PromotionsWidget />

        {/* FAQ Section */}
        <motion.section
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto py-16 px-4"
        >
          <h2 className="text-6xl font-semibold mb-6 mt-10 text-center">Часто задаваемые вопросы</h2>
          <div className="space-y-4 pt-10 pb-10 text-2xl">
            {[
              {
                question: "Что такое криптовалютная биржа?",
                answer:
                  "Криптобиржа — это цифровая площадка, позволяющая пользователям покупать и продавать криптовалюту, такую как Bitcoin, Ethereum и Tether",
              },
              {
                question: "Как купить биткойн и другие криптовалюты на CryptoVerse?",
                answer:
                  "Создайте аккаунт, пополните баланс и используйте торговый интерфейс для покупки нужной криптовалюты",
              },
              {
                question: "Как отслеживать цены на криптовалюту?",
                answer:
                  "В разделе ''Рынки'' вы можете отслеживать текущие цены, графики и изменения",
              },
              {
                question: "Как торговать криптовалютой на CryptoVerse?",
                answer:
                  "Выберите торговую пару, укажите сумму и тип ордера, затем нажмите ''Купить'' или ''Продать''",
              },
              {
                question: "Как заработать на криптовалюте на CryptoVerse?",
                answer:
                  "Вы можете использовать стейкинг, реферальную программу или участвовать в IDO/IEO",
              },
            ].map(({ question, answer }, i) => (
              <Accordion key={i} question={question} answer={answer} />
            ))}
          </div>
        </motion.section>
      </main>

      {/* Footer */}
      <footer role="contentinfo" className="bg-black text-blue-200 py-8 text-xl">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-6">
          <div>
            <h4 className="text-white mb-2">Сообщество</h4>
            <ul className="space-y-1">
              <li>Twitter</li>
              <li>Telegram</li>
              <li>YouTube</li>
              <li>GitHub</li>
            </ul>
          </div>
          <div>
            <h4 className="text-white mb-2">О нас</h4>
            <ul className="space-y-1">
              <li>Вакансии</li>
              <li>Новости</li>
              <li>Пресс-центр</li>
            </ul>
          </div>
          <div>
            <h4 className="text-white mb-2">Продукты</h4>
            <ul className="space-y-1">
              <li>Купить криптовалюту</li>
              <li>Academy</li>
              <li>Live</li>
              <li>Поддержка</li>
            </ul>
          </div>
          <div>
            <h4 className="text-white mb-2">Узнать больше</h4>
            <ul className="space-y-1">
              <li>Как торговать</li>
              <li>Цены</li>
              <li>Платежи</li>
            </ul>
          </div>
          <div>
            <h4 className="text-white mb-2">Поддержка</h4>
            <ul className="space-y-1">
              <li>24/7 чат</li>
              <li>Центр помощи</li>
              <li>Комиссии</li>
            </ul>
          </div>
        </div>
        <div className="text-center pt-5 text-xl mt-6">CryptoVerse © 2025</div>
      </footer>
    </div>
  );
}
