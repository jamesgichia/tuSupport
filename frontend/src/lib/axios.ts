import axios from "axios";

// One configured Axios instance used everywhere in the app.
// No component should ever call axios directly — always import this.
const apiClient = axios.create({
	baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
	headers: {
		"Content-Type": "application/json",
	},
});

// ─── Request interceptor ──────────────────────────────────────────
// Automatically attaches the access token to every outgoing request.
// No component needs to manually add Authorization headers.
apiClient.interceptors.request.use(
	(config) => {
		const token = sessionStorage.getItem("access_token");
		if (token) {
			config.headers.Authorization = `Bearer ${token}`;
		}
		return config;
	},
	(error) => Promise.reject(error)
);

// ─── Response interceptor ─────────────────────────────────────────
// Watches every response coming back from the backend.
// On 401 → silently refreshes the access token → retries original request.
// If refresh itself fails → clears session → redirects to login.
apiClient.interceptors.response.use(
	(response) => response, // Happy path — pass response through untouched

	async (error) => {
		const originalRequest = error.config;

		// Only handle 401s we haven't already retried.
		// _retry flag prevents an infinite loop if refresh endpoint itself returns 401.
		if (error.response?.status === 401 && !originalRequest._retry) {
			originalRequest._retry = true;

			const refreshToken = sessionStorage.getItem("refresh_token");

			if (!refreshToken) {
				// No refresh token available — session is already dead
				clearSession();
				redirectToLogin();
				return Promise.reject(error);
			}

			try {
				// Use a plain axios call here — NOT apiClient.
				// apiClient would trigger this interceptor again → infinite loop.
				const response = await axios.post(
					`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/v1/auth/token/refresh/`,
					{ refresh: refreshToken }
				);

				const newAccessToken = response.data.access;
				sessionStorage.setItem("access_token", newAccessToken);

				// Backend has ROTATE_REFRESH_TOKENS=True — it issues a new refresh token too.
				// Store it so the old one isn't reused.
				if (response.data.refresh) {
					sessionStorage.setItem("refresh_token", response.data.refresh);
				}

				// Retry the original request with the fresh access token
				originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
				return apiClient(originalRequest);

			} catch (refreshError) {
				// Refresh token is expired or revoked — session is genuinely dead
				clearSession();
				redirectToLogin();
				return Promise.reject(refreshError);
			}
		}

		// All other errors (403, 404, 500) — pass through untouched
		return Promise.reject(error);
	}
);

// ─── Helpers ──────────────────────────────────────────────────────
function clearSession() {
	sessionStorage.removeItem("access_token");
	sessionStorage.removeItem("refresh_token");
	sessionStorage.removeItem("organizations");
}

function redirectToLogin() {
	window.location.href = "/login";
}

export default apiClient;
