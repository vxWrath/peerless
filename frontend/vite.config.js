import devtoolsJson from 'vite-plugin-devtools-json';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
	plugins: [sveltekit(), devtoolsJson(), tailwindcss()],
	// This will need to be changed in production
	server: {
		host: true,
		strictPort: true,
		watch: {
		usePolling: true,
		},
	},
});
