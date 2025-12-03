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
            --glass-border: 1px solid #E5E7EB;
            --accent-color: #1D4ED8; /* Royal Blue */
            --text-color: #1F2937; /* Dark Grey */
            --user-bubble-bg: #1D4ED8;
            --user-bubble-text: #FFFFFF;
            --lyra-bubble-bg: #FFFFFF;
            --lyra-bubble-text: #1F2937;
            --input-bg: #F9FAFB;
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
            scrollbar-color: var(--accent-color) transparent;
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
            overflow-wrap: break-word;
            white-space: pre-wrap; /* Preserve newlines, wrap text */
        }

        .user-message {
            align-self: flex-end;
            background: var(--user-bubble-bg);
            color: var(--user-bubble-text);
            border-bottom-right-radius: 2px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }

        .lyra-message {
            align-self: flex-start;
            background: var(--lyra-bubble-bg);
            color: var(--lyra-bubble-text);
            border: 1px solid #E5E7EB;
            border-bottom-left-radius: 2px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        /* Markdown Styling inside Lyra messages */
        .lyra-message strong { font-weight: 600; color: #111827; }
        .lyra-message em { color: #4B5563; }
        .lyra-message code { background: #F3F4F6; padding: 2px 4px; border-radius: 4px; font-family: monospace; font-size: 0.9em; }

        /* Typography */
        h1, h2, h3 { font-weight: 600; margin-top: 0; color: #111827; }
        p { margin: 0 0 10px 0; }
        p:last-child { margin: 0; }
        ul, ol { margin: 0 0 10px 0; padding-left: 20px; }
        li { margin-bottom: 4px; }

        /* Input Area */
        #input-area {
            padding: 15px;
            background: var(--input-bg);
            border-top: var(--glass-border);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        input {
            flex: 1;
            background: #FFFFFF;
            border: 1px solid #D1D5DB;
            border-radius: 20px;
            padding: 10px 15px;
            color: var(--text-color);
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }
        input:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 3px rgba(29, 78, 216, 0.1);
        }

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
            transition: transform 0.2s, background-color 0.2s;
            box-shadow: 0 2px 4px rgba(29, 78, 216, 0.3);
        }
        button:hover {
            transform: scale(1.05);
            background-color: #1E40AF;
        }

        /* Header */
        #header {
            padding: 15px 20px;
            border-bottom: var(--glass-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #FFFFFF;
        }
        #header-title {
            font-weight: 600;
            font-size: 16px;
            color: var(--accent-color);
            letter-spacing: 0.5px;
        }

        /* Status Text */
        #status-text {
            font-size: 12px;
            color: #6B7280;
            font-style: italic;
            display: none;
            animation: pulseText 1.5s infinite;
        }

        /* Suggestions */
        #suggestions {
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
            margin-top: auto;
            padding-bottom: 5px;
        }
        .suggestion-chip {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            color: #4B5563;
            padding: 10px;
            border-radius: 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 13px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .suggestion-chip:hover {
            background: #EFF6FF;
            border-color: var(--accent-color);
            color: var(--accent-color);
        }

        /* Animations */
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes pulseText { 0% { opacity: 0.6; } 50% { opacity: 1; } 100% { opacity: 0.6; } }

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
        <div id="status-text">Sto pensando...</div>
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
            const statusText = document.getElementById('status-text');
            if (isThinking) {
                pulse.style.display = 'block';
                statusText.style.display = 'block';
            } else {
                pulse.style.display = 'none';
                statusText.style.display = 'none';
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
