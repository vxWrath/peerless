// src/routes/+layout.server.ts
import type { LayoutServerLoad } from '$types';

export const load: LayoutServerLoad = async ({ locals }) => {
	return {
		authenticated: Boolean(locals.user),
		user: locals.user ?? null
	};
};