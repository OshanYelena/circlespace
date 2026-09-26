"use client";

import { Bell, Home, LogOut, Search, Users } from "lucide-react";
import Link from "next/link";

import { Avatar } from "@/components/avatar";
import { useAuth } from "@/components/auth-provider";

export function AppNav() {
  const { user, logout } = useAuth();
  if (!user) return null;
  return (
    <header className="app-nav">
      <div className="nav-inner">
        <Link className="brand" href="/feed" aria-label="CircleSpace home">
          <span className="brand-mark">C</span>
          <span>CircleSpace</span>
        </Link>
        <nav aria-label="Main navigation">
          <Link href="/feed"><Home size={19} /> Feed</Link>
          <Link href="/friends"><Users size={19} /> Friends</Link>
          <Link href={`/profile/${user.username}`}><Search size={19} /> Profile</Link>
        </nav>
        <div className="nav-actions">
          <button className="icon-button" aria-label="Notifications"><Bell size={19} /></button>
          <Link className="profile-chip" href={`/profile/${user.username}`}>
            <Avatar name={user.profile.display_name} src={user.profile.avatar_url} size="sm" />
            <span>{user.profile.display_name}</span>
          </Link>
          <button className="icon-button" onClick={logout} aria-label="Sign out"><LogOut size={18} /></button>
        </div>
      </div>
    </header>
  );
}

