/**
 * Chat Provider for Anna AI VSCode Extension
 * ===========================================
 * Provides chat webview interface for conversational AI
 */

const vscode = require("vscode");
const { OllamaClient } = require("./ollamaClient");

class ChatProvider {
  constructor(context) {
    this.viewId = "anna-ai.chatView";
    this._view = undefined;
    this._ollama = new OllamaClient();
    this._context = context;
    this._messages = [];
  }

  /**
   * Resolve the webview
   */
  resolveWebviewView(webviewView, context, token) {
    this._view = webviewView;

    webviewView.webview.options = {
      enableScripts: true,
      localResourceRoots: [
        vscode.Uri.joinPath(this._context.extensionUri, "media"),
      ],
    };

    webviewView.webview.html = this._getHtml();

    // Handle messages from webview
    webviewView.webview.onDidReceiveMessage(async (message) => {
      await this._handleMessage(message);
    });
  }

  /**
   * Send message to AI and get response
   */
  async sendMessage(prompt) {
    this._messages.push({ role: "user", content: prompt });

    const response = await this._ollama.chat(this._messages);

    this._messages.push({ role: "assistant", content: response });

    // Update webview if visible
    if (this._view) {
      this._view.webview.postMessage({
        type: "response",
        content: response,
      });
    }

    return response;
  }

  /**
   * Handle incoming messages from webview
   */
  async _handleMessage(message) {
    switch (message.type) {
      case "send":
        await this.sendMessage(message.content);
        break;

      case "clear":
        this._messages = [];
        if (this._view) {
          this._view.webview.postMessage({ type: "cleared" });
        }
        break;

      case "getContext":
        const context = this._getEditorContext();
        if (this._view) {
          this._view.webview.postMessage({
            type: "context",
            content: context,
          });
        }
        break;
    }
  }

  /**
   * Get current editor context
   */
  _getEditorContext() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return "";

    const document = editor.document;
    const selection = editor.selection;

    return JSON.stringify({
      language: document.languageId,
      fileName: document.fileName,
      selectedText: document.getText(selection),
      cursorLine: selection.active.line,
      cursorColumn: selection.active.character,
    });
  }

  /**
   * Get HTML for chat webview
   */
  _getHtml() {
    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0; padding: 10px;
            background: #1e1e1e; color: #d4d4d4;
        }
        .messages { height: calc(100vh - 120px); overflow-y: auto; }
        .message { margin: 8px 0; padding: 8px; border-radius: 4px; }
        .message.user { background: #264f78; margin-left: 20px; }
        .message.assistant { background: #2d2d2d; margin-right: 20px; }
        .input-area {
            display: flex; gap: 8px; margin-top: 10px;
        }
        input {
            flex: 1; padding: 8px; border-radius: 4px;
            background: #3c3c3c; border: 1px solid #555; color: #fff;
        }
        button {
            padding: 8px 16px; border-radius: 4px;
            background: #007acc; border: none; color: white; cursor: pointer;
        }
        button:hover { background: #005a9e; }
        .header {
            font-size: 14px; font-weight: bold; margin-bottom: 10px;
            color: #569cd6;
        }
    </style>
</head>
<body>
    <div class="header">🤖 Anna AI Chat</div>
    <div class="messages" id="messages"></div>
    <div class="input-area">
        <input type="text" id="input" placeholder="Ask Anna AI..." />
        <button id="send">Send</button>
    </div>
    <script>
        const vscode = acquireVsCodeApi();
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('input');

        document.getElementById('send').addEventListener('click', sendMessage);
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });

        function sendMessage() {
            const content = input.value.trim();
            if (!content) return;

            addMessage('user', content);
            input.value = '';

            vscode.postMessage({ type: 'send', content });
        }

        function addMessage(role, content) {
            const div = document.createElement('div');
            div.className = 'message ' + role;
            div.textContent = content;
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        window.addEventListener('message', (event) => {
            const message = event.data;
            if (message.type === 'response') {
                addMessage('assistant', message.content);
            }
        });
    </script>
</body>
</html>`;
  }
}

module.exports = { ChatProvider };
