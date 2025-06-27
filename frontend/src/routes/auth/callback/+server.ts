import { redirect } from '@sveltejs/kit';

export async function GET({ request }) {
	const url = new URL(request.url);
	const code = url.searchParams.get('code');
	const oauth_token = url.searchParams.get('state');

	if (!code) {
		throw redirect(302, '/auth/login');
	}

	let data;

	try {
		const apiUrl = new URL(`${process.env.API_URL}/oauth/code`);
		apiUrl.searchParams.set('code', code);
		if (oauth_token) apiUrl.searchParams.set('oauth_token', oauth_token);

		const res = await fetch(apiUrl.toString(), {
			headers: {
				Authorization: process.env.API_SECRET
			}
		});

		if (!res.ok) {
			throw new Error('Failed to fetch OAuth code');
		}

		data = await res.json();
	} catch (error) {
		console.error('OAuth callback error:', error);
		throw redirect(302, '/auth/login');
	}

	const sessionToken = data.user.session_token;
	const cookie = `session_token=${sessionToken}; Path=/; HttpOnly; Secure; SameSite=Strict`;

	return new Response(
		`<html><head><meta http-equiv="refresh" content="0; URL='${data.redirect_to || '/'}'" /></head></html>`,
		{
			status: 200,
			headers: {
				'Content-Type': 'text/html',
				'Set-Cookie': cookie
			}
		}
	);
}