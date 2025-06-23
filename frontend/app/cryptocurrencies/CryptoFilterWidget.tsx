'use client';

import React, { useState } from 'react';
import { useSearchParams, useRouter, usePathname } from 'next/navigation';

export default function CryptoFilter() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const [search, setSearch] = useState(searchParams?.get('search') ?? '');
  const [maxPrice, setMaxPrice] = useState(searchParams?.get('max_price') ?? '');
  const [sort, setSort] = useState(searchParams?.get('sort') ?? 'desc');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // просто собираем строку query вручную:
    let query = [];

    if (search) query.push(`search=${encodeURIComponent(search)}`);
    if (maxPrice) query.push(`max_price=${encodeURIComponent(maxPrice)}`);
    if (sort) query.push(`sort=${encodeURIComponent(sort)}`);

    const queryString = query.length > 0 ? `?${query.join('&')}` : '';

    router.push(`${pathname}${queryString}`, { scroll: false });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
    <div>
        <label className="block mb-1 text-lg font-medium">Поиск по названию</label>
        <input
          type="text"
          placeholder="Bitcoin..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="text-black w-full h-10 rounded-md px-2"
        />
    </div>

    <div>
        <label className="block mb-1 text-lg font-medium">Максимальная цена</label>
        <input
          type="number"
          placeholder="1000"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
          className="text-black w-full h-10 rounded-md px-2"
        />
    </div>

    <div>
        <label className="block mb-1 text-lg font-medium">Сортировка</label>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="text-black w-full h-10 rounded-md px-2"
        >
          <option value="desc">По убыванию</option>
          <option value="asc">По возрастанию</option>
        </select>
    </div>

    <button type="submit" className="bg-yellow-400 text-lg text-black w-full h-10 rounded-md font-semibold">
        Применить
    </button>
    </form>
  );
}
