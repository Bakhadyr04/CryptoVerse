'use client';

import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';

interface User {
  id: number;
  email: string;
  name: string;
}

interface Promotion {
  id: number;
  title: string;
  description: string;
}

interface UserPromotion {
  id: number;
  user: User;
  promotion: Promotion;
  participation_date: string;
}

export default function UserPromotionsPage() {
  const [data, setData] = useState<UserPromotion[]>([]);
  const [loading, setLoading] = useState(false);

  const [users, setUsers] = useState<User[]>([]);
  const [promos, setPromos] = useState<Promotion[]>([]);

  const [newUserId, setNewUserId] = useState('');
  const [newPromoId, setNewPromoId] = useState('');
  const [newDate, setNewDate] = useState('');

  const fetchData = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/user-promotions/');
      const json = await res.json();
      setData(Array.isArray(json) ? json : []);
    } catch (error) {
      console.error('Ошибка при получении данных:', error);
      setData([]);
    }
    setLoading(false);
  };

  const fetchUsersAndPromos = async () => {
    try {
      const [uRes, pRes] = await Promise.all([
        fetch('http://localhost:8000/api/users/'),
        fetch('http://localhost:8000/api/promotions/')
      ]);
      const [uData, pData] = await Promise.all([uRes.json(), pRes.json()]);
      setUsers(Array.isArray(uData) ? uData : []);
      setPromos(Array.isArray(pData) ? pData : []);
    } catch (error) {
      console.error('Ошибка при получении пользователей/акций:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Удалить участие?')) return;
    await fetch(`http://localhost:8000/api/user-promotions/${id}/`, {
      method: 'DELETE',
    });
    fetchData();
  };

  const handleEditDate = async (id: number, newDate: string) => {
    await fetch(`http://localhost:8000/api/user-promotions/${id}/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ participation_date: newDate + ':00Z' }),
    });
    fetchData();
  };

  const handleCreate = async () => {
    if (!newUserId || !newPromoId || !newDate)
      return alert('Заполните все поля');

    await fetch('http://localhost:8000/api/user-promotions/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user: Number(newUserId),
        promotion: Number(newPromoId),
        participation_date: newDate + ':00Z',
      }),
    });

    setNewUserId('');
    setNewPromoId('');
    setNewDate('');
    fetchData();
  };

  useEffect(() => {
    fetchData();
    fetchUsersAndPromos();
  }, []);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">Участия в акциях</h1>

      <Card>
        <CardContent className="flex flex-col md:flex-row gap-4">
          <select
            value={newUserId}
            onChange={(e) => setNewUserId(e.target.value)}
            className="p-2 rounded"
          >
            <option value="">Выберите пользователя</option>
            {Array.isArray(users) &&
              users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.email}
                </option>
              ))}
          </select>

          <select
            value={newPromoId}
            onChange={(e) => setNewPromoId(e.target.value)}
            className="p-2 rounded"
          >
            <option value="">Выберите акцию</option>
            {Array.isArray(promos) &&
              promos.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.title}
                </option>
              ))}
          </select>

          <Input
            type="datetime-local"
            value={newDate}
            onChange={(e) => setNewDate(e.target.value)}
          />
          <Button onClick={handleCreate}>Создать</Button>
        </CardContent>
      </Card>

      {loading ? (
        <p>Загрузка...</p>
      ) : (
        <Card>
          <CardContent>
            <table className="w-full table-auto border">
              <thead>
                <tr>
                  <th className="p-2 border">ID</th>
                  <th className="p-2 border">Email</th>
                  <th className="p-2 border">Акция</th>
                  <th className="p-2 border">Дата</th>
                  <th className="p-2 border">Действия</th>
                </tr>
              </thead>
              <tbody>
                {Array.isArray(data) &&
                  data.map((item) => (
                    <tr key={item.id} className="text-center">
                      <td className="border p-1">{item.id}</td>
                      <td className="border p-1">{item.user.email}</td>
                      <td className="border p-1">{item.promotion.title}</td>
                      <td className="border p-1">
                        <Input
                          type="datetime-local"
                          defaultValue={item.participation_date.slice(0, 16)}
                          onBlur={(e) =>
                            handleEditDate(item.id, e.target.value)
                          }
                        />
                      </td>
                      <td className="border p-1">
                        <Button onClick={() => handleDelete(item.id)}>
                          Удалить
                        </Button>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
