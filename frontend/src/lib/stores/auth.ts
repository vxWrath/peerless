import { writable } from 'svelte/store';
import { browser } from '$app/environment';

export interface User {
	id: string;
	username: string;
	discriminator: string;
	avatar: string;
	guilds?: Guild[];
}

export interface Guild {
	id: string;
	name: string;
	icon: string;
	owner: boolean;
	permissions: string;
}

export const user = writable<User | null>(null);

export async function checkAuth() {
	if (!browser) return;
	
	try {
		const response = await fetch('/api/auth/me');
		if (response.ok) {
			const userData = await response.json();
			user.set(userData);
		}
	} catch (error) {
		console.error('Auth check failed:', error);
	}
}

export async function fetchUserGuilds() {
	try {
		const response = await fetch('/api/auth/guilds');
		if (response.ok) {
			const guilds = await response.json();
			user.update(u => u ? { ...u, guilds } : null);
			return guilds;
		}
	} catch (error) {
		console.error('Failed to fetch guilds:', error);
	}
	return [];
}
