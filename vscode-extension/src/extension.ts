/**
 * Anna AI VSCode Extension
 * ========================
 * AI assistant integration for Visual Studio Code
 *
 * Features:
 * - Chat panel for conversational AI
 * - Code explanation and refactoring
 * - Test generation
 * - Inline AI assistance
 */

import * as vscode from "vscode";
import { ChatProvider } from "./chatProvider";
import { InlineCompletionProvider } from "./inlineProvider";
import { StatusBarManager } from "./statusBar";

// Global state
let chatProvider: ChatProvider | undefined;
let inlineProvider: InlineCompletionProvider | undefined;
let statusBar: StatusBarManager | undefined;

/**
 * Activate the extension
 */
export function activate(context: vscode.ExtensionContext): void {
  console.log("Anna AI extension activating...");

  // Initialize status bar
  statusBar = new StatusBarManager();
  statusBar.showStatus("initializing");

  // Register chat provider
  chatProvider = new ChatProvider(context);
  vscode.window.registerWebviewViewProvider(ChatProvider.viewId, chatProvider, {
    webviewOptions: { retainContextWhenHidden: true },
  });

  // Register inline completion provider
  inlineProvider = new InlineCompletionProvider();
  vscode.languages.registerInlineCompletionProvider(
    { pattern: "**" },
    inlineProvider,
  );

  // Register commands
  registerCommands(context);

  // Update status
  statusBar.showStatus("ready");
  console.log("Anna AI extension activated");
}

/**
 * Register VSCode commands
 */
function registerCommands(context: vscode.ExtensionContext): void {
  // Open chat command
  vscode.commands.registerCommand("anna-ai.chat", async () => {
    await vscode.commands.executeCommand("anna-ai.chatView.focus");
  });

  // Explain code command
  vscode.commands.registerCommand("anna-ai.explain", async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
      vscode.window.showWarningMessage("No active editor");
      return;
    }

    const selection = editor.selection;
    const selectedText = editor.document.getText(selection);

    if (!selectedText) {
      vscode.window.showWarningMessage("No code selected");
      return;
    }

    const response = await chatProvider?.sendMessage(
      `Explain this code:\n\`\`\`\n${selectedText}\n\`\`\``,
    );

    if (response) {
      vscode.window.showInformationMessage(response.slice(0, 100) + "...");
    }
  });

  // Refactor command
  vscode.commands.registerCommand("anna-ai.refactor", async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const selection = editor.selection;
    const selectedText = editor.document.getText(selection);

    if (!selectedText) {
      vscode.window.showWarningMessage("No code selected");
      return;
    }

    const response = await chatProvider?.sendMessage(
      `Refactor this code:\n\`\`\`\n${selectedText}\n\`\`\``,
    );

    if (response) {
      // Show in new document for review
      const doc = await vscode.workspace.openTextDocument({
        content: response,
        language: editor.document.languageId,
      });
      await vscode.window.showTextDocument(doc);
    }
  });

  // Generate tests command
  vscode.commands.registerCommand("anna-ai.generateTests", async () => {
    const editor = vscode.window.activeTextEditor;
    if (!editor) return;

    const selection = editor.selection;
    const selectedText = editor.document.getText(selection);

    if (!selectedText) {
      vscode.window.showWarningMessage("No code selected");
      return;
    }

    const response = await chatProvider?.sendMessage(
      `Generate unit tests for this code:\n\`\`\`\n${selectedText}\n\`\`\``,
    );

    if (response) {
      const doc = await vscode.workspace.openTextDocument({
        content: response,
        language: "javascript", // Default to JS tests
      });
      await vscode.window.showTextDocument(doc);
    }
  });

  // Health check command
  vscode.commands.registerCommand("anna-ai.checkHealth", async () => {
    const config = vscode.workspace.getConfiguration("annaAI");
    const endpoint = config.get<string>("endpoint", "http://localhost:11434");

    try {
      const response = await fetch(`${endpoint}/api/tags`);
      if (response.ok) {
        vscode.window.showInformationMessage("✅ Anna AI: Connected");
        statusBar?.showStatus("ready");
      } else {
        vscode.window.showWarningMessage("⚠️ Anna AI: Connection error");
        statusBar?.showStatus("error");
      }
    } catch (error) {
      vscode.window.showErrorMessage("❌ Anna AI: Not reachable");
      statusBar?.showStatus("error");
    }
  });
}

/**
 * Deactivate the extension
 */
export function deactivate(): void {
  console.log("Anna AI extension deactivated");
  statusBar?.dispose();
}
