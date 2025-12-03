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
        :root {
            --bg-color: #FFFFFF;
            --accent-color: #1D4ED8; /* Royal Blue */
            --accent-hover: #1E40AF;
            --text-color: #1F2937;
            --text-muted: #6B7280;
            --user-bubble-bg: #1D4ED8;
            --user-bubble-text: #FFFFFF;
            --lyra-bubble-bg: #F3F4F6;
            --lyra-bubble-text: #1F2937;
            --border-color: #E5E7EB;
        }

        body {
            background-color: transparent;
            color: var(--text-color);
            font-family: 'Inter', 'Segoe UI', sans-serif;
            margin: 0;
            padding: 0;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        #chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            scrollbar-width: thin;
            scrollbar-color: #CBD5E1 transparent;
        }

        /* Bubbles */
        .message {
            max-width: 85%;
            width: fit-content;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.5;
            animation: fadeIn 0.3s ease-out;
            position: relative;
            word-wrap: break-word;
        }

        .user-message {
            align-self: flex-end;
            background: var(--user-bubble-bg);
            color: var(--user-bubble-text);
            border-bottom-right-radius: 2px;
            box-shadow: 0 2px 4px rgba(29, 78, 216, 0.2);
        }

        .lyra-message {
            align-self: flex-start;
            background: var(--lyra-bubble-bg);
            color: var(--lyra-bubble-text);
            border-bottom-left-radius: 2px;
            border: 1px solid var(--border-color);
        }

        /* Typography */
        h1, h2, h3 { font-weight: 600; margin-top: 5px; margin-bottom: 5px; font-size: 16px; }
        p { margin: 0 0 8px 0; }
        p:last-child { margin: 0; }
        code { background: #E2E8F0; padding: 2px 5px; border-radius: 4px; font-family: monospace; font-size: 12px; color: #D946EF; }
        pre { background: #1E293B; color: #F8FAFC; padding: 10px; border-radius: 8px; overflow-x: auto; font-size: 12px; }
        ul, ol { margin: 0 0 10px 0; padding-left: 20px; }
        strong { color: var(--accent-color); }

        /* Input Area */
        #input-area {
            padding: 15px;
            background: #FFFFFF;
            border-top: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        input {
            flex: 1;
            background: #F9FAFB;
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 10px 15px;
            color: var(--text-color);
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
            font-family: inherit;
        }
        input:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 2px rgba(29, 78, 216, 0.1);
        }
        input::placeholder { color: var(--text-muted); }

        button {
            background: var(--accent-color);
            border: none;
            border-radius: 50%;
            width: 36px;
            height: 36px;
            color: white;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.2s, background 0.2s;
        }
        button:hover { background: var(--accent-hover); transform: scale(1.05); }

        /* Header */
        #header {
            padding: 15px 20px;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #FFFFFF;
        }
        #header-title { font-weight: 700; font-size: 16px; color: var(--accent-color); letter-spacing: 0.5px; }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #10B981; /* Green */
            border-radius: 50%;
        }
        .status-dot.thinking {
            background-color: #F59E0B; /* Amber */
            animation: pulse 1s infinite;
        }

        /* Suggestions */
        #suggestions {
            display: flex;
            flex-direction: column;
            gap: 8px;
            margin-top: auto;
        }
        .suggestion-chip {
            background: #EFF6FF; /* Blue-50 */
            border: 1px solid #DBEAFE; /* Blue-100 */
            padding: 8px 12px;
            border-radius: 8px;
            text-align: left;
            cursor: pointer;
            transition: background 0.2s, border-color 0.2s;
            font-size: 13px;
            color: var(--accent-color);
            font-weight: 500;
        }
        .suggestion-chip:hover {
            background: #DBEAFE;
            border-color: var(--accent-color);
        }

        /* Animations */
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

    </style>
</head>
<body>
    <div id="header">
        <div id="header-title">LYRA</div>
        <div class="status-dot" id="status-indicator"></div>
    </div>

    <div id="chat-container">
        <!-- Zero State -->
        <div id="suggestions">
            <div class="suggestion-chip" onclick="sendMessage('Analisi Scadenze Settimana')">📅 Analisi Scadenze Settimana</div>
            <div class="suggestion-chip" onclick="sendMessage('Chi manca all\'appello?')">🔍 Chi manca all'appello?</div>
            <div class="suggestion-chip" onclick="sendMessage('Sintesi Sicurezza')">🛡️ Sintesi Sicurezza</div>
        </div>
    </div>

    <div id="input-area">
        <input type="text" id="message-input" placeholder="Chiedi a Lyra..." onkeypress="handleKeyPress(event)">
        <button onclick="sendUserMessage()">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
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

            // Hide suggestions if they exist
            const suggestions = document.getElementById('suggestions');
            if (suggestions) suggestions.style.display = 'none';

            setThinking(true);
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
            const div = document.createElement('div');
            div.className = `message ${sender}-message`;

            if (sender === 'lyra') {
                div.innerHTML = marked.parse(text);
            } else {
                div.textContent = text;
            }

            container.appendChild(div);
            container.scrollTop = container.scrollHeight;
        }

        function setThinking(isThinking) {
            const dot = document.getElementById('status-indicator');
            if (isThinking) {
                dot.classList.add('thinking');
            } else {
                dot.classList.remove('thinking');
            }
        }

        // Called from Python
        function onLyraResponse(text) {
            setThinking(false);
            addMessage(text, 'lyra');
        }
    </script>
</body>
</html>
    """
