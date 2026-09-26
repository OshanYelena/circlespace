"use client";

import { Edit3, MapPin, UserPlus } from "lucide-react";
import { FormEvent, use, useEffect, useState } from "react";

import { Avatar } from "@/components/avatar";
import { useAuth } from "@/components/auth-provider";
import { PostCard } from "@/components/post-card";
import { api, ApiError } from "@/lib/api";
import type { Post, PublicUser } from "@/lib/types";

export default function ProfilePage({ params }: { params: Promise<{ username: string }> }) {
  const { username } = use(params);
  const { token, user, updateUser } = useAuth();
  const [profile, setProfile] = useState<PublicUser | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [editing, setEditing] = useState(false);
  const [message, setMessage] = useState("");
  const ownProfile = user?.username === username;

  useEffect(() => {
    if (!token) return;
    Promise.all([api.profile(username, token), api.userPosts(token, username)])
      .then(([nextProfile, nextPosts]) => { setProfile(nextProfile); setPosts(nextPosts); })
      .catch(() => setMessage("This profile could not be loaded."));
  }, [token, username]);

  async function saveProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    const data = new FormData(event.currentTarget);
    try {
      const updated = await api.updateProfile(token, {
        display_name: String(data.get("display_name")),
        bio: String(data.get("bio")),
        location: String(data.get("location")),
        avatar_url: String(data.get("avatar_url")) || null,
      });
      updateUser(updated);
      setProfile(updated);
      setEditing(false);
    } catch (reason) {
      setMessage(reason instanceof ApiError ? reason.message : "Could not update your profile.");
    }
  }

  async function addFriend() {
    if (!token) return;
    try {
      await api.sendRequest(token, username);
      setMessage("Friend request sent.");
    } catch (reason) {
      setMessage(reason instanceof ApiError ? reason.message : "Could not send a friend request.");
    }
  }

  if (!profile) return <div className="empty-state">{message || "Opening this profile…"}</div>;
  return (
    <div className="profile-page">
      <section className="profile-hero card">
        <div className="profile-wash" />
        <div className="profile-details">
          <Avatar name={profile.profile.display_name} src={profile.profile.avatar_url} size="lg" />
          <div><h1>{profile.profile.display_name}</h1><span>@{profile.username}</span>{profile.profile.bio && <p>{profile.profile.bio}</p>}{profile.profile.location && <small><MapPin size={15} /> {profile.profile.location}</small>}</div>
          {ownProfile ? <button className="button button-ghost" onClick={() => setEditing((value) => !value)}><Edit3 size={17} /> Edit profile</button> : <button className="button" onClick={addFriend}><UserPlus size={17} /> Add friend</button>}
        </div>
        {message && <div className="inline-message">{message}</div>}
      </section>
      {editing && <form className="profile-form card" onSubmit={saveProfile}><h2>Edit your profile</h2><div className="form-grid"><label>Display name<input name="display_name" defaultValue={profile.profile.display_name} required /></label><label>Location<input name="location" defaultValue={profile.profile.location ?? ""} /></label></div><label>Bio<textarea name="bio" defaultValue={profile.profile.bio ?? ""} rows={3} maxLength={500} /></label><label>Avatar URL<input name="avatar_url" type="url" defaultValue={profile.profile.avatar_url ?? ""} /></label><div className="form-actions"><button type="button" className="subtle-button" onClick={() => setEditing(false)}>Cancel</button><button className="button button-small">Save profile</button></div></form>}
      <div className="profile-content"><div className="section-heading compact"><div><span className="eyebrow">Stories</span><h2>{ownProfile ? "What you’ve shared" : `From ${profile.profile.display_name}`}</h2></div></div>{posts.length ? <div className="post-list">{posts.map((post) => <PostCard key={post.id} post={post} onDelete={(id) => setPosts((current) => current.filter((item) => item.id !== id))} />)}</div> : <div className="empty-state"><h2>No posts yet.</h2><p>There’s plenty of room for a first thought.</p></div>}</div>
    </div>
  );
}

