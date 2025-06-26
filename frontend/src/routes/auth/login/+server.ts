import { redirect } from '@sveltejs/kit';

export async function GET({ request }) {
	const reqUrl = new URL(request.url);
	const redirectTo = reqUrl.searchParams.get('redirect_to') ?? '/';

	let data;

	try {
		const url = new URL(`${process.env.API_URL}/bot/oauth`);
		url.searchParams.set('redirect_to', redirectTo);

		console.log('Redirecting to OAuth URL:', url.toString());

		const res = await fetch(url.toString(), {
			headers: {
				Authorization: process.env.API_SECRET
			}
		});

		if (!res.ok) {
			throw new Error('Failed to fetch oauth URL');
		}

		data = await res.json();
	} catch (error) {
		console.error('OAuth redirect error:', error);
		if (error instanceof Error) {
			console.error('Full stack trace:\n', error.stack);
		}
		return new Response('OAuth redirect failed', { status: 500 });
	}

	return redirect(302, data.url);
}