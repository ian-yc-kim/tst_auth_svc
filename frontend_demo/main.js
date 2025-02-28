document.addEventListener('DOMContentLoaded', function() {
  const feedbackEl = document.getElementById('feedback');

  function displayFeedback(message, isError = false) {
    feedbackEl.textContent = message;
    feedbackEl.style.color = isError ? 'red' : 'green';
  }

  // Registration Form Event
  const registerForm = document.getElementById('registerForm');
  registerForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('reg-username').value.trim();
    const email = document.getElementById('reg-email').value.trim();
    const password = document.getElementById('reg-password').value;

    if (!username || !email || !password) {
      displayFeedback('All fields are required for registration', true);
      return;
    }
    // Simple email validation
    if (!email.includes('@') || !email.includes('.')) {
      displayFeedback('Invalid email format', true);
      return;
    }

    try {
      const response = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
      });
      const data = await response.json();
      if (response.ok) {
        displayFeedback(data.message);
      } else {
        displayFeedback(data.detail || 'Registration failed', true);
      }
    } catch (error) {
      displayFeedback('Error during registration', true);
    }
  });

  // Login Form Event
  const loginForm = document.getElementById('loginForm');
  loginForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value;

    if (!username || !password) {
      displayFeedback('Both fields required for login', true);
      return;
    }

    try {
      const response = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      const data = await response.json();
      if (response.ok) {
        displayFeedback(data.message || 'Login successful');
        // Optionally, store session token for logout
        if (data.session_token) {
          localStorage.setItem('session_token', data.session_token);
        }
      } else {
        displayFeedback(data.detail || 'Login failed', true);
      }
    } catch (error) {
      displayFeedback('Error during login', true);
    }
  });

  // Password Reset Request Form Event
  const passwordResetRequestForm = document.getElementById('passwordResetRequestForm');
  passwordResetRequestForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const identifier = document.getElementById('reset-identifier').value.trim();
    if (!identifier) {
      displayFeedback('Please enter username or email for password reset', true);
      return;
    }
    try {
      const response = await fetch('/password-reset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ identifier })
      });
      const data = await response.json();
      if (response.ok) {
        displayFeedback(data.message);
      } else {
        displayFeedback(data.detail || 'Password reset request failed', true);
      }
    } catch (error) {
      displayFeedback('Error during password reset request', true);
    }
  });

  // Password Update Form Event
  const passwordUpdateForm = document.getElementById('passwordUpdateForm');
  passwordUpdateForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const reset_token = document.getElementById('update-reset-token').value.trim();
    const new_password = document.getElementById('update-new-password').value;
    if (!reset_token || !new_password) {
      displayFeedback('Both reset token and new password are required', true);
      return;
    }
    try {
      const response = await fetch('/password-update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reset_token, new_password })
      });
      const data = await response.json();
      if (response.ok) {
        displayFeedback(data.message);
      } else {
        displayFeedback(data.detail || 'Password update failed', true);
      }
    } catch (error) {
      displayFeedback('Error during password update', true);
    }
  });

  // Logout Button Event
  const logoutButton = document.getElementById('logoutButton');
  logoutButton.addEventListener('click', async function() {
    const session_token = localStorage.getItem('session_token') || '';
    if (!session_token) {
      displayFeedback('No session token found', true);
      return;
    }
    try {
      const response = await fetch('/logout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_token })
      });
      const data = await response.json();
      if (response.ok) {
        displayFeedback(data.message);
        localStorage.removeItem('session_token');
      } else {
        displayFeedback(data.detail || 'Logout failed', true);
      }
    } catch (error) {
      displayFeedback('Error during logout', true);
    }
  });

  // Google OAuth2 Button Event
  const googleOAuthButton = document.getElementById('googleOAuthButton');
  googleOAuthButton.addEventListener('click', function() {
    window.location.href = '/auth/google/google-login';
  });
});
