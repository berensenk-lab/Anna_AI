/**
 * Ollama Client for Anna AI VSCode Extension
 * ==========================================
 * Handles communication with Ollama API
 */

import * as vscode from "vscode";

export interface ChatMessage {
  role: "user" | "assistant" | "system";
  content: string;
}

export interface OllamaResponse {
  model: string;
  message: ChatMessage;
  done: boolean;
}

export class OllamaClient {
  private endpoint: string;
  private model: string;

  constructor() {
    const config = vscode.workspace.getConfiguration("annaAI");
    this.endpoint = config.get<string>("endpoint", "http://localhost:11434");
    this.model = config.get<string>("model", "llama2");
  }

  /**
   * Send chat request to Ollama
   */
  async chat(messages: ChatMessage[]): Promise<string> {
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

      const data: OllamaResponse = await response.json();
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
  async checkHealth(): Promise<boolean> {
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
  async listModels(): Promise<string[]> {
    try {
      const response = await fetch(`${this.endpoint}/api/tags`);
      if (!response.ok) return [];

      const data = await response.json();
      return data.models?.map((m: any) => m.name) || [];
    } catch {
      return [];
    }
  }
}
