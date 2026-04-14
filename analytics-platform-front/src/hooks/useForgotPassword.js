import api from "../services/api"

export function useForgotPassword() {
  const forgotPassword = async (email) => {
    const response = await api.post("/auth/forgot-password", { email })
    return response.data
  }

  const verifyToken = async (token) => {
    const response = await api.post("/auth/verify-reset-token", { token })
    return response.data
  }

  const resetPassword = async (token, newPassword) => {
    const response = await api.post("/auth/reset-password", {
      token,
      new_password: newPassword,
    })
    return response.data
  }

  return {
    forgotPassword,
    verifyToken,
    resetPassword,
  }
}
