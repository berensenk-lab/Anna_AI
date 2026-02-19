/**
 * Status Bar Manager for Anna AI VSCode Extension
 * ===============================================
 * Manages the VSCode status bar item
 */

const vscode = require("vscode");

class StatusBarManager {
  constructor() {
    this._statusBar = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Right,
      100,
    );
    this._statusBar.command = "anna-ai.chat";
    this._statusBar.tooltip = "Anna AI - Click to chat";
    this._statusBar.show();
  }

  /**
   * Show status in status bar
   */
  showStatus(status) {
    switch (status) {
      case "ready":
        this._statusBar.text = "$(robot) Anna AI";
        this._statusBar.backgroundColor = undefined;
        break;

      case "busy":
        this._statusBar.text = "$(sync~spin) Anna AI";
        this._statusBar.backgroundColor = new vscode.ThemeColor(
          "statusbarItem.warningBackground",
        );
        break;

      case "error":
        this._statusBar.text = "$(error) Anna AI";
        this._statusBar.backgroundColor = new vscode.ThemeColor(
          "statusbarItem.errorBackground",
        );
        break;

      case "initializing":
        this._statusBar.text = "$(sync~spin) Initializing...";
        break;
    }
  }

  /**
   * Dispose the status bar item
   */
  dispose() {
    this._statusBar.dispose();
  }
}

module.exports = { StatusBarManager };
