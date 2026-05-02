import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [access_token, setAccessToken] = useState(null);
  const [role, setRole] = useState(null);
  const [full_name, setFullName] = useState(null);
  const [userId, setUserId] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialiser depuis localStorage au montage
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    const userRole = localStorage.getItem("role");
    const userName = localStorage.getItem("full_name");
    const uid = localStorage.getItem("user_id");

    if (token) {
      setAccessToken(token);
      setRole(userRole);
      setFullName(userName);
      setUserId(uid);
    }
    setIsLoading(false);
  }, []);

  const login = (token, userRole, userName, uid) => {
    localStorage.setItem("access_token", token);
    localStorage.setItem("role", userRole);
    localStorage.setItem("full_name", userName);
    localStorage.setItem("user_id", uid);

    setAccessToken(token);
    setRole(userRole);
    setFullName(userName);
    setUserId(uid);
  };

  const updateProfile = (userName) => {
    localStorage.setItem("full_name", userName);
    setFullName(userName);
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("role");
    localStorage.removeItem("full_name");
    localStorage.removeItem("user_id");

    setAccessToken(null);
    setRole(null);
    setFullName(null);
    setUserId(null);
  };

  const isAdmin = () => {
    return role === "admin";
  };

  const value = {
    access_token,
    role,
    full_name,
    userId,
    isLoading,
    login,
    logout,
    updateProfile,
    isAdmin,
    isAuthenticated: !!access_token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth doit être utilisé dans un AuthProvider");
  }
  return context;
};
