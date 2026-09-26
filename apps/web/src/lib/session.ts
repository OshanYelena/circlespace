import type { User } from "@/lib/types";

export const SESSION_KEY = "circlespace.session";

export type Session = { token: string; user: User };

export function readSession(storage: Pick<Storage, "getItem">): Session | null {
  const value = storage.getItem(SESSION_KEY);
  if (!value) return null;
  try {
    const parsed = JSON.parse(value) as Session;
    return parsed.token && parsed.user?.id ? parsed : null;
  } catch {
    return null;
  }
}

export function writeSession(storage: Pick<Storage, "setItem">, session: Session): void {
  storage.setItem(SESSION_KEY, JSON.stringify(session));
}

