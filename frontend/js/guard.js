function requireAuth() {
  if (!isLoggedIn()) window.location.href = "login.html";
}

function redirectIfAuthed() {
  if (isLoggedIn()) window.location.href = "dashboard.html";
}
