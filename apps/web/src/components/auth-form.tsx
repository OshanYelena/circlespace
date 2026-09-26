"use client";

import { ArrowRight, LoaderCircle } from "lucide-react";
import Link from "next/link";
import { FormEvent, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { api, ApiError } from "@/lib/api";

export function AuthForm({ mode }: { mode: "login" | "register" }) {
  const { completeAuth } = useAuth();
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setPending(true);
    setError("");
    const data = new FormData(event.currentTarget);
    try {
      const response = mode === "login"
        ? await api.login({ login: String(data.get("login")), password: String(data.get("password")) })
        : await api.register({
            email: String(data.get("email")),
            username: String(data.get("username")),
            display_name: String(data.get("display_name")),
            password: String(data.get("password")),
          });
      completeAuth(response);
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "We could not complete that request.");
    } finally {
      setPending(false);
    }
  }

  const login = mode === "login";
  return (
    <main className="auth-page">
      <Link className="brand auth-brand" href="/"><span className="brand-mark">C</span><span>CircleSpace</span></Link>
      <section className="auth-card">
        <div className="eyebrow">{login ? "Welcome back" : "Your circle starts here"}</div>
        <h1>{login ? "Step back into your space." : "Make a little room for what matters."}</h1>
        <p>{login ? "Your people and conversations are right where you left them." : "Create a profile and invite your favorite people in."}</p>
        <form onSubmit={submit}>
          {!login && (
            <div className="form-grid">
              <label>Display name<input name="display_name" autoComplete="name" required /></label>
              <label>Username<input name="username" autoComplete="username" minLength={3} pattern="[a-zA-Z0-9_]+" required /></label>
            </div>
          )}
          {login ? (
            <label>Email or username<input name="login" autoComplete="username" required autoFocus /></label>
          ) : (
            <label>Email address<input name="email" type="email" autoComplete="email" required /></label>
          )}
          <label>Password<input name="password" type="password" autoComplete={login ? "current-password" : "new-password"} minLength={8} required /></label>
          {error && <div className="form-error" role="alert">{error}</div>}
          <button className="button button-wide" disabled={pending}>
            {pending ? <LoaderCircle className="spin" size={19} /> : <>{login ? "Sign in" : "Create my space"} <ArrowRight size={18} /></>}
          </button>
        </form>
        <div className="auth-switch">
          {login ? "New to CircleSpace?" : "Already have a space?"}{" "}
          <Link href={login ? "/register" : "/login"}>{login ? "Create an account" : "Sign in"}</Link>
        </div>
      </section>
      <div className="orb orb-one" /><div className="grain" />
    </main>
  );
}

