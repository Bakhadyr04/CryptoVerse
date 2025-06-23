"use client";

import React, { useState } from "react";

export default function AddCryptoPage() {
  const [name, setName] = useState("");
  const [symbol, setSymbol] = useState("");
  const [network, setNetwork] = useState("");
  const [price, setPrice] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const response = await fetch("http://localhost:8000/cryptocurrencies/add/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, symbol, network, price }),
    });

    if (response.ok) {
      alert("Криптовалюта успешно добавлена");
      window.location.href = "/crypto";
    } else {
      alert("Ошибка при добавлении");
    }
  };

  return (
    <div className="bg-blue-800 min-h-screen text-white py-10">
      <div className="max-w-xl mx-auto bg-blue-900 p-6 rounded-xl border border-yellow-400">
        <h1 className="text-3xl mb-6 text-center font-bold">Добавить криптовалюту</h1>
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
          <button type="submit" className="w-full bg-yellow-400 text-black py-2 rounded font-bold text-lg hover:bg-yellow-300">Добавить</button>
        </form>
      </div>
    </div>
  );
}
