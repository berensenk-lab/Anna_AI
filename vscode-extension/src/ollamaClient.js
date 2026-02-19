/**
 * Ollama Client for Anna AI VSCode Extension
 * ==========================================
 * Handles communication with Ollama API
 */

const vscode = require("vscode");

class OllamaClient {
  constructor() {
    const config = vscode.workspace.getConfiguration("annaAI");
    this.endpoint = config.get("endpoint", "http://localhost:11434");
    this.model = config.get("model", "llama2");
  }

  /**
   * Send chat request to Ollama
   */
  async chat(messages) {
    try {
      const response = await fetch(`${this.endpoint}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: this.model,
          messages: messages,
          stream: false,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.message.content;
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown error";
      vscode.window.showErrorMessage(`Ollama Error: ${message}`);
      return `Error: ${message}`;
    }
  }

  /**
   * Check if Ollama is available
   */
  async checkHealth() {
    try {
      const response = await fetch(`${this.endpoint}/api/tags`);
      return response.ok;
    } catch {
      return false;
    }
  }

  /**
   * Get available models
   */
  async listModels() {
    try {
      const response = await fetch(`${this.endpoint}/api/tags`);
      if (!response.ok) return [];

      const data = await response.json();
      return data.models ? data.models.map((m) => m.name) : [];
    } catch {
      return [];
    }
  }
}

module.exports = { OllamaClient };
