import type { AuthResponse, FriendRequest, Post, PublicUser, User } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
  ) {
    super(message);
  }
}

async function request<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(response.status, body.detail ?? "Request failed");
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  register: (body: { email: string; username: string; password: string; display_name: string }) =>
    request<AuthResponse>("/auth/register", { method: "POST", body: JSON.stringify(body) }),
  login: (body: { login: string; password: string }) =>
    request<AuthResponse>("/auth/login", { method: "POST", body: JSON.stringify(body) }),
  me: (token: string) => request<User>("/users/me", {}, token),
  profile: (username: string, token?: string) =>
    request<PublicUser>(`/users/${username}`, {}, token),
  updateProfile: (token: string, body: Partial<PublicUser["profile"]>) =>
    request<User>("/users/me/profile", { method: "PATCH", body: JSON.stringify(body) }, token),
  feed: (token: string) => request<Post[]>("/posts/feed", {}, token),
  userPosts: (token: string, username: string) =>
    request<Post[]>(`/posts/users/${username}`, {}, token),
  createPost: (token: string, body: { content: string; image_url?: string }) =>
    request<Post>("/posts", { method: "POST", body: JSON.stringify(body) }, token),
  updatePost: (token: string, postId: number, body: { content: string }) =>
    request<Post>(`/posts/${postId}`, { method: "PATCH", body: JSON.stringify(body) }, token),
  deletePost: (token: string, postId: number) =>
    request<void>(`/posts/${postId}`, { method: "DELETE" }, token),
  like: (token: string, postId: number, active: boolean) =>
    request<{ active: boolean; count: number }>(
      `/posts/${postId}/like`,
      { method: active ? "PUT" : "DELETE" },
      token,
    ),
  share: (token: string, postId: number, active: boolean) =>
    request<{ active: boolean; count: number }>(
      `/posts/${postId}/share`,
      { method: active ? "PUT" : "DELETE" },
      token,
    ),
  comment: (token: string, postId: number, content: string) =>
    request<Post>(
      `/posts/${postId}/comments`,
      { method: "POST", body: JSON.stringify({ content }) },
      token,
    ),
  friends: (token: string) => request<PublicUser[]>("/friendships", {}, token),
  requests: (token: string) =>
    request<FriendRequest[]>("/friendships/requests/received", {}, token),
  sendRequest: (token: string, username: string) =>
    request<FriendRequest>(
      "/friendships/requests",
      { method: "POST", body: JSON.stringify({ username }) },
      token,
    ),
  decideRequest: (token: string, id: number, action: "accept" | "reject") =>
    request<FriendRequest>(
      `/friendships/requests/${id}`,
      { method: "PATCH", body: JSON.stringify({ action }) },
      token,
    ),
  removeFriend: (token: string, friendId: number) =>
    request<void>(`/friendships/${friendId}`, { method: "DELETE" }, token),
};
