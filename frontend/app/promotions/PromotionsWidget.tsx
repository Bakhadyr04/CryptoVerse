'use client';

import React, { useEffect, useState } from 'react';

interface Promotion {
  id: number;
  title: string;
  description: string;
  image: string | null;
  start_date: string;
  end_date: string | null;
}

export default function PromotionsWidget(): JSX.Element {
  const [promotions, setPromotions] = useState<Promotion[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 10;

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(`http://localhost:8000/promotions-api/?page=${currentPage}`);
      const data = await response.json();
      setPromotions(data.promotions);
      setTotalPages(data.total_pages);
    };

    fetchData();
  }, [currentPage]);

  return (
    <div className="w-full flex flex-col items-center mt-16">
      <h2 className="text-4xl md:text-6xl font-bold text-white mb-10 mt-10">Промоакции</h2>
      <div className="flex justify-center w-full">
        <div className="w-full max-w-[1300px] p-4 border rounded-2xl border-yellow-400 bg-blue-900 text-white">
          <table className="w-full table-auto border-collapse text-lg">
            <thead>
              <tr className="text-yellow-400 border-b text-xl border-yellow-400">
                <th className="py-2">№</th>
                <th className="py-2">Название</th>
                <th className="py-2">Описание</th>
                <th className="py-2">Изображение</th>
                <th className="py-2">Начало</th>
                <th className="py-2">Окончание</th>
              </tr>
            </thead>
            <tbody>
              {promotions.map((promo, i) => (
                <tr key={promo.id} className="border-b border-gray-700">
                  <td className="py-2 text-center">{(currentPage - 1) * pageSize + i + 1}</td>
                  <td className="py-2 text-center">{promo.title}</td>
                  <td className="py-2 text-center">{promo.description}</td>
                  <td className="py-2 text-center">
                    {promo.image ? (
                      <img
                        src={`http://localhost:8000${promo.image}`}
                        alt={promo.title}
                        className="h-16 mx-auto rounded"
                      />
                    ) : (
                      'Нет изображения'
                    )}
                  </td>
                  <td className="py-2 text-center">{promo.start_date}</td>
                  <td className="py-2 text-center">{promo.end_date ?? '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Пагинация */}
          <div className="flex justify-center items-center gap-2 mt-6">
            {Array.from({ length: totalPages }, (_, i) => (
              <button
                key={i}
                onClick={() => setCurrentPage(i + 1)}
                className={`w-8 h-8 rounded border ${
                  currentPage === i + 1
                    ? 'bg-yellow-400 text-black'
                    : 'border-white text-white'
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
