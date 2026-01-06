import axios from "axios"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
})

// Add session ID to all requests
apiClient.interceptors.request.use((config) => {
  const sessionId = typeof window !== "undefined" ? localStorage.getItem("sessionId") : null

  if (sessionId) {
    config.headers["X-Session-ID"] = sessionId
  }

  return config
})

// Handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("sessionId")
    }
    return Promise.reject(error)
  },
)
