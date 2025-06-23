"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";

interface Cryptocurrency {
  id: number;
  name: string;
  symbol: string;
  network: string;
  price: string;
}

export default function CryptoDetailPage() {
  const params = useParams();
  const id = params?.id;
  const [crypto, setCrypto] = useState<Cryptocurrency | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(`http://localhost:8000/cryptocurrencies/${id}/`);
      if (response.ok) {
        const data = await response.json();
        setCrypto(data);
      } else {
        console.error("Ошибка при загрузке данных");
      }
    };

    if (id) {
      fetchData();
    }
  }, [id]);

  if (!crypto) {
    return <div className="text-white text-3xl text-center mt-10">Загрузка...</div>;
  }

  return (
    <div className="bg-blue-800 text-white min-h-screen py-20 px-10">
      <h1 className="text-5xl text-center font-bold mb-10">Информация о криптовалюте</h1>
      <div className="bg-blue-900 border border-yellow-400 rounded-xl p-10 w-full max-w-3xl mx-auto space-y-6">
        <p className="text-2xl">Название: {crypto.name}</p>
        <p className="text-2xl">Символ: {crypto.symbol}</p>
        <p className="text-2xl">Сеть: {crypto.network}</p>
        <p className="text-2xl">Цена: {parseFloat(crypto.price).toLocaleString("en-US", {
          style: "currency",
          currency: "USD",
        })}</p>
      </div>
    </div>
  );
}
