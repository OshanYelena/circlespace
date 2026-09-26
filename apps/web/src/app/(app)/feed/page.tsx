"use client";

import { Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

import { useAuth } from "@/components/auth-provider";
import { PostCard } from "@/components/post-card";
import { PostComposer } from "@/components/post-composer";
import { api, ApiError } from "@/lib/api";
import type { Post } from "@/lib/types";

export default function FeedPage() {
  const { token, user } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!token) return;
    api.feed(token)
      .then(setPosts)
      .catch((reason) => setError(reason instanceof ApiError ? reason.message : "Could not load the feed."))
      .finally(() => setLoading(false));
  }, [token]);

  return (
    <div className="feed-layout">
      <section className="feed-main">
        <div className="section-heading"><div><span className="eyebrow">Your circle</span><h1>Good {new Date().getHours() < 12 ? "morning" : new Date().getHours() < 18 ? "afternoon" : "evening"}, {user?.profile.display_name.split(" ")[0]}.</h1></div><Sparkles size={25} /></div>
        <PostComposer onCreated={(post) => setPosts((current) => [post, ...current])} />
        {error && <div className="notice error-notice">{error}</div>}
        {loading ? <div className="empty-state">Gathering the latest from your circle…</div> : posts.length ? <div className="post-list">{posts.map((post) => <PostCard key={post.id} post={post} onDelete={(id) => setPosts((current) => current.filter((item) => item.id !== id))} />)}</div> : <div className="empty-state"><Sparkles size={26} /><h2>Your feed is ready for its first story.</h2><p>Publish something above, or add friends to see what they share.</p></div>}
      </section>
      <aside className="feed-aside card"><span className="eyebrow">A small prompt</span><blockquote>What’s one thing you noticed today that you don’t want to forget?</blockquote><p>CircleSpace shows posts from you and accepted friends—nothing else competing for your attention.</p></aside>
    </div>
  );
}

