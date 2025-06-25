<script lang="ts">
	import { onMount } from 'svelte';
	import { browser } from '$app/environment';

    let show_dropdown = $state(false);
    let menu_open = $state(false);
    let mobile_menu: HTMLElement;

    let authenticated = $state(false);
    let user = $state({
        username: '',
        discord_id: '',
        avatar_url: ''
    });

    async function store_user_data(user_data) {
        try {
            await fetch('/account/user', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(user_data)
            });
            localStorage.setItem('user', JSON.stringify(user_data));
        } catch (e) {
            console.error('Failed to store user data:', e);
            localStorage.setItem('user', JSON.stringify(user_data));
        }
    }

    async function load_user_data(discord_id) {
        try {
            const response = await fetch(`/account/user/${discord_id}`);
            if (response.ok) {
                const user_data = await response.json();
                if (!user_data.error) {
                    return user_data;
                }
            }
        } catch (e) {
            console.error('Failed to load user data from API:', e);
        }
        return null;
    }

    onMount(async () => {
        if (browser) {
            const saved_user = localStorage.getItem('user');
            if (saved_user) {
                try {
                    const local_user = JSON.parse(saved_user);
                    const api_user = await load_user_data(local_user.discord_id);

                    if (api_user) {
                        user = api_user;
                        authenticated = true;
                        localStorage.setItem('user', JSON.stringify(api_user));
                    } else {
                        user = local_user;
                        authenticated = true;
                    }
                } catch (e) {
                    localStorage.removeItem('user');
                }
            }

            const url_params = new URLSearchParams(window.location.search);
            const username = url_params.get('username');
            const discord_id = url_params.get('discord_id');
            const avatar_url = url_params.get('avatar_url');

            if (username && discord_id && avatar_url) {
                const user_data = {
                    username: decodeURIComponent(username),
                    discord_id: discord_id,
                    avatar_url: decodeURIComponent(avatar_url)
                };

                user = user_data;
                authenticated = true;

                await store_user_data(user_data);

                const new_url = window.location.pathname;
                window.history.replaceState({}, '', new_url);
            }
        }
    });

    function toggle_mobile_menu() {
        menu_open = !menu_open;
        mobile_menu.classList.toggle('hidden');
    }

    function toggle_dropdown() {
        show_dropdown = !show_dropdown;
    }

    function handle_logout() {
        if (browser) {
            localStorage.removeItem('user');
        }
        authenticated = false;
        user = {
            username: '',
            discord_id: '',
            avatar_url: ''
        };
    }
</script>

<header class="sticky top-0 z-50 bg-gray-900/95 backdrop-blur-md shadow-xl border-b border-gray-700">
    <nav class="w-full px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16 w-full">
            <div class="flex items-center space-x-8">
                <a href="/" class="flex items-center group" aria-label="Peerless Home">
                    <img src="pink.png" alt="Peerless Logo" class="h-10 w-10 mr-3 filter drop-shadow-lg group-hover:scale-110 transition-transform duration-300">
                    <span class="text-2xl font-bold bg-gradient-to-r from-pink-400 to-pink-600 bg-clip-text text-transparent">Peerless</span>
                </a>

                <div class="hidden lg:flex items-center space-x-8">
                    <a href="#features" class="text-gray-300 hover:text-pink-400 transition-all duration-300 font-medium relative group">
                        Features
                        <span class="absolute -bottom-1 left-0 w-0 h-0.5 bg-pink-400 transition-all duration-300 group-hover:w-full"></span>
                    </a>
                    <a href="#pricing" class="text-gray-300 hover:text-pink-400 transition-all duration-300 font-medium relative group">
                        Pricing
                        <span class="absolute -bottom-1 left-0 w-0 h-0.5 bg-pink-400 transition-all duration-300 group-hover:w-full"></span>
                    </a>
                    <a href="https://discord.gg/FsNK9y7MPg" class="text-gray-300 hover:text-pink-400 transition-all duration-300 font-medium relative group">
                        Support
                        <span class="absolute -bottom-1 left-0 w-0 h-0.5 bg-pink-400 transition-all duration-300 group-hover:w-full"></span>
                    </a>
                </div>
            </div>

            <div class="flex items-center space-x-4">
                <a href="https://discord.com/application-directory/1105640024113954829"
                   class="hidden lg:block bg-pink-500 hover:bg-pink-600 text-white px-4 py-2 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg">
                    <i class="fab fa-discord mr-2"></i>
                    Invite Bot
                </a>

                {#if authenticated}
                    <div class="relative">
                        <button
                            onclick={toggle_dropdown}
                            class="flex items-center space-x-2 hover:text-pink-400 text-white px-3 py-2 rounded-lg transition-all duration-300 bg-gray-800 hover:bg-gray-700"
                        >
                            <span class="hidden md:block font-medium">{user.username}</span>
                            <img src={user.avatar_url} alt="Profile" class="h-8 w-8 rounded-full" />
                            <i
                                class="fas fa-chevron-down text-gray-300 text-sm transition-transform duration-200"
                                class:rotate-180={show_dropdown}
                            ></i>
                        </button>

                        {#if show_dropdown}
                            <div class="absolute right-0 top-12 mt-2 w-56 bg-gray-800 rounded-lg shadow-xl border border-gray-700 overflow-hidden">
                                <div class="px-4 py-3 border-b border-gray-700">
                                    <p class="text-sm text-gray-400">Signed in as</p>
                                    <p class="text-white font-medium">{user.username}</p>
                                </div>
                                <a href="/dashboard" class="block px-4 py-3 hover:bg-gray-700 transition-colors">
                                    <div class="flex items-center space-x-3">
                                        <i class="fas fa-tachometer-alt text-pink-400 w-5"></i>
                                        <span>Dashboard</span>
                                    </div>
                                </a>
                                <a href="/servers" class="block px-4 py-3 hover:bg-gray-700 transition-colors">
                                    <div class="flex items-center space-x-3">
                                        <i class="fas fa-server text-pink-400 w-5"></i>
                                        <span>My Servers</span>
                                    </div>
                                </a>
                                <a href="#pricing" class="block px-4 py-3 hover:bg-gray-700 transition-colors">
                                    <div class="flex items-center space-x-3">
                                        <i class="fas fa-crown text-pink-400 w-5"></i>
                                        <span>Upgrade Plans</span>
                                    </div>
                                </a>
                                <div class="border-t border-gray-700">
                                    <button onclick={handle_logout} class="block w-full px-4 py-3 text-left hover:bg-red-600 hover:text-white transition-all duration-300 cursor-pointer group">
                                        <div class="flex items-center space-x-3">
                                            <i class="fas fa-sign-out-alt text-red-400 group-hover:text-white w-5 transition-colors duration-300"></i>
                                            <span class="group-hover:font-medium transition-all duration-300">Sign Out</span>
                                        </div>
                                    </button>
                                </div>
                            </div>
                        {/if}
                    </div>
                {:else}
                    <a href="/account/login/discord" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-lg">
                        <i class="fab fa-discord mr-2"></i>
                        Login
                    </a>
                {/if}

                <button
                    onclick={toggle_mobile_menu}
                    aria-label="Toggle mobile menu"
                    class="lg:hidden ml-2 p-2 text-gray-300 hover:text-pink-400 focus:outline-none transition-colors duration-300"
                >
                    {#if menu_open}
                        <i class="fas fa-times text-xl"></i>
                    {:else}
                        <i class="fas fa-bars text-xl"></i>
                    {/if}
                </button>
            </div>
        </div>
    </nav>

    {#if menu_open}
        <div bind:this={mobile_menu} class="lg:hidden bg-gray-900 border-t border-gray-700">
            <div class="px-4 py-6 space-y-4">
                <a href="#features" class="block py-3 text-lg font-medium text-gray-300 hover:text-pink-400 transition-colors border-b border-gray-700">
                    <i class="fas fa-star mr-3 text-pink-400"></i>
                    Features
                </a>
                <a href="#pricing" class="block py-3 text-lg font-medium text-gray-300 hover:text-pink-400 transition-colors border-b border-gray-700">
                    <i class="fas fa-tag mr-3 text-pink-400"></i>
                    Pricing
                </a>
                <a href="https://discord.gg/FsNK9y7MPg" class="block py-3 text-lg font-medium text-gray-300 hover:text-pink-400 transition-colors border-b border-gray-700">
                    <i class="fas fa-headset mr-3 text-pink-400"></i>
                    Support
                </a>
                <a href="https://discord.com/application-directory/1105640024113954829"
                   class="block py-3 bg-pink-500 hover:bg-pink-600 text-white text-center rounded-lg font-semibold transition-colors">
                    <i class="fab fa-discord mr-2"></i>
                    Invite Bot
                </a>
            </div>
        </div>
    {/if}
</header>