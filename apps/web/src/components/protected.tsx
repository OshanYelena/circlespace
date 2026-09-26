"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "@/components/auth-provider";

export function Protected({ children }: { children: React.ReactNode }) {
  const { user, ready } = useAuth();
  const router = useRouter();
  useEffect(() => {
    if (ready && !user) router.replace("/login");
  }, [ready, router, user]);
  if (!ready || !user) return <div className="page-loader">Preparing your space…</div>;
  return <>{children}</>;
}

