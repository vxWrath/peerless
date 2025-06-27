import { redirect } from '@sveltejs/kit';

export async function GET({ cookies }) {
	const sessionToken = cookies.get('session_token');

	cookies.delete('session_token', {
		path: '/',
	});

	if (!sessionToken) {
		return redirect(302, '/');
	}

	try {
		const url = new URL(`${process.env.API_URL}/oauth/logout`);

		const res = await fetch(url.toString(), {
			headers: {
				Authorization: process.env.API_SECRET,
				'X-Session-Token': sessionToken
			}
		});

		if (!res.ok) {
			throw new Error('Failed to fetch oauth URL');
		}
	} catch (error) {
		console.error('OAuth redirect error:', error);
		if (error instanceof Error) {
			console.error('Full stack trace:\n', error.stack);
		}
		return new Response('OAuth redirect failed', { status: 500 });
	}

	return redirect(302, '/');
}