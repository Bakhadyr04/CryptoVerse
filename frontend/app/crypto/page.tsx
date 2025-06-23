"use client";

import React, { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useSearchParams } from "next/navigation";
import CryptoFilterWidget from "../cryptocurrencies/CryptoFilterWidget";

interface Cryptocurrency {
  id?: number;
  name: string;
  symbol: string;
  network: string;
  price: string;
}

export default function CryptoPage() {
  const [isBuy, setIsBuy] = useState(true);
  const [cryptos, setCryptos] = useState<Cryptocurrency[]>([]);
  const [avgPrice, setAvgPrice] = useState<number | null>(null);
  const searchParams = useSearchParams();
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Форма для добавления/редактирования
  const [form, setForm] = useState<Cryptocurrency>({
    name: "",
    symbol: "",
    network: "",
    price: ""
  });
  const [editId, setEditId] = useState<number | null>(null);

  useEffect(() => {
    fetchCryptos();
  }, [searchParams]);

  const fetchCryptos = async () => {
    const queryString = searchParams?.toString() ?? "";
    const response = await fetch(`http://localhost:8000/cryptocurrencies/?${queryString}`);
    const data = await response.json();
    setCryptos(data.cryptocurrencies);
    setAvgPrice(data.avg_price);
  };

  const handleDelete = async (id: number) => {
    if (confirm("Вы уверены, что хотите удалить эту криптовалюту?")) {
      await fetch(`http://localhost:8000/cryptocurrencies/${id}/delete/`, { method: "DELETE" });
      await fetchCryptos();
    }
  };

  const handleSubmit = async () => {
    try {
      const method = editId ? "PUT" : "POST";
      const url = editId
        ? `http://localhost:8000/cryptocurrencies/${editId}/update/`
        : `http://localhost:8000/cryptocurrencies/add/`;

      const response = await fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form)
      });

      if (!response.ok) throw new Error("Ошибка сохранения");

      setForm({ name: "", symbol: "", network: "", price: "" });
      setEditId(null);
      await fetchCryptos();
      alert("Сохранено!");
    } catch (error) {
      alert("Ошибка при сохранении");
    }
  };

  const handleEdit = (crypto: Cryptocurrency) => {
    setForm(crypto);
    setEditId(crypto.id ?? null);
  };

  const paginated = cryptos.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  const totalPages = Math.ceil(cryptos.length / pageSize);

  return (
    <div className="bg-blue-800 text-white min-h-screen">
      <header className="flex justify-between items-center p-10 max-w-7xl mx-auto">
        <a href="/" className="flex items-center">
          <img src="/logo.svg" alt="CryptoVerse logo" className="w-12 h-12" />
          <span className="text-yellow-400 font-bold text-3xl">CryptoVerse</span>
        </a>
        <nav className="hidden md:flex gap-6 text-2xl">
          <a href="/crypto" className="hover:text-yellow-400">Купить криптовалюту</a>
          <a href="#" className="hover:text-yellow-400">Рынки</a>
          <a href="#" className="hover:text-yellow-400">Торговля</a>
          <a href="/user-promotions" className="hover:text-yellow-400">Новости</a>
        </nav>
        <div className="flex gap-2">
          <a href="/login">
            <Button className="bg-yellow-400 w-20 text-black hover:bg-gray-200 text-xl">Вход</Button>
          </a>
          <a href="/register">
            <Button className="bg-yellow-400 w-40 text-black hover:bg-gray-200 text-xl">Регистрация</Button>
          </a>
        </div>
      </header>

      <div className="px-4 py-12 space-y-20 mb-20">
        <h1 className="text-5xl md:text-7xl font-bold max-w-7xl mx-auto">Купить криптовалюту</h1>

        <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-8">
          <div className="flex flex-col md:flex-row gap-8 w-full">
            <div className="w-full md:w-2/3 border border-yellow-400 rounded-xl p-6 bg-blue-900">
              <table className="w-full text-left">
                <thead>
                  <tr className="text-yellow-400 border-b border-yellow-400 text-xl">
                    <th className="pb-2">№</th>
                    <th className="pb-2">Название</th>
                    <th className="pb-2">Символ</th>
                    <th className="pb-2">Сеть</th>
                    <th className="pb-2">Цена</th>
                    <th className="pb-2">Действия</th>
                  </tr>
                </thead>
                <tbody>
                  {paginated.map((crypto, i) => (
                    <tr key={crypto.id} className="border-t border-gray-600 text-lg">
                      <td className="py-2">{(currentPage - 1) * pageSize + i + 1}</td>
                      <td className="py-2">
                        <a href={`/crypto/${crypto.id}`} className="text-yellow-400 hover:underline">
                          {crypto.name}
                        </a>
                      </td>
                      <td className="py-2">{crypto.symbol}</td>
                      <td className="py-2">{crypto.network}</td>
                      <td className="py-2">
                        {parseFloat(crypto.price).toLocaleString("en-US", { style: "currency", currency: "USD" })}
                      </td>
                      <td className="py-2">
                        <button onClick={() => handleEdit(crypto)} className="mr-4 text-green-400 hover:underline">Редактировать</button>
                        <button onClick={() => handleDelete(crypto.id!)} className="text-red-400 hover:underline">Удалить</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {avgPrice !== null && (
                <div className="mt-6 text-xl font-semibold text-center text-yellow-400">
                  Средняя цена: {Number(avgPrice).toLocaleString("en-US", { style: "currency", currency: "USD" })}
                </div>
              )}

              <div className="flex flex-wrap justify-center gap-2 pt-6 max-w-[360px] mx-auto">
                {Array.from({ length: totalPages }, (_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentPage(i + 1)}
                    className={`w-8 h-8 border rounded ${currentPage === i + 1 ? "bg-yellow-400 text-black" : "border-white text-white"}`}
                  >{i + 1}</button>
                ))}
              </div>
            </div>

            <div className="w-full md:w-[320px] border border-yellow-400 bg-blue-900 rounded-xl p-6 space-y-4">
              <CryptoFilterWidget />
              <h3 className="text-xl text-white font-bold">{editId ? "Редактировать" : "Добавить новую криптовалюту"}</h3>
              <div className="space-y-3">
                <Input placeholder="Название" value={form.name} onChange={e => setForm({...form, name: e.target.value})} />
                <Input placeholder="Символ" value={form.symbol} onChange={e => setForm({...form, symbol: e.target.value})} />
                <Input placeholder="Сеть" value={form.network} onChange={e => setForm({...form, network: e.target.value})} />
                <Input placeholder="Цена (USD)" value={form.price} onChange={e => setForm({...form, price: e.target.value})} />
                <Button className="w-full bg-yellow-400 text-black py-2 text-lg" onClick={handleSubmit}>
                  {editId ? "Сохранить изменения" : "Добавить"}
                </Button>
              </div>
            </div>
          </div>
          {/* Блок купли-продажи крипты */}
          {/* <div className="border border-yellow-400 rounded-2xl p-6 bg-blue-900 w-full md:w-1/2">
            <div className="flex gap-4 mb-6">
              <button className={`px-4 py-2 rounded-t-md font-semibold ${isBuy ? "bg-blue-950 text-white" : "bg-blue-900"}`} onClick={() => setIsBuy(true)}>Купить</button>
              <button className={`px-4 py-2 rounded-t-md font-semibold ${!isBuy ? "bg-blue-950 text-white" : "bg-blue-900"}`} onClick={() => setIsBuy(false)}>Продать</button>
            </div>
            <div className="bg-blue-900 p-4 rounded-b-md space-y-4">
              <div>
                <label className="text-lg">Списать</label>
                <div className="flex items-center gap-2 bg-blue-950 p-2 rounded">
                  <input type="number" defaultValue={0.92} className="bg-transparent w-full outline-none text-white" />
                  <span className="text-gray-400">EUR ⌄</span>
                </div>
              </div>
              <div>
                <label className="text-lg">Получить</label>
                <div className="flex items-center gap-2 bg-blue-950 p-2 rounded">
                  <input type="number" defaultValue={1} className="bg-transparent w-full outline-none text-white" />
                  <span className="text-gray-400">USDT ⌄</span>
                </div>
              </div>
              <button className="w-full bg-yellow-400 text-black py-2 rounded font-bold text-lg hover:bg-yellow-300">Купить / Продать</button>
            </div>
          </div> */}
        </div>
      </div>

      <footer className="bg-black text-blue-200 py-8 text-xl">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-2 md:grid-cols-5 gap-6">
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
