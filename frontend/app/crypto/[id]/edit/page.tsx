"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";

export default function EditCryptoPage() {
  const params = useParams();
  const id = params?.id;
  const [name, setName] = useState("");
  const [symbol, setSymbol] = useState("");
  const [network, setNetwork] = useState("");
  const [price, setPrice] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(`http://localhost:8000/cryptocurrencies/${id}/`);
      const data = await response.json();
      setName(data.name);
      setSymbol(data.symbol);
      setNetwork(data.network);
      setPrice(data.price);
    };
    fetchData();
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const response = await fetch(`http://localhost:8000/cryptocurrencies/${id}/edit/`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, symbol, network, price }),
    });

    if (response.ok) {
      alert("Изменения сохранены");
      window.location.href = "/crypto";
    } else {
      alert("Ошибка при сохранении");
    }
  };

  return (
    <div className="bg-blue-800 min-h-screen text-white py-10">
      <div className="max-w-xl mx-auto bg-blue-900 p-6 rounded-xl border border-yellow-400">
        <h1 className="text-3xl mb-6 text-center font-bold">Редактировать криптовалюту</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label>Название</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)} required className="w-full p-2 rounded bg-blue-950 text-white"/>
          </div>
          <div>
            <label>Символ</label>
            <input type="text" value={symbol} onChange={(e) => setSymbol(e.target.value)} required className="w-full p-2 rounded bg-blue-950 text-white"/>
          </div>
          <div>
            <label>Сеть</label>
            <input type="text" value={network} onChange={(e) => setNetwork(e.target.value)} required className="w-full p-2 rounded bg-blue-950 text-white"/>
          </div>
          <div>
            <label>Цена (USD)</label>
            <input type="number" value={price} onChange={(e) => setPrice(e.target.value)} required className="w-full p-2 rounded bg-blue-950 text-white"/>
          </div>
          <button type="submit" className="w-full bg-yellow-400 text-black py-2 rounded font-bold text-lg hover:bg-yellow-300">Сохранить</button>
        </form>
      </div>
    </div>
  );
}
