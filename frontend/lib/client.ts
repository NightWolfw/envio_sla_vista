"use client";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:5000/api";

type Method = "GET" | "POST" | "PUT" | "DELETE";

async function request<T>(path: string, method: Method, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json"
    },
    body: body ? JSON.stringify(body) : undefined
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Erro ${res.status}`);
  }

  if (res.status === 204) {
    return {} as T;
  }

  return res.json() as Promise<T>;
}

export const clientApi = {
  put: <T>(path: string, body?: unknown) => request<T>(path, "PUT", body),
  post: <T>(path: string, body?: unknown) => request<T>(path, "POST", body),
  delete: <T>(path: string, body?: unknown) => request<T>(path, "DELETE", body)
};
