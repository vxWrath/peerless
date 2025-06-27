import type { DiscordUser } from './lib/types/models';

declare global {
	namespace App {
		// interface Error {}
		interface Locals {
			user?: DiscordUser | null;
		}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

export {};