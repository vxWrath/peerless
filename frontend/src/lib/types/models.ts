type DiscordPermissions = number;

export interface DiscordPartialGuild {
  id: number;
  name: string;
  icon?: string | null;
  banner?: string | null;
  owner: boolean;
  permissions: DiscordPermissions;
  icon_url: string;
}

export interface DiscordUser {
  session_token: string;
  id: number;
  username: string;
  avatar?: string | null;
  global_name: string;
  guilds: Record<number, DiscordPartialGuild>;
  avatar_url: string;
}

export interface UserData {
    authenticated: boolean;
    user: DiscordUser | null;
}