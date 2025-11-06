const vscode = acquireVsCodeApi();
const messages = document.getElementById('messages');
const input = document.getElementById('input');

// Load previous state if available
let isRestoring = true;
const previousState = vscode.getState();
if (previousState?.messages) {
    previousState.messages.forEach(m => appendMessage(m.text, m.sender));
}
isRestoring = false; // Now safe to save new messages

window.addEventListener('message', event => {
    const data = event.data;
    if (data.type === 'ai_message') {
        appendMessage(data.message, 'ai');
    } else {
        // appendMessage(data.message, 'misc');
    }
});

function sendUserMessage() {
    console.log('\n\nSENT USER MESSAGE!!!\n\n');
    const query = input.value.trim();
    if (!query) { return; }
    appendMessage(query, 'user');
    vscode.postMessage({ type: 'sendUserMessage', query });
    input.value = '';
    input.rows = 1;
}

function clearHistory() {
    messages.innerHTML = '';
    vscode.setState({ messages: [] });
    vscode.postMessage({ type: 'clearHistory' });
}

function appendMessage(text, sender) {
    const div = document.createElement('div');
    div.textContent = text;
    div.className = 'message ' + sender;
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;

    if (!isRestoring) {
        const currentState = vscode.getState() || { messages: [] };
        currentState.messages.push({ text, sender });
        vscode.setState(currentState);
    }
}

input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        if (e.shiftKey) {
            return;
        }
        e.preventDefault();
        sendUserMessage();
    }
});

input.addEventListener('input', () => {
    input.rows = Math.min(input.value.split('\n').length, 5);
});
