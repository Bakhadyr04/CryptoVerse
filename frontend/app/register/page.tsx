"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { FcGoogle } from "react-icons/fc";
import { FaApple } from "react-icons/fa";
import Image from "next/image";
import Link from "next/link";

export default function RegisterPage() {
  const [email, setEmail] = useState("");

  return (
    <div className="bg-blue-900 min-h-screen flex flex-col items-center justify-center text-white">
      <div className="bg-black p-8 rounded-xl border-2 border-yellow-400 w-[350px] sm:w-[420px] text-white">
        {/* Logo */}
        <div className="flex items-center gap-2 mb-6">
          {/* <Image src="/logo.svg" alt="Logo" width={32} height={32} />
          <span className="text-yellow-400 font-bold text-xl">CryptoVerse</span> */}
          <a href="/" className="flex items-center">
            <img src="/logo.svg" alt="CryptoVerse logo" className="w-12 h-12" />
            <span className="text-yellow-400 font-bold text-3xl">CryptoVerse</span>
          </a>
        </div>

        {/* Title */}
        <h2 className="text-2xl font-bold mb-2">Добро пожаловать на CryptoVerse</h2>
        <p className="text-sm text-blue-400 mb-4">
          Присоединяйтесь к крупнейшей криптовалютной бирже в мире
        </p>

        {/* Email Input */}
        <label className="block text-sm mb-2">Электронная почта / номер телефона</label>
        <Input
          type="text"
          placeholder="+7 (969) 696-96-96"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-80 h-11 px-4 text-xl text-black shadow-sm"
        />

        {/* Checkbox */}
        <label className="flex items-start gap-2 pt-5 text-sm text-left mb-4">
          <input type="checkbox" className="mt-1" />
          Создавая учетную запись, я соглашаюсь с 
          <span className="underline">Условиями использования CryptoVerse и Политикой конфиденциальности</span>
        </label>

        {/* Register Button */}
        <Button className="w-full mb-4">Зарегистрироваться</Button>

        {/* Divider */}
        <div className="text-center text-sm text-gray-400 mb-4">или</div>

        {/* Social Buttons */}
        <Button className="w-full mb-2 flex items-center gap-2 justify-center border border-gray-600 bg-black hover:bg-gray-800">
          <FcGoogle size={20} /> Продолжить с Google
        </Button>
        <Button className="w-full flex items-center gap-2 justify-center border border-gray-600 bg-black hover:bg-gray-800">
          <FaApple size={20} /> Продолжить с Apple
        </Button>
      </div>

      {/* Footer Links */}
      <div className="mt-6 text-center text-sm">
        <p>
          <Link href="#" className="text-yellow-400 hover:underline">
            Зарегистрируйте корпоративный аккаунт
          </Link>
        </p>
        <p>
          или{" "}
          <Link href="/login" className="underline hover:text-yellow-400">
            Войдите в систему
          </Link>
        </p>
      </div>

      <footer className="absolute bottom-4 text-xs text-gray-300 space-x-4">
        <Link href="#">Cookies</Link>
        <Link href="#">Условия использования</Link>
        <Link href="#">Политика конфиденциальности</Link>
      </footer>
    </div>
  );
}
