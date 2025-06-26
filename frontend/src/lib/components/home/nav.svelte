<script lang="ts">
    let showDropdown = $state(false);
    let menuOpen = $state(false);
    let mobileMenu: HTMLElement;

    let authenticated = $state(false);
    let user = $state({
        username: '',
        avatar_url: ''
    });

    function toggleMobileMenu() {
        menuOpen = !menuOpen;
        mobileMenu.classList.toggle('hidden');
    }

    function toggleDropdown() {
        showDropdown = !showDropdown;
    }
</script>

<header class="sticky top-0 z-50 bg-gray-800/95 backdrop-blur-sm shadow-md">
    <nav class="p-4 flex items-center justify-between">
        <div class="flex items-center space-x-6">
            <a href="/" class="flex items-center hover:text-pink-400 transition-colors" aria-label="Peerless Home">
                <img src="pink.png" alt="Peerless Logo" class="h-10 mr-3 filter drop-shadow-lg">
                <span class="text-xl font-bold">Peerless</span>
            </a>

            <div class="hidden md:flex items-center space-x-6">
                <a href="#features" class="text-xl text-gray-300 hover:text-pink-400 transition-colors">Features</a>
                <a href="#pricing" class="text-xl text-gray-300 hover:text-pink-400 transition-colors">Pricing</a>
                <a href="#support" class="text-xl text-gray-300 hover:text-pink-400 transition-colors">Support</a>
                <a href="#status" class="text-xl text-gray-300 hover:text-pink-400 transition-colors">Status</a>
                <a href="https://discord.com/api/oauth2/authorize?client_id=1105640024113954829&permissions=9193109515280&scope=bot+applications.commands" class="text-xl text-gray-300 hover:text-pink-400 transition-colors">Invite</a>
            </div>
        </div>

        <div class="relative flex items-center justify-center">
            {#if authenticated}
                <div>
                    <button
                        onclick={toggleDropdown}
                        class="flex items-center space-x-2 hover:text-pink-400 text-white px-4 rounded-lg transition-colors cursor-pointer focus:outline-none"
                    >
                        <span class="hidden md:block">{user.username}</span>
                        <img src={user.avatar_url} alt="Profile" class="h-10 w-10 rounded-full filter drop-shadow-lg" />
                        <i
                            class="fas fa-chevron-down text-gray-300 text-sm transition-transform duration-200"
                            class:rotate-180={showDropdown}
                        ></i>
                    </button>

                    {#if showDropdown}
                        <!-- Dropdown Menu -->
                        <div
                            class="absolute right-0 top-12 mt-1 w-48 bg-gray-800 text-white shadow-lg border-2 border-gray-700"
                        >
                            <a href="/servers" class="block pl-0.5 py-2 hover:bg-gray-700 transition-colors">
                                <div class="flex items-center space-x-2 text-right">
                                    <i class="fas fa-server w-6"></i>
                                    <p>Servers</p>
                                </div>
                            </a>
                            <a href="/custom-bots" class="block pl-0.5 py-2 hover:bg-gray-700 transition-colors">
                                <div class="flex items-center space-x-2 text-right">
                                    <i class="fas fa-cogs w-6"></i>
                                    <p>Custom Bots</p>
                                </div>
                            </a>
                            <button class="block pl-0.5 py-2 hover:bg-red-500 transition-colors w-full text-left">
                                <div class="flex items-center space-x-2 text-right">
                                    <i class="fas fa-sign-out-alt w-6"></i>
                                    <p>Log Out</p>
                                </div>
                            </button>
                        </div>
                    {/if}
                </div>
            {:else}
                <a
                    href="/auth/login?redirect_to=/servers"
                    class="flex items-center space-x-2 bg-indigo-500 hover:bg-indigo-600 text-white px-4 py-2 rounded-lg transition-colors cursor-pointer"
                >
                    <i class="fab fa-discord"></i>
                    <span>Login</span>
                </a>
            {/if}

            <div class="relative flex items-center justify-center">
                <button
                    id="mobileMenuBtn"
                    onclick={toggleMobileMenu}
                    aria-label="Toggle mobile menu"
                    class="md:hidden ml-4 text-gray-300 hover:text-pink-400 focus:outline-none flex items-center transition-transform duration-300"
                >
                    {#if menuOpen}
                        <i class="fas fa-times text-2xl transition-transform duration-300"></i>
                    {:else}
                        <i class="fas fa-bars text-2xl transition-transform duration-300"></i>
                    {/if}
                </button>
            </div>
        </div>
    </nav>

    <div bind:this={mobileMenu} class="md:hidden hidden">
        <div class="flex flex-col items-center border-b-2 border-gray-700 px-4 text-center">
            <div class="border-2 border-b-0 border-gray-700 rounded-t-lg flex flex-col w-full overflow-hidden">
                <a href="#features" class="w-full py-0.5 bg-gray-900 text-2xl font-medium text-gray-300 hover:text-pink-400 transition-colors">Features</a>
                <a href="#pricing" class="w-full py-0.5 bg-gray-800 text-2xl font-medium text-gray-300 hover:text-pink-400 transition-colors">Pricing</a>
                <a href="#support" class="w-full py-0.5 bg-gray-900 text-2xl font-medium text-gray-300 hover:text-pink-400 transition-colors">Support</a>
                <a href="#status" class="w-full py-0.5 bg-gray-800 text-2xl font-medium text-gray-300 hover:text-pink-400 transition-colors">Status</a>
                <a 
                    href="https://discord.com/api/oauth2/authorize?client_id=1105640024113954829&permissions=9193109515280&scope=bot+applications.commands" 
                    class="w-full py-0.5 bg-gray-900 text-2xl font-medium text-gray-300 hover:text-pink-400 transition-colors"
                >Invite</a>
            </div>
        </div>
    </div>
</header>