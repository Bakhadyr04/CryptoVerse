export async function fetchCryptos(search: string, max_price: string, sort: string) {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    if (max_price) params.append('max_price', max_price);
    if (sort) params.append('sort', sort);

    const response = await fetch(`/api/cryptocurrencies/?${params.toString()}`);
    const data = await response.json();
    return data;
}
