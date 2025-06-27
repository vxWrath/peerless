// src/hooks.server.ts
import type { Handle } from '@sveltejs/kit';
import type { DiscordUser } from '$lib/types/models';

export const handle: Handle = async ({ event, resolve }) => {
	const sessionToken = event.cookies.get('session_token');

	if (!sessionToken) {
		return resolve(event);
	}

    let user: DiscordUser | null = null;

	try {
		const apiUrl = new URL(`${process.env.API_URL}/api/user`);

		const res = await fetch(apiUrl.toString(), {
			headers: {
				'Authorization': process.env.API_SECRET!,
				'X-Session-Token': sessionToken
			}
		});

		if (!res.ok) {
			throw new Error('Failed to fetch user');
		}

		user = await res.json();
	} catch (error) {
		console.error('Error fetching user:', error);
		return resolve(event);
	}

	if (user) {
		event.locals.user = user;
	}

	return resolve(event);
};