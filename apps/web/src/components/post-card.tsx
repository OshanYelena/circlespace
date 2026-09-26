"use client";

import { Heart, MessageCircle, Pencil, Repeat2, Send, Trash2 } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { FormEvent, useState } from "react";

import { Avatar } from "@/components/avatar";
import { useAuth } from "@/components/auth-provider";
import { api } from "@/lib/api";
import type { Post } from "@/lib/types";

function timeAgo(value: string): string {
  const seconds = Math.floor((Date.now() - new Date(value).getTime()) / 1000);
  if (seconds < 60) return "just now";
  if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
  if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
  return `${Math.floor(seconds / 86400)}d ago`;
}

export function PostCard({
  post: initialPost,
  onDelete,
}: {
  post: Post;
  onDelete: (postId: number) => void;
}) {
  const { token, user } = useAuth();
  const [post, setPost] = useState(initialPost);
  const [comment, setComment] = useState("");
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(post.content);
  const ownPost = user?.id === post.author.id;

  async function engage(kind: "like" | "share") {
    if (!token) return;
    const current = kind === "like" ? post.viewer_liked : post.viewer_shared;
    setPost((value) => ({
      ...value,
      [kind === "like" ? "viewer_liked" : "viewer_shared"]: !current,
      [kind === "like" ? "like_count" : "share_count"]:
        value[kind === "like" ? "like_count" : "share_count"] + (current ? -1 : 1),
    }));
    try {
      const result = kind === "like"
        ? await api.like(token, post.id, !current)
        : await api.share(token, post.id, !current);
      setPost((value) => ({
        ...value,
        [kind === "like" ? "viewer_liked" : "viewer_shared"]: result.active,
        [kind === "like" ? "like_count" : "share_count"]: result.count,
      }));
    } catch {
      setPost(initialPost);
    }
  }

  async function addComment(event: FormEvent) {
    event.preventDefault();
    if (!token || !comment.trim()) return;
    const updated = await api.comment(token, post.id, comment.trim());
    setPost(updated);
    setComment("");
  }

  async function saveEdit() {
    if (!token || !draft.trim()) return;
    setPost(await api.updatePost(token, post.id, { content: draft.trim() }));
    setEditing(false);
  }

  async function remove() {
    if (!token || !window.confirm("Delete this post? This cannot be undone.")) return;
    await api.deletePost(token, post.id);
    onDelete(post.id);
  }

  return (
    <article className="post-card card">
      <header className="post-header">
        <Link href={`/profile/${post.author.username}`}><Avatar name={post.author.profile.display_name} src={post.author.profile.avatar_url} /></Link>
        <div className="post-byline"><Link href={`/profile/${post.author.username}`}>{post.author.profile.display_name}</Link><span>@{post.author.username} · {timeAgo(post.created_at)}</span></div>
        {ownPost && <div className="post-owner-actions"><button className="icon-button" onClick={() => setEditing((value) => !value)} aria-label="Edit post"><Pencil size={16} /></button><button className="icon-button danger" onClick={remove} aria-label="Delete post"><Trash2 size={16} /></button></div>}
      </header>
      {editing ? <div className="edit-post"><textarea value={draft} onChange={(event) => setDraft(event.target.value)} rows={4} /><div><button className="subtle-button" onClick={() => setEditing(false)}>Cancel</button><button className="button button-small" onClick={saveEdit}>Save</button></div></div> : <p className="post-content">{post.content}</p>}
      {post.image_url && <div className="post-image"><Image src={post.image_url} alt="Post attachment" fill sizes="(max-width: 700px) 100vw, 620px" unoptimized /></div>}
      <div className="engagement-row">
        <button className={post.viewer_liked ? "active-like" : ""} onClick={() => engage("like")}><Heart size={19} fill={post.viewer_liked ? "currentColor" : "none"} /> {post.like_count || "Like"}</button>
        <button onClick={() => document.getElementById(`comment-${post.id}`)?.focus()}><MessageCircle size={19} /> {post.comments.length || "Comment"}</button>
        <button className={post.viewer_shared ? "active-share" : ""} onClick={() => engage("share")}><Repeat2 size={20} /> {post.share_count || "Share"}</button>
      </div>
      {post.comments.length > 0 && <div className="comments">{post.comments.map((item) => <div className="comment" key={item.id}><Avatar name={item.author.profile.display_name} src={item.author.profile.avatar_url} size="sm" /><div><strong>{item.author.profile.display_name}</strong><p>{item.content}</p></div></div>)}</div>}
      <form className="comment-form" onSubmit={addComment}><Avatar name={user?.profile.display_name ?? "You"} src={user?.profile.avatar_url} size="sm" /><input id={`comment-${post.id}`} value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Write a thoughtful reply…" maxLength={500} /><button className="icon-button" disabled={!comment.trim()} aria-label="Post comment"><Send size={17} /></button></form>
    </article>
  );
}

