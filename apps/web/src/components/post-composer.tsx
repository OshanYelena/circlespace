"use client";

import { Image as ImageIcon, LoaderCircle, Send } from "lucide-react";
import { FormEvent, useState } from "react";

import { Avatar } from "@/components/avatar";
import { useAuth } from "@/components/auth-provider";
import { api, ApiError } from "@/lib/api";
import type { Post } from "@/lib/types";

export function PostComposer({ onCreated }: { onCreated: (post: Post) => void }) {
  const { token, user } = useAuth();
  const [content, setContent] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [showImage, setShowImage] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!token || !content.trim()) return;
    setPending(true);
    setError("");
    try {
      const post = await api.createPost(token, {
        content: content.trim(),
        ...(imageUrl.trim() ? { image_url: imageUrl.trim() } : {}),
      });
      onCreated(post);
      setContent("");
      setImageUrl("");
      setShowImage(false);
    } catch (reason) {
      setError(reason instanceof ApiError ? reason.message : "Could not publish your post.");
    } finally {
      setPending(false);
    }
  }

  if (!user) return null;
  return (
    <form className="composer card" onSubmit={submit}>
      <Avatar name={user.profile.display_name} src={user.profile.avatar_url} />
      <div className="composer-body">
        <textarea
          value={content}
          onChange={(event) => setContent(event.target.value)}
          placeholder="What’s moving through your world?"
          maxLength={2000}
          rows={3}
          aria-label="Post content"
        />
        {showImage && <input value={imageUrl} onChange={(event) => setImageUrl(event.target.value)} type="url" placeholder="Paste an image URL" aria-label="Image URL" />}
        {error && <div className="form-error">{error}</div>}
        <div className="composer-tools">
          <button className="subtle-button" type="button" onClick={() => setShowImage((value) => !value)}><ImageIcon size={17} /> Add image</button>
          <button className="button button-small" disabled={pending || !content.trim()}>{pending ? <LoaderCircle className="spin" size={17} /> : <><Send size={16} /> Publish</>}</button>
        </div>
      </div>
    </form>
  );
}

