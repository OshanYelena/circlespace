"use client";

import { useRouter } from "next/navigation";
import { createContext, useContext, useEffect, useMemo, useState } from "react";

import { api } from "@/lib/api";
import { readSession, SESSION_KEY, writeSession, type Session } from "@/lib/session";
import type { AuthResponse, User } from "@/lib/types";

type AuthContextValue = {
  token: string | null;
  user: User | null;
  ready: boolean;
  completeAuth: (response: AuthResponse) => void;
  updateUser: (user: User) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const stored = readSession(window.localStorage);
    queueMicrotask(() => {
      setSession(stored);
      setReady(true);
    });
    if (stored) {
      api.me(stored.token)
        .then((user) => {
          const refreshed = { ...stored, user };
          setSession(refreshed);
          writeSession(window.localStorage, refreshed);
        })
        .catch(() => {
          window.localStorage.removeItem(SESSION_KEY);
          setSession(null);
        });
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      token: session?.token ?? null,
      user: session?.user ?? null,
      ready,
      completeAuth(response) {
        const next = { token: response.access_token, user: response.user };
        setSession(next);
        writeSession(window.localStorage, next);
        router.push("/feed");
      },
      updateUser(user) {
        if (!session) return;
        const next = { ...session, user };
        setSession(next);
        writeSession(window.localStorage, next);
      },
      logout() {
        window.localStorage.removeItem(SESSION_KEY);
        setSession(null);
        router.push("/");
      },
    }),
    [ready, router, session],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}
