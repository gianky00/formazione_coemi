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
            --bg-color: rgba(20, 20, 40, 0.95);
            --glass-border: 1px solid rgba(100, 100, 255, 0.3);
            --accent-color: #6366f1; /* Indigo 500 */
            --text-color: #e2e8f0;
            --user-bubble: rgba(255, 255, 255, 0.1);
            --lyra-bubble: rgba(99, 102, 241, 0.15);
        }

        body {
            background-color: transparent; /* Let Qt handle the background */
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
            scrollbar-color: var(--accent-color) transparent;
        }

        /* Bubbles */
        .message {
            max-width: 85%;
            padding: 12px 16px;
            border-radius: 12px;
            font-size: 14px;
            line-height: 1.6;
            animation: fadeIn 0.3s ease-out;
            position: relative;
        }

        .user-message {
            align-self: flex-end;
            background: var(--user-bubble);
            border-bottom-right-radius: 2px;
            color: #fff;
        }

        .lyra-message {
            align-self: flex-start;
            background: var(--lyra-bubble);
            border: var(--glass-border);
            border-bottom-left-radius: 2px;
            backdrop-filter: blur(5px);
        }

        /* Typography */
        h1, h2, h3 { font-weight: 300; margin-top: 0; }
        p { margin: 0 0 10px 0; }
        p:last-child { margin: 0; }
        code { background: rgba(0,0,0,0.3); padding: 2px 5px; border-radius: 4px; font-family: monospace; }
        pre { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; overflow-x: auto; }
        ul, ol { margin: 0 0 10px 0; padding-left: 20px; }

        /* Input Area */
        #input-area {
            padding: 15px;
            background: rgba(30, 30, 60, 0.8);
            border-top: var(--glass-border);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        input {
            flex: 1;
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            padding: 10px 15px;
            color: white;
            outline: none;
            transition: border-color 0.2s;
        }
        input:focus { border-color: var(--accent-color); }

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
            transition: transform 0.2s;
        }
        button:hover { transform: scale(1.1); }

        /* Header */
        #header {
            padding: 15px 20px;
            border-bottom: var(--glass-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(30, 30, 60, 0.9);
        }
        #header-title { font-weight: 300; font-size: 18px; letter-spacing: 1px; }
        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            box-shadow: 0 0 5px #10b981;
        }
        .status-dot.thinking {
            background-color: #f59e0b;
            box-shadow: 0 0 8px #f59e0b;
            animation: pulse 1s infinite;
        }

        /* Suggestions */
        #suggestions {
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
            margin-top: auto; /* Push to bottom of empty chat */
        }
        .suggestion-chip {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 10px;
            border-radius: 20px;
            text-align: center;
            cursor: pointer;
            transition: background 0.2s;
            font-size: 13px;
        }
        .suggestion-chip:hover { background: rgba(255, 255, 255, 0.1); border-color: var(--accent-color); }

        /* Animations */
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }

        /* Neural Pulse Bar */
        #neural-pulse {
            height: 2px;
            width: 100%;
            background: linear-gradient(90deg, transparent, var(--accent-color), transparent);
            position: absolute;
            top: 0;
            left: -100%;
            animation: neuralMove 1.5s infinite linear;
            display: none;
        }
        @keyframes neuralMove { 0% { left: -100%; } 100% { left: 100%; } }

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
            <div class="suggestion-chip" onclick="sendMessage('Analisi Scadenze Settimana')">Analisi Scadenze Settimana</div>
            <div class="suggestion-chip" onclick="sendMessage('Chi manca all\'appello?')">Chi manca all'appello?</div>
            <div class="suggestion-chip" onclick="sendMessage('Sintesi Sicurezza')">Sintesi Sicurezza</div>
        </div>
    </div>

    <div style="position: relative;">
        <div id="neural-pulse"></div>
        <div id="input-area">
            <input type="text" id="message-input" placeholder="Chiedi a Lyra..." onkeypress="handleKeyPress(event)">
            <button onclick="sendUserMessage()">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
        </div>
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
            const pulse = document.getElementById('neural-pulse');
            const dot = document.getElementById('status-indicator');
            if (isThinking) {
                pulse.style.display = 'block';
                dot.classList.add('thinking');
            } else {
                pulse.style.display = 'none';
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
