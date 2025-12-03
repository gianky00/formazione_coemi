def get_chat_html():
    return """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

        :root {
            --bg-color: #FFFFFF;
            --primary-color: #1D4ED8; /* Royal Blue */
            --primary-light: #EFF6FF;
            --text-primary: #111827;
            --text-secondary: #6B7280;
            --border-color: #F3F4F6;

            --user-bubble-bg: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%);
            --user-bubble-text: #FFFFFF;

            --lyra-bubble-bg: #F9FAFB;
            --lyra-bubble-text: #1F2937;
            --lyra-border: #E5E7EB;
        }

        * {
            box-sizing: border-box;
            -webkit-font-smoothing: antialiased;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
        }

        /* Header */
        #header {
            padding: 16px 20px;
            border-bottom: 1px solid var(--border-color);
            background: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(10px);
            display: flex;
            align-items: center;
            gap: 12px;
            z-index: 20;
            box-shadow: 0 1px 2px rgba(0,0,0,0.02);
        }

        .header-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 14px;
            box-shadow: 0 2px 4px rgba(29, 78, 216, 0.2);
        }

        .header-info {
            display: flex;
            flex-direction: column;
        }

        .header-title {
            font-weight: 600;
            font-size: 15px;
            color: var(--text-primary);
        }

        .header-status {
            font-size: 11px;
            color: #10B981; /* Green-500 */
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .header-status::before {
            content: '';
            display: block;
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #10B981;
            box-shadow: 0 0 0 2px rgba(16, 185, 129, 0.1);
        }

        /* Chat Area */
        #chat-container {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
            scroll-behavior: smooth;
        }

        #chat-container::-webkit-scrollbar {
            width: 6px;
        }
        #chat-container::-webkit-scrollbar-thumb {
            background-color: #E5E7EB;
            border-radius: 3px;
        }
        #chat-container::-webkit-scrollbar-track {
            background: transparent;
        }

        /* Message Row */
        .message-row {
            display: flex;
            gap: 12px;
            opacity: 0;
            animation: slideInUp 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
            max-width: 100%;
        }

        .message-row.user {
            flex-direction: row-reverse;
        }

        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            flex-shrink: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
        }

        .avatar.lyra {
            background: #EFF6FF;
            color: #1D4ED8;
            border: 1px solid #BFDBFE;
        }

        .avatar.user {
            background: #F3F4F6;
            color: #4B5563;
        }

        /* Bubbles */
        .bubble {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.5;
            position: relative;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            word-wrap: break-word;
        }

        .message-row.user .bubble {
            background: var(--user-bubble-bg);
            color: var(--user-bubble-text);
            border-top-right-radius: 2px;
        }

        .message-row.lyra .bubble {
            background: var(--lyra-bubble-bg);
            color: var(--lyra-bubble-text);
            border: 1px solid var(--lyra-border);
            border-top-left-radius: 2px;
        }

        /* Markdown Styles */
        .bubble p { margin: 0 0 8px 0; }
        .bubble p:last-child { margin: 0; }
        .bubble strong { font-weight: 600; }
        .bubble code {
            font-family: 'Menlo', monospace;
            font-size: 0.9em;
            padding: 2px 4px;
            border-radius: 4px;
            background: rgba(0,0,0,0.05);
        }
        .message-row.user .bubble code { background: rgba(255,255,255,0.2); }

        /* Typing Indicator */
        .typing-indicator {
            display: none; /* Flex when active */
            align-items: center;
            gap: 4px;
            padding: 12px 16px;
            background: #F9FAFB;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            border-top-left-radius: 2px;
            width: fit-content;
            margin-left: 44px; /* Avatar width + gap */
            margin-bottom: 10px;
            animation: fadeIn 0.3s ease;
        }

        .dot {
            width: 6px;
            height: 6px;
            background-color: #9CA3AF;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }

        /* Input Area */
        #input-area {
            padding: 16px;
            background: #FFFFFF;
            border-top: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 12px;
            position: relative;
            z-index: 20;
        }

        #message-input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #E5E7EB;
            border-radius: 24px;
            background: #F9FAFB;
            font-family: inherit;
            font-size: 14px;
            outline: none;
            transition: all 0.2s;
        }
        #message-input:focus {
            background: #FFFFFF;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.1);
        }

        #send-btn {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: var(--primary-color);
            color: white;
            border: none;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.2s, background 0.2s;
            box-shadow: 0 2px 4px rgba(29, 78, 216, 0.3);
        }
        #send-btn:hover {
            background: #1E40AF;
            transform: scale(1.05);
        }
        #send-btn:active {
            transform: scale(0.95);
        }
        #send-btn svg {
            width: 20px;
            height: 20px;
            fill: none;
            stroke: currentColor;
            stroke-width: 2;
            stroke-linecap: round;
            stroke-linejoin: round;
        }

        /* Suggestions */
        #suggestions {
            display: flex;
            gap: 8px;
            padding: 12px 20px;
            overflow-x: auto;
            background: #FFFFFF;
            border-bottom: 1px solid var(--border-color);
        }
        #suggestions::-webkit-scrollbar { height: 0; }

        .chip {
            padding: 6px 12px;
            background: #F3F4F6;
            border: 1px solid #E5E7EB;
            border-radius: 16px;
            font-size: 12px;
            color: #4B5563;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
        }
        .chip:hover {
            background: #EFF6FF;
            color: var(--primary-color);
            border-color: #BFDBFE;
        }

        /* Animations */
        @keyframes slideInUp {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

    </style>
</head>
<body>
    <div id="header">
        <div class="header-avatar">L</div>
        <div class="header-info">
            <div class="header-title">Lyra AI</div>
            <div class="header-status">Online</div>
        </div>
    </div>

    <div id="suggestions">
        <div class="chip" onclick="sendMessage('Analisi Scadenze')">Analisi Scadenze</div>
        <div class="chip" onclick="sendMessage('Sintesi Sicurezza')">Sintesi Sicurezza</div>
        <div class="chip" onclick="sendMessage('Statistiche')">Statistiche</div>
    </div>

    <div id="chat-container">
        <!-- Messages will appear here -->
        <div class="message-row lyra">
            <div class="avatar lyra">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2 2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/><path d="M4 11v2a8 8 0 0 0 16 0v-2"/><line x1="12" y1="22" x2="12" y2="15"/></svg>
            </div>
            <div class="bubble">
                Ciao! Sono Lyra. Come posso aiutarti con la gestione della sicurezza oggi?
            </div>
        </div>
    </div>

    <div class="typing-indicator" id="typing-indicator">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    </div>

    <div id="input-area">
        <input type="text" id="message-input" placeholder="Scrivi un messaggio..." onkeypress="handleKeyPress(event)">
        <button id="send-btn" onclick="sendUserMessage()">
            <svg viewBox="0 0 24 24"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
        </button>
    </div>

    <script>
        let backend;

        // Initialize WebChannel
        new QWebChannel(qt.webChannelTransport, function(channel) {
            backend = channel.objects.backend;
        });

        function handleKeyPress(e) {
            if (e.key === 'Enter') sendUserMessage();
        }

        function sendMessage(text) {
            if (!text) return;
            addMessage(text, 'user');

            showTyping(true);

            if (backend) {
                backend.receive_message(text);
            }
        }

        function sendUserMessage() {
            const input = document.getElementById('message-input');
            const text = input.value.trim();
            if (text) {
                sendMessage(text);
                input.value = '';
            }
        }

        function addMessage(text, sender) {
            const container = document.getElementById('chat-container');

            const row = document.createElement('div');
            row.className = `message-row ${sender}`;

            // Avatar
            const avatar = document.createElement('div');
            avatar.className = `avatar ${sender}`;
            if (sender === 'lyra') {
                avatar.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2 2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z"/><path d="M4 11v2a8 8 0 0 0 16 0v-2"/><line x1="12" y1="22" x2="12" y2="15"/></svg>';
            } else {
                avatar.innerHTML = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>';
            }

            // Bubble
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            if (sender === 'lyra') {
                bubble.innerHTML = marked.parse(text);
            } else {
                bubble.textContent = text;
            }

            row.appendChild(avatar);
            row.appendChild(bubble);

            container.appendChild(row);
            scrollToBottom();
        }

        function showTyping(show) {
            const indicator = document.getElementById('typing-indicator');
            const container = document.getElementById('chat-container');

            if (show) {
                indicator.style.display = 'flex';
                // Scroll to include typing indicator
                indicator.scrollIntoView({ behavior: 'smooth', block: 'end' });
            } else {
                indicator.style.display = 'none';
            }
        }

        function scrollToBottom() {
            const container = document.getElementById('chat-container');
            // Timeout to ensure DOM is updated
            setTimeout(() => {
                container.scrollTop = container.scrollHeight;
            }, 50);
        }

        // Called from Python
        function onLyraResponse(text) {
            showTyping(false);
            addMessage(text, 'lyra');
        }
    </script>
</body>
</html>
    """
