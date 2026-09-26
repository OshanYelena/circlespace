export type Profile = {
  display_name: string;
  bio: string | null;
  avatar_url: string | null;
  location: string | null;
};

export type PublicUser = {
  id: number;
  username: string;
  created_at: string;
  profile: Profile;
};

export type User = PublicUser & { email: string };

export type AuthResponse = {
  access_token: string;
  token_type: "bearer";
  user: User;
};

export type Comment = {
  id: number;
  author: PublicUser;
  content: string;
  created_at: string;
  updated_at: string;
};

export type Post = {
  id: number;
  author: PublicUser;
  content: string;
  image_url: string | null;
  created_at: string;
  updated_at: string;
  comments: Comment[];
  like_count: number;
  share_count: number;
  viewer_liked: boolean;
  viewer_shared: boolean;
};

export type FriendRequest = {
  id: number;
  requester: PublicUser;
  recipient: PublicUser;
  status: "pending" | "accepted" | "rejected";
  created_at: string;
  responded_at: string | null;
};

