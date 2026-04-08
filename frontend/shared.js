// Change this if your backend runs on a different host/port.
// For example, if you run uvicorn on 127.0.0.1:8000:
const API_BASE = "http://127.0.0.1:8000";

/**
 * Helper to get the stored JWT token.
 */
function getToken() {
  return localStorage.getItem("token");
}

/**
 * Helper to remove JWT token and redirect to the login page.
 */
function logout() {
  localStorage.removeItem("token");
  window.location.href = "login.html";
}

