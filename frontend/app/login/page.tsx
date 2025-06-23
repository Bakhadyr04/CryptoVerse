"use client";

import { useState, ChangeEvent } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { FcGoogle } from "react-icons/fc";
import { FaApple } from "react-icons/fa";
import Image from "next/image";
import Link from "next/link";

export default function LoginPage() {
  const [email, setEmail] = useState<string>("");

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value);
  };

  return (
    <div className="bg-blue-900 min-h-screen flex flex-col items-center justify-center text-white">
      <div className="bg-black p-8 rounded-xl border-2 border-yellow-400 w-[350px] sm:w-[420px] text-white">
        {/* Header: Logo and Title */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            {/* <Image src="/logo.svg" alt="Logo" width={32} height={32} />
            <span className="text-yellow-400 font-bold text-lg">CryptoVerse</span> */}
            <a href="/" className="flex items-center">
              <img src="/logo.svg" alt="CryptoVerse logo" className="w-12 h-12" />
              <span className="text-yellow-400 font-bold text-3xl">CryptoVerse</span>
            </a>
          </div>
        </div>

        <h2 className="text-2xl font-semibold mb-4">Войти</h2>

        <label className="block text-sm mb-2">Электронная почта / номер телефона</label>
        <Input
          type="text"
          value={email}
          onChange={handleInputChange}
          placeholder="+7 (969) 696-96-96"
          className="bg-black text-black border border-gray-600 mb-4 w-full h-12 text-base px-4"
        />

        <Button className="w-full bg-yellow-400 text-black hover:bg-yellow-500 mb-4">
          Войти
        </Button>

        <div className="text-center text-sm text-gray-400 mb-4">или</div>

        <Button className="w-full mb-2 flex items-center gap-2 justify-center border border-gray-600 bg-black hover:bg-gray-800">
          <FcGoogle size={20} /> Продолжить с Google
        </Button>
        <Button className="w-full flex items-center gap-2 justify-center border border-gray-600 bg-black hover:bg-gray-800">
          <FaApple size={20} /> Продолжить с Apple
        </Button>
      </div>

      {/* Footer */}
      <div className="mt-4 text-sm text-center underline">
        <p>
          <Link href="/register" className="hover:text-yellow-400 hover:underline">
            Создать аккаунт CryptoVerse
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
