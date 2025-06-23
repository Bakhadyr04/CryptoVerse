'use client';

import React, { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import CryptoFilter from "./CryptoFilterWidget";
import Link from "next/link";

interface Cryptocurrency {
  id: number;
  name: string;
  symbol: string;
  network: string;
  price: string;
}

export default function Page(): JSX.Element {
  const [cryptos, setCryptos] = useState<Cryptocurrency[]>([]);
  const [avgPrice, setAvgPrice] = useState<number | null>(null);
  const searchParams = useSearchParams();

  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  useEffect(() => {
    const fetchData = async () => {
      const queryString = searchParams?.toString() ?? '';
      const response = await fetch(`http://localhost:8000/cryptocurrencies/?${queryString}`);
      const data = await response.json();
      setCryptos(data.cryptocurrencies);
      setAvgPrice(data.avg_price);
    };

    fetchData();
  }, [searchParams]);

  const paginated = cryptos.slice(
    (currentPage - 1) * pageSize,
    currentPage * pageSize
  );

  const totalPages = Math.ceil(cryptos.length / pageSize);

  return (
    <div className="bg-blue-800 text-white">
      <main>
        <section className="py-10 px-4 max-w-6xl mx-auto">
          <h2 className="text-4xl md:text-6xl font-bold text-white text-center mt-10 mb-10">
            Топ криптовалют
          </h2>
          <div className="flex flex-col md:flex-row gap-8">
            <div className="w-full md:w-2/3 border border-yellow-400 rounded-xl p-6 bg-blue-900">

              {/* Таблица */}
              <table className="w-full text-left">
                <thead>
                  <tr className="text-yellow-400 border-b border-yellow-400 text-xl">
                    <th className="pb-2">№</th>
                    <th className="pb-2">Название</th>
                    <th className="pb-2">Символ</th>
                    <th className="pb-2">Сеть</th>
                    <th className="pb-2">Цена</th>
                  </tr>
                </thead>
                <tbody>
                  {paginated.map((crypto, i) => (
                    <tr key={crypto.id} className="border-t border-gray-600 text-lg">
                      <td className="py-2">{(currentPage - 1) * pageSize + i + 1}</td>
                      <td className="py-2">{crypto.name}</td>
                      <td className="py-2">{crypto.symbol}</td>
                      <td className="py-2">{crypto.network}</td>
                      <td className="py-2">
                        {parseFloat(crypto.price).toLocaleString("en-US", {
                          style: "currency",
                          currency: "USD",
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* Средняя цена */}
              {avgPrice !== null && (
                <div className="mt-6 text-xl font-semibold text-center text-yellow-400">
                  Средняя цена: {Number(avgPrice).toLocaleString("en-US", {
                    style: "currency",
                    currency: "USD",
                  })}
                </div>
              )}

              {/* Пагинация */}
              <div className="flex flex-wrap justify-center gap-2 pt-6 max-w-[360px] mx-auto">
                {Array.from({ length: totalPages }, (_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentPage(i + 1)}
                    className={`w-8 h-8 border rounded ${currentPage === i + 1
                      ? "bg-yellow-400 text-black"
                      : "border-white text-white"
                      }`}
                  >
                    {i + 1}
                  </button>
                ))}
              </div>
            </div>

            <div className="w-full md:w-[320px] border border-yellow-400 bg-blue-900 rounded-xl p-6 space-y-4">
              <CryptoFilter />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
