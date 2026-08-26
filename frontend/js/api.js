const TOKEN_KEY = "budgy_token";

const SUPPORTED_CURRENCIES = ["TRY", "EUR", "USD", "GBP", "CHF"];

const TX_TYPE_LABELS = {
  deposit: { label: "Ekleme", badge: "badge-deposit", icon: "💰" },
  withdrawal: { label: "Çıkarma", badge: "badge-withdrawal", icon: "➖" },
  saving: { label: "Tasarruf", badge: "badge-saving", icon: "🍃" },
};

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function isLoggedIn() {
  return !!getToken();
}

// Decodes the JWT payload client-side. Not a security check — the backend
// still verifies the signature on every request.

// Reads the `uid` claim so the frontend can show owner-only
// controls (complete / delete) without an extra round trip.
function currentUserId() {
  const token = getToken();
  if (!token) return null;
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json).uid ?? null;
  } catch {
    return null;
  }
}

// Reads the `uname` claim for display purposes (topbar greeting etc).
function currentUsername() {
  const token = getToken();
  if (!token) return null;
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json).uname || null;
  } catch {
    return null;
  }
}

async function apiFetch(path, { method = "GET", body, auth = false, form = false } = {}) {
  const headers = {};
  if (body && !form) headers["Content-Type"] = "application/json";
  if (form) headers["Content-Type"] = "application/x-www-form-urlencoded";
  if (auth) headers["Authorization"] = `Bearer ${getToken()}`;

  const res = await fetch(path, {
    method,
    headers,
    body: form ? body : body ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && auth) {
    clearToken();
    window.location.href = "login.html";
    return;
  }

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg).join(", ")
      : detail || "Bir hata oluştu";
    throw new Error(message);
  }

  return data;
}

const api = {
  register: (email, username, password) =>
    apiFetch("/auth/register", { method: "POST", body: { email, username, password } }),

  login: (email, password) =>
    apiFetch("/auth/login", {
      method: "POST",
      form: true,
      body: new URLSearchParams({ username: email, password }).toString(),
    }),

  listBudgets: () => apiFetch("/budgets/", { auth: true }),

  listCompletedBudgets: () => apiFetch("/budgets/completed", { auth: true }),

  getBudget: (budgetId) => apiFetch(`/budgets/${budgetId}`, { auth: true }),

  createBudget: (title, target_amount, base_currency) =>
    apiFetch("/budgets/", { method: "POST", auth: true, body: { title, target_amount, base_currency } }),

  joinBudget: ({ budget_id, invite_code }) =>
    apiFetch("/budgets/join", { method: "POST", auth: true, body: { budget_id, invite_code } }),

  setBudgetCompleted: (budgetId, isCompleted) =>
    apiFetch(`/budgets/${budgetId}`, { method: "PATCH", auth: true, body: { is_completed: isCompleted } }),

  deleteBudget: (budgetId) => apiFetch(`/budgets/${budgetId}`, { method: "DELETE", auth: true }),

  addTransaction: (budgetId, { original_amount, original_currency, type, note }) =>
    apiFetch(`/budgets/${budgetId}/transactions/`, {
      method: "POST",
      auth: true,
      body: { original_amount, original_currency, type, note },
    }),

  listTransactions: (budgetId) => apiFetch(`/budgets/${budgetId}/transactions/`, { auth: true }),
};
