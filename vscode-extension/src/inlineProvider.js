/**
 * Inline Completion Provider for Anna AI VSCode Extension
 * =======================================================
 * Provides AI-powered inline code completions
 */

const vscode = require("vscode");
const { OllamaClient } = require("./ollamaClient");

class InlineCompletionProvider {
  constructor() {
    this._ollama = new OllamaClient();
    this._isEnabled = true;
    this._debounceTimer = undefined;

    // Listen for configuration changes
    vscode.workspace.onDidChangeConfiguration((e) => {
      if (e.affectsConfiguration("annaAI.enableInlineCompletion")) {
        this._isEnabled = vscode.workspace
          .getConfiguration("annaAI")
          .get("enableInlineCompletion", true);
      }
    });
  }

  /**
   * Provide inline completions
   */
  async provideInlineCompletionItems(document, position, context, token) {
    if (!this._isEnabled) {
      return [];
    }

    // Only trigger on trigger character
    if (!context.triggerCharacter && position.character > 0) {
      return [];
    }

    // Get text before cursor
    const range = new vscode.Range(
      new vscode.Position(Math.max(0, position.line - 50), 0),
      position,
    );
    const textBefore = document.getText(range);

    // Create completion request
    const messages = [
      {
        role: "system",
        content:
          "You are a code completion assistant. Complete the code naturally. Respond ONLY with the code completion, no explanations.",
      },
      {
        role: "user",
        content: `Complete this code:\n${textBefore}`,
      },
    ];

    // Debounce requests
    if (this._debounceTimer) {
      clearTimeout(this._debounceTimer);
    }

    return new Promise((resolve) => {
      this._debounceTimer = setTimeout(async () => {
        try {
          const completion = await this._ollama.chat(messages);

          if (completion && !completion.startsWith("Error:")) {
            const item = new vscode.InlineCompletionItem(
              completion.trim(),
              new vscode.Range(position, position),
            );
            item.insertTextRules =
              vscode.InlineCompletionInsertTextRule.InsertAsSnippet;
            resolve([item]);
          } else {
            resolve([]);
          }
        } catch {
          resolve([]);
        }
      }, 150);
    });
  }
}

module.exports = { InlineCompletionProvider };
