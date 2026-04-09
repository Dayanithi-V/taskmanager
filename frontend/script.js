const API_BASE =
  "https://taskmanager-api-123-cbcdg6gcc8eqhhb0.eastasia-01.azurewebsites.net";

const authView = document.getElementById("auth-view");
const dashboardView = document.getElementById("dashboard-view");
const loadingEl = document.getElementById("loading");
const toastEl = document.getElementById("toast");
const taskListEl = document.getElementById("task-list");
const modeLabelEl = document.getElementById("mode-label");

const loginForm = document.getElementById("login-form");
const registerForm = document.getElementById("register-form");
const taskForm = document.getElementById("task-form");

const loginTabBtn = document.getElementById("show-login");
const registerTabBtn = document.getElementById("show-register");

const refreshBtn = document.getElementById("refresh-btn");
const prioritizeBtn = document.getElementById("prioritize-btn");
const logoutBtn = document.getElementById("logout-btn");

let prioritizedMode = false;

function setLoading(show) {
  loadingEl.classList.toggle("hidden", !show);
}

function showToast(type, message) {
  toastEl.textContent = message;
  toastEl.className = `toast ${type}`;
  setTimeout(() => {
    toastEl.className = "toast hidden";
  }, 2600);
}

function getToken() {
  return localStorage.getItem("token");
}

function setToken(token) {
  localStorage.setItem("token", token);
}

function clearToken() {
  localStorage.removeItem("token");
}

function switchAuthTab(tab) {
  const isLogin = tab === "login";
  loginForm.classList.toggle("hidden", !isLogin);
  registerForm.classList.toggle("hidden", isLogin);
  loginTabBtn.classList.toggle("active", isLogin);
  registerTabBtn.classList.toggle("active", !isLogin);
}

function switchView(loggedIn) {
  authView.classList.toggle("hidden", loggedIn);
  dashboardView.classList.toggle("hidden", !loggedIn);
}

function authHeaders() {
  return {
    Authorization: "Bearer " + getToken(),
  };
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function formatDeadline(deadline) {
  if (!deadline) return "No deadline";
  return new Date(deadline).toLocaleString();
}

function renderTasks(tasks, isPrioritized = false) {
  taskListEl.innerHTML = "";

  if (!tasks || tasks.length === 0) {
    taskListEl.innerHTML = `<div class="task-card"><p class="subtitle">No tasks yet.</p></div>`;
    return;
  }

  tasks.forEach((task, index) => {
    const topPriority = isPrioritized && index < 2;
    const scoreChip =
      isPrioritized && typeof task.priority_score === "number"
        ? `<span class="chip">AI Score: ${task.priority_score.toFixed(2)}</span>`
        : "";

    const html = `
      <article class="task-card ${topPriority ? "top-priority" : ""}">
        <div class="task-row">
          <h4 class="task-title">${escapeHtml(task.title)}</h4>
          <button class="btn-delete" data-delete="${task.id}">Delete</button>
        </div>
        <div class="chips">
          <span class="chip">Deadline: ${escapeHtml(formatDeadline(task.deadline))}</span>
          <span class="chip">Importance: ${task.importance}</span>
          ${scoreChip}
        </div>
      </article>
    `;
    taskListEl.insertAdjacentHTML("beforeend", html);
  });

  document.querySelectorAll("[data-delete]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const taskId = btn.getAttribute("data-delete");
      await deleteTask(taskId);
    });
  });
}

async function registerUser(email, password) {
  setLoading(true);
  try {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Registration failed");
    showToast("success", "Account created. Please login.");
    switchAuthTab("login");
  } catch (error) {
    showToast("error", error.message);
  } finally {
    setLoading(false);
  }
}

async function loginUser(email, password) {
  setLoading(true);
  try {
    const body = new URLSearchParams();
    body.append("username", email);
    body.append("password", password);

    const res = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Login failed");

    setToken(data.access_token);
    switchView(true);
    await loadTasks();
    showToast("success", "Logged in successfully.");
  } catch (error) {
    showToast("error", error.message);
  } finally {
    setLoading(false);
  }
}

async function loadTasks() {
  setLoading(true);
  prioritizedMode = false;
  modeLabelEl.textContent = "Recent order";
  try {
    const res = await fetch(`${API_BASE}/tasks/`, { headers: authHeaders() });
    if (res.status === 401) return logout();
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to load tasks");
    renderTasks(data, false);
  } catch (error) {
    showToast("error", error.message);
  } finally {
    setLoading(false);
  }
}

async function loadPrioritized() {
  setLoading(true);
  prioritizedMode = true;
  modeLabelEl.textContent = "AI prioritized";
  try {
    const res = await fetch(`${API_BASE}/ai/prioritize`, { headers: authHeaders() });
    if (res.status === 401) return logout();
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to prioritize tasks");
    renderTasks(data.tasks, true);
    showToast("success", "Tasks prioritized. Top tasks are highlighted.");
  } catch (error) {
    showToast("error", error.message);
  } finally {
    setLoading(false);
  }
}

async function createTask(payload) {
  setLoading(true);
  try {
    const res = await fetch(`${API_BASE}/tasks/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || "Failed to create task");
    showToast("success", "Task added.");
    taskForm.reset();
    document.getElementById("task-importance").value = "3";
    if (prioritizedMode) {
      await loadPrioritized();
    } else {
      await loadTasks();
    }
  } catch (error) {
    showToast("error", error.message);
  } finally {
    setLoading(false);
  }
}

async function deleteTask(taskId) {
  setLoading(true);
  try {
    const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
      method: "DELETE",
      headers: authHeaders(),
    });
    if (res.status === 401) return logout();
    if (!res.ok && res.status !== 204) {
      const data = await res.json();
      throw new Error(data.detail || "Delete failed");
    }
    showToast("success", "Task deleted.");
    if (prioritizedMode) {
      await loadPrioritized();
    } else {
      await loadTasks();
    }
  } catch (error) {
    showToast("error", error.message);
  } finally {
    setLoading(false);
  }
}

function logout() {
  clearToken();
  switchView(false);
  switchAuthTab("login");
}

// Event bindings
loginTabBtn.addEventListener("click", () => switchAuthTab("login"));
registerTabBtn.addEventListener("click", () => switchAuthTab("register"));

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("login-email").value.trim();
  const password = document.getElementById("login-password").value;
  await loginUser(email, password);
});

registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("register-email").value.trim();
  const password = document.getElementById("register-password").value;
  await registerUser(email, password);
});

taskForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const title = document.getElementById("task-title").value.trim();
  const description = document.getElementById("task-description").value.trim();
  const deadlineInput = document.getElementById("task-deadline").value;
  const importance = parseInt(document.getElementById("task-importance").value, 10);
  const deadline = deadlineInput ? new Date(deadlineInput).toISOString() : null;

  await createTask({ title, description, deadline, importance });
});

refreshBtn.addEventListener("click", loadTasks);
prioritizeBtn.addEventListener("click", loadPrioritized);
logoutBtn.addEventListener("click", logout);

// Startup state
if (getToken()) {
  switchView(true);
  loadTasks();
} else {
  switchView(false);
  switchAuthTab("login");
}

