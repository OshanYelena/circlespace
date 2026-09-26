"use client";

import { Check, UserMinus, UserPlus, X } from "lucide-react";
import { FormEvent, useCallback, useEffect, useState } from "react";

import { Avatar } from "@/components/avatar";
import { useAuth } from "@/components/auth-provider";
import { api, ApiError } from "@/lib/api";
import type { FriendRequest, PublicUser } from "@/lib/types";

export default function FriendsPage() {
  const { token } = useAuth();
  const [friends, setFriends] = useState<PublicUser[]>([]);
  const [requests, setRequests] = useState<FriendRequest[]>([]);
  const [message, setMessage] = useState("");

  const load = useCallback(async () => {
    if (!token) return;
    const [friendList, requestList] = await Promise.all([api.friends(token), api.requests(token)]);
    setFriends(friendList);
    setRequests(requestList);
  }, [token]);

  useEffect(() => {
    if (!token) return;
    Promise.all([api.friends(token), api.requests(token)])
      .then(([friendList, requestList]) => {
        setFriends(friendList);
        setRequests(requestList);
      })
      .catch(() => setMessage("Could not load your connections."));
  }, [token]);

  async function send(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token) return;
    const form = event.currentTarget;
    const username = String(new FormData(form).get("username"));
    try {
      await api.sendRequest(token, username);
      setMessage(`Friend request sent to @${username}.`);
      form.reset();
    } catch (reason) {
      setMessage(reason instanceof ApiError ? reason.message : "Could not send the request.");
    }
  }

  async function decide(id: number, action: "accept" | "reject") {
    if (!token) return;
    await api.decideRequest(token, id, action);
    await load();
  }

  async function remove(friend: PublicUser) {
    if (!token || !window.confirm(`Remove ${friend.profile.display_name} from your friends?`)) return;
    await api.removeFriend(token, friend.id);
    setFriends((current) => current.filter((item) => item.id !== friend.id));
  }

  return (
    <div className="connections-page">
      <div className="section-heading"><div><span className="eyebrow">People</span><h1>Your circle</h1><p>Keep your community close and intentional.</p></div></div>
      <section className="friend-invite card"><div><UserPlus size={25} /><h2>Invite someone in</h2><p>Enter their exact CircleSpace username.</p></div><form onSubmit={send}><input name="username" placeholder="username" required /><button className="button button-small">Send request</button></form>{message && <span className="inline-message">{message}</span>}</section>
      {requests.length > 0 && <section><h2 className="subheading">Waiting for you</h2><div className="people-grid">{requests.map((request) => <article className="person-card card" key={request.id}><Avatar name={request.requester.profile.display_name} src={request.requester.profile.avatar_url} /><div><strong>{request.requester.profile.display_name}</strong><span>@{request.requester.username}</span></div><div className="person-actions"><button className="button button-small" onClick={() => decide(request.id, "accept")}><Check size={16} /> Accept</button><button className="icon-button" onClick={() => decide(request.id, "reject")} aria-label="Reject"><X size={17} /></button></div></article>)}</div></section>}
      <section><h2 className="subheading">Friends · {friends.length}</h2>{friends.length ? <div className="people-grid">{friends.map((friend) => <article className="person-card card" key={friend.id}><Avatar name={friend.profile.display_name} src={friend.profile.avatar_url} /><div><strong>{friend.profile.display_name}</strong><span>@{friend.username}</span></div><button className="icon-button" onClick={() => remove(friend)} aria-label={`Remove ${friend.profile.display_name}`}><UserMinus size={18} /></button></article>)}</div> : <div className="empty-state"><UserPlus size={28} /><h2>Your circle has room.</h2><p>Send a request using someone’s username to get started.</p></div>}</section>
    </div>
  );
}
