import { NextApiRequest, NextApiResponse } from "next";

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  try {
    const response = await fetch("http://localhost:8000/api/cryptocurrencies/");
    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    console.error("Ошибка при получении данных:", error);
    return res.status(500).json({ error: "Ошибка сервера" });
  }
}
