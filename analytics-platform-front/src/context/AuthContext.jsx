import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
/* eslint-disable react-refresh/only-export-components */
import api, {
  setAccessToken as setApiAccessToken,
  setAuthFailureHandler,
  setAuthRefreshHandler,
} from "../services/api";

const AuthContext = createContext();
const ACCESS_TOKEN_STORAGE_KEY = "digmaco_access_token";
let refreshRequest = null;

export const AuthProvider = ({ children }) => {
  const [access_token, setAccessToken] = useState(null);
  const [role, setRole] = useState(null);
  const [full_name, setFullName] = useState(null);
  const [userId, setUserId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const clearLocalAuth = useCallback(() => {
    sessionStorage.removeItem(ACCESS_TOKEN_STORAGE_KEY);
    localStorage.removeItem("role");
    localStorage.removeItem("full_name");
    localStorage.removeItem("user_id");
    setAccessToken(null);
    setApiAccessToken(null);
    setRole(null);
    setFullName(null);
    setUserId(null);
  }, []);

  const refreshAccessToken = useCallback(async ({ clearOnUnauthorized = true } = {}) => {
    if (refreshRequest) return refreshRequest;

    refreshRequest = (async () => {
      try {
        const response = await api.post(
          "/auth/refresh",
          {},
          { skipAuthRefresh: true },
        );
        const {
          access_token: token,
          role: userRole,
          full_name: userName,
          user_id: uid,
        } = response.data;

        setAccessToken(token);
        setApiAccessToken(token);
        sessionStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, token);
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
      } catch (err) {
        const status = err?.response?.status;
        if (
          (status === 401 || status === 403) &&
          clearOnUnauthorized
        ) {
          clearLocalAuth();
        }
        return null;
      } finally {
        refreshRequest = null;
      }
    })();

    return refreshRequest;
  }, [clearLocalAuth]);

  useEffect(() => {
    setAuthRefreshHandler(() => refreshAccessToken());
    setAuthFailureHandler(clearLocalAuth);

    return () => {
      setAuthRefreshHandler(null);
      setAuthFailureHandler(null);
    };
  }, [clearLocalAuth, refreshAccessToken]);

  useEffect(() => {
    const userRole = localStorage.getItem("role");
    const userName = localStorage.getItem("full_name");
    const uid = localStorage.getItem("user_id");
    const storedToken = sessionStorage.getItem(ACCESS_TOKEN_STORAGE_KEY);

    if (userRole) setRole(userRole);
    if (userName) setFullName(userName);
    if (uid) setUserId(uid);
    if (storedToken) {
      setAccessToken(storedToken);
      setApiAccessToken(storedToken);
    }

    const bootstrap = async () => {
      if (storedToken) {
        setIsLoading(false);
        refreshAccessToken({ clearOnUnauthorized: false });
        return;
      }

      if (userRole) {
        await refreshAccessToken({ clearOnUnauthorized: true });
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
    sessionStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, token);
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
      await api.post("/auth/logout", {}, { skipAuthRefresh: true });
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
