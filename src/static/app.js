document.addEventListener('DOMContentLoaded', () => {
    // Configure marked for Markdown parsing
    marked.setOptions({
        breaks: true,
        gfm: true
    });

    const userInput = document.getElementById('user-input');
    const chatStream = document.getElementById('chat-stream');

    window.triggerPrompt = function(queryText) {
        userInput.value = queryText;
        window.handleChatSubmit();
    };

    window.handleChatSubmit = async function() {
        const val = userInput.value.trim();
        if(!val) return;

        // Add user message
        const userDiv = document.createElement('div');
        userDiv.className = 'flex items-start gap-space-md justify-end';
        userDiv.innerHTML = `
            <div class="bg-primary-container text-on-primary-container px-space-lg py-space-md rounded-2xl rounded-tr-none max-w-xl text-body-md shadow-sm">${val}</div>
            <div class="w-8 h-8 rounded-full bg-surface-bright flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-on-surface text-[16px]">person</span>
            </div>
        `;
        chatStream.appendChild(userDiv);
        userInput.value = '';
        userInput.disabled = true;

        // Scroll to bottom
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

        // Add loading indicator
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'flex items-start gap-space-md id-loading';
        loadingDiv.innerHTML = `
            <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
                <span class="material-symbols-outlined text-on-primary text-[16px]" style="font-variation-settings: 'FILL' 1;">smart_toy</span>
            </div>
            <div class="bg-surface-container p-space-lg rounded-2xl rounded-tl-none max-w-2xl flex items-center gap-space-sm text-on-surface-variant text-body-md shadow-md">
                <span class="material-symbols-outlined animate-spin text-primary">progress_activity</span>
                Retrieving from grounded sources & synthesizing response...
            </div>
        `;
        chatStream.appendChild(loadingDiv);
        window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

            // When deployed to Vercel, this API_BASE_URL should be updated to point to the live Railway backend URL.
            // Example: const API_BASE_URL = 'https://your-m2rag-backend.up.railway.app';
            const API_BASE_URL = 'https://web-production-c27cc.up.railway.app'; // Leave empty for local same-origin, or set to 'http://localhost:8000' for local cross-origin
            const endpoint = API_BASE_URL ? `${API_BASE_URL}/api/chat` : '/api/chat';

            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: val })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            
            // Remove loading indicator
            chatStream.removeChild(loadingDiv);
            userInput.disabled = false;
            userInput.focus();

            const aiDiv = document.createElement('div');
            aiDiv.className = 'flex items-start gap-space-md';
            
            // Special styling for errors/refusals based on response content
            if (data.response.includes("I'm not able to provide medical advice") || data.response.includes("M2Rag is strictly programmed to decline")) {
                aiDiv.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
                        <span class="material-symbols-outlined text-on-primary text-[16px]" style="font-variation-settings: 'FILL' 1;">smart_toy</span>
                    </div>
                    <div class="bg-surface-container p-space-lg rounded-2xl rounded-tl-none max-w-2xl flex flex-col gap-space-md shadow-md border-l-4 border-error">
                        <div class="flex items-center gap-space-sm text-error">
                            <span class="material-symbols-outlined">block</span>
                            <h4 class="font-headline-sm text-headline-sm">Out-of-Scope / Safety Refusal</h4>
                        </div>
                        <div class="text-body-md text-on-surface leading-relaxed content-prose">
                            ${marked.parse(data.response)}
                        </div>
                    </div>
                `;
            } else if (data.response.includes("don't appear to cover this topic") || data.response.includes("outside the indexed")) {
                aiDiv.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
                        <span class="material-symbols-outlined text-on-primary text-[16px]" style="font-variation-settings: 'FILL' 1;">smart_toy</span>
                    </div>
                    <div class="bg-surface-container p-space-lg rounded-2xl rounded-tl-none max-w-2xl flex flex-col gap-space-md shadow-md border-l-4 border-tertiary">
                        <div class="flex items-center gap-space-sm text-tertiary">
                            <span class="material-symbols-outlined">search_off</span>
                            <h4 class="font-headline-sm text-headline-sm">Corpus Retrieval Notice</h4>
                        </div>
                        <div class="text-body-md text-on-surface leading-relaxed content-prose">
                            ${marked.parse(data.response)}
                        </div>
                    </div>
                `;
            } else {
                // Successful response
                aiDiv.innerHTML = `
                    <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
                        <span class="material-symbols-outlined text-on-primary text-[16px]" style="font-variation-settings: 'FILL' 1;">smart_toy</span>
                    </div>
                    <div class="bg-surface-container p-space-lg rounded-2xl rounded-tl-none max-w-2xl flex flex-col gap-space-md shadow-md">
                        <div class="text-body-md text-on-surface leading-relaxed content-prose">
                            ${marked.parse(data.response)}
                        </div>
                    </div>
                `;
            }

            chatStream.appendChild(aiDiv);
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });

        } catch (error) {
            console.error('Error:', error);
            chatStream.removeChild(loadingDiv);
            userInput.disabled = false;
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'flex items-start gap-space-md';
            errorDiv.innerHTML = `
                <div class="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
                    <span class="material-symbols-outlined text-on-primary text-[16px]" style="font-variation-settings: 'FILL' 1;">smart_toy</span>
                </div>
                <div class="bg-surface-container p-space-lg rounded-2xl rounded-tl-none max-w-2xl flex flex-col gap-space-md shadow-md border-l-4 border-error">
                    <div class="flex items-center gap-space-sm text-error">
                        <span class="material-symbols-outlined">error</span>
                        <h4 class="font-headline-sm text-headline-sm">Network Error</h4>
                    </div>
                    <p class="text-body-md text-on-surface leading-relaxed">
                        Sorry, there was an error processing your request. Please try again.
                    </p>
                </div>
            `;
            chatStream.appendChild(errorDiv);
            window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
        }
    };
});
