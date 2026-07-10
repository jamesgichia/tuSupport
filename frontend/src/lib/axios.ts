import axios from 'axios';

const apiClient = axios.create({
	baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
	withCredentials: true,  // Critical — tells browser to send cookies on every request
});

// Attach access token to every outgoing request
apiClient.interceptors.request.use((config) => {
	const token = sessionStorage.getItem('access_token');
	if (token) {
		config.headers.Authorization = `Bearer ${token}`;
	}
	return config;
});

// On 401 — silently refresh, retry original request
apiClient.interceptors.response.use(
	(response) => response,
	async (error) => {
		const original = error.config;

		if (error.response?.status === 401 && !original._retry) {
			original._retry = true;

			try {
				// Empty POST body — browser sends the HttpOnly cookie automatically
				const refreshResponse = await axios.post(
					'http://localhost:8000/api/v1/auth/token/refresh/',
					{},
					{ withCredentials: true }  // Must be set here too — this is a raw axios call, not apiClient
				);

				const newAccess = refreshResponse.data.access;
				sessionStorage.setItem('access_token', newAccess);
				original.headers.Authorization = `Bearer ${newAccess}`;

				return apiClient(original);
			} catch {
				sessionStorage.clear();
				window.location.href = '/login';
			}
		}

		return Promise.reject(error);
	}
);

export default apiClient;
