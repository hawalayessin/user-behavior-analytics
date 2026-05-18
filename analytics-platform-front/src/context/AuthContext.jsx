import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import api, { setAccessToken as setApiAccessToken } from "../services/api";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [access_token, setAccessToken] = useState(null);
  const [role, setRole] = useState(null);
  const [full_name, setFullName] = useState(null);
  const [userId, setUserId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const clearLocalAuth = useCallback(() => {
    localStorage.removeItem("role");
    localStorage.removeItem("full_name");
    localStorage.removeItem("user_id");
    setAccessToken(null);
    setApiAccessToken(null);
    setRole(null);
    setFullName(null);
    setUserId(null);
  }, []);

  const refreshAccessToken = useCallback(async () => {
    try {
      const response = await api.post("/auth/refresh", {});
      const { access_token: token, role: userRole, full_name: userName, user_id: uid } = response.data;

      setAccessToken(token);
      setApiAccessToken(token);
      if (userRole) {
        localStorage.setItem("role", userRole);
        setRole(userRole);
      }
      if (userName) {
        localStorage.setItem("full_name", userName);
        setFullName(userName);
      }
      if (uid) {
        localStorage.setItem("user_id", uid);
        setUserId(uid);
      }
      return token;
    } catch {
      clearLocalAuth();
      return null;
    }
  }, [clearLocalAuth]);

  useEffect(() => {
    const userRole = localStorage.getItem("role");
    const userName = localStorage.getItem("full_name");
    const uid = localStorage.getItem("user_id");

    if (userRole) setRole(userRole);
    if (userName) setFullName(userName);
    if (uid) setUserId(uid);

    const bootstrap = async () => {
      if (userRole) {
        await refreshAccessToken();
      }
      setIsLoading(false);
    };

    bootstrap();
  }, [refreshAccessToken]);

  const login = (token, userRole, userName, uid) => {
    localStorage.setItem("role", userRole);
    localStorage.setItem("full_name", userName);
    localStorage.setItem("user_id", uid);

    setAccessToken(token);
    setApiAccessToken(token);
    setRole(userRole);
    setFullName(userName);
    setUserId(uid);
  };

  const updateProfile = (userName) => {
    localStorage.setItem("full_name", userName);
    setFullName(userName);
  };

  const logout = async () => {
    try {
      await api.post("/auth/logout", {});
    } catch {
      // best effort logout
    }
    clearLocalAuth();
  };

  const isAdmin = () => role === "admin";

  const value = {
    access_token,
    role,
    full_name,
    userId,
    isLoading,
    login,
    logout,
    refreshAccessToken,
    updateProfile,
    isAdmin,
    isAuthenticated: !!access_token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside an AuthProvider");
  }
  return context;
};
