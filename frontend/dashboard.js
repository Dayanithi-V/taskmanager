const messageEl = document.getElementById("message");
const taskListEl = document.getElementById("task-list");
const priorityLabelEl = document.getElementById("priority-label");

function requireAuth() {
  if (!getToken()) {
    window.location.href = "login.html";
  }
}

requireAuth();

document.getElementById("logout-button").addEventListener("click", () => {
  logout();
});

document.getElementById("refresh-button").addEventListener("click", () => {
  loadTasks();
});

document.getElementById("ai-button").addEventListener("click", () => {
  loadPrioritizedTasks();
});

document.getElementById("task-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  clearMessage();

  const title = document.getElementById("title").value.trim();
  const description = document.getElementById("description").value.trim();
  const deadlineInput = document.getElementById("deadline").value;
  const importance = parseInt(document.getElementById("importance").value, 10);

  // Convert from local datetime to ISO (backend expects ISO 8601 string).
  const deadline = deadlineInput ? new Date(deadlineInput).toISOString() : null;

  try {
    const res = await fetch(API_BASE + "/tasks/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer " + getToken(),
      },
      body: JSON.stringify({ title, description, deadline, importance }),
    });

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Could not create task");
    }

    document.getElementById("task-form").reset();
    document.getElementById("importance").value = "3";
    showSuccess("Task added.");
    loadTasks();
  } catch (err) {
    showError(err.message);
  }
});

async function loadTasks() {
  clearMessage();
  priorityLabelEl.textContent = "Showing: most recent first";

  try {
    const res = await fetch(API_BASE + "/tasks/", {
      headers: {
        Authorization: "Bearer " + getToken(),
      },
    });

    if (res.status === 401) {
      logout();
      return;
    }

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Could not load tasks");
    }

    renderTasks(data);
  } catch (err) {
    showError(err.message);
  }
}

async function loadPrioritizedTasks() {
  clearMessage();
  priorityLabelEl.textContent = "Showing: AI-prioritized";

  try {
    const res = await fetch(API_BASE + "/ai/prioritize", {
      headers: {
        Authorization: "Bearer " + getToken(),
      },
    });

    if (res.status === 401) {
      logout();
      return;
    }

    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.detail || "Could not prioritize tasks");
    }

    renderTasks(data.tasks, true);
  } catch (err) {
    showError(err.message);
  }
}

async function deleteTask(id) {
  clearMessage();

  try {
    const res = await fetch(API_BASE + "/tasks/" + id, {
      method: "DELETE",
      headers: {
        Authorization: "Bearer " + getToken(),
      },
    });

    if (res.status === 401) {
      logout();
      return;
    }

    if (!res.ok && res.status !== 204) {
      const data = await res.json();
      throw new Error(data.detail || "Could not delete task");
    }

    showSuccess("Task deleted.");
    loadTasks();
  } catch (err) {
    showError(err.message);
  }
}

function renderTasks(tasks, showPriority = false) {
  taskListEl.innerHTML = "";

  if (!tasks || tasks.length === 0) {
    taskListEl.innerHTML = "<p style='color:#6b7280;font-size:0.9rem'>No tasks yet.</p>";
    return;
  }

  tasks.forEach((task) => {
    const div = document.createElement("div");
    div.className = "task-item";

    const header = document.createElement("div");
    header.className = "task-item-header";

    const titleSpan = document.createElement("span");
    titleSpan.className = "task-title";
    titleSpan.textContent = task.title;

    const importanceSpan = document.createElement("span");
    importanceSpan.className = "chip";
    importanceSpan.textContent = "Importance: " + task.importance;

    header.appendChild(titleSpan);
    header.appendChild(importanceSpan);

    const descP = document.createElement("div");
    descP.className = "task-desc";
    descP.textContent = task.description || "";

    const meta = document.createElement("div");
    meta.className = "task-meta";

    if (task.deadline) {
      const d = new Date(task.deadline);
      const deadlineChip = document.createElement("span");
      deadlineChip.className = "chip";
      deadlineChip.textContent = "Deadline: " + d.toLocaleString();
      meta.appendChild(deadlineChip);
    }

    const createdChip = document.createElement("span");
    createdChip.className = "chip";
    createdChip.textContent =
      "Created: " + new Date(task.created_at).toLocaleDateString();
    meta.appendChild(createdChip);

    if (showPriority && typeof task.priority_score === "number") {
      const pChip = document.createElement("span");
      pChip.className = "chip";
      pChip.textContent = "AI score: " + task.priority_score.toFixed(2);
      meta.appendChild(pChip);
    }

    const actions = document.createElement("div");
    actions.className = "task-actions";

    const delBtn = document.createElement("button");
    delBtn.className = "secondary";
    delBtn.textContent = "Delete";
    delBtn.addEventListener("click", () => deleteTask(task.id));

    actions.appendChild(delBtn);

    div.appendChild(header);
    div.appendChild(descP);
    div.appendChild(meta);
    div.appendChild(actions);

    taskListEl.appendChild(div);
  });
}

function clearMessage() {
  messageEl.textContent = "";
  messageEl.className = "";
}

function showError(msg) {
  messageEl.textContent = msg;
  messageEl.className = "error";
}

function showSuccess(msg) {
  messageEl.textContent = msg;
  messageEl.className = "success";
}

// Load tasks initially
loadTasks();

