# Filename: BASE/tools/installed/vtube_studio/tool.py
"""
VTube Studio Tool
Controls avatar expressions/animations through VTube Studio Public API.
"""

import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from BASE.handlers.base_tool import BaseTool

WEBSOCKET_AVAILABLE = True
WEBSOCKET_ERROR = None
try:
    from websocket import create_connection
except Exception as e:
    WEBSOCKET_AVAILABLE = False
    WEBSOCKET_ERROR = str(e)


class VTubeStudioTool(BaseTool):
    """Control VTube Studio via WebSocket API."""

    __slots__ = (
        "_ws_url",
        "_plugin_name",
        "_plugin_developer",
        "_token_file",
        "_auth_token",
        "_timeout",
        "_api_name",
        "_api_version",
        "_ws_client_ready",
    )

    @property
    def name(self) -> str:
        return "vtube_studio"

    async def initialize(self) -> bool:
        self._api_name = "VTubeStudioPublicAPI"
        self._api_version = "1.0"
        self._ws_url = str(
            os.getenv(
                "VTUBE_STUDIO_WS_URL",
                getattr(self._config, "vtube_studio_ws_url", "ws://127.0.0.1:8001"),
            )
        )
        self._plugin_name = str(
            getattr(self._config, "vtube_studio_plugin_name", "Anna AI")
        )
        self._plugin_developer = str(
            getattr(self._config, "vtube_studio_plugin_developer", "beren")
        )
        raw_timeout = os.getenv(
            "VTUBE_STUDIO_TIMEOUT",
            str(getattr(self._config, "vtube_studio_timeout", 5.0)),
        )
        self._timeout = self._safe_float(raw_timeout, 5.0)

        project_root = Path(getattr(self._config, "project_root", Path.cwd()))
        self._token_file = (
            project_root / "personality" / "memory" / "vtube_studio_token.json"
        )
        self._auth_token = self._load_token()
        self._ws_client_ready = WEBSOCKET_AVAILABLE

        if not self._ws_client_ready:
            if self._logger:
                self._logger.warning(
                    f"[VTubeStudio] websocket-client unavailable; tool in standby: {WEBSOCKET_ERROR}"
                )
            return True

        if self._logger:
            self._logger.system(
                f"[VTubeStudio] Initialized (ws: {self._ws_url}, plugin: {self._plugin_name})"
            )
        return True

    async def cleanup(self):
        if self._logger:
            self._logger.system("[VTubeStudio] Cleanup complete")

    def is_available(self) -> bool:
        return getattr(self, "_running", False)

    async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]:
        if not self.is_available():
            return self._error_result(
                "VTube Studio tool is not available",
                guidance="Check websocket-client installation and tool startup",
            )
        if not self._ws_client_ready:
            return self._error_result(
                "websocket-client is not installed for VTube Studio",
                guidance="Install with: pip install websocket-client",
            )

        cmd = (command or "").strip().lower()
        if cmd in ("", "emotion"):
            return await self._trigger_hotkey(args, category="emotion")
        if cmd == "animation":
            return await self._trigger_hotkey(args, category="animation")
        if cmd == "list_hotkeys":
            return await self._list_hotkeys()
        if cmd == "status":
            return await self._status()
        if cmd == "connect":
            ok, message = self._ensure_authenticated(force_token_refresh=False)
            if ok:
                return self._success_result(message)
            return self._error_result(message)

        return self._error_result(
            f"Unknown command: {command}",
            guidance="Available commands: emotion, animation, list_hotkeys, status, connect",
        )

    async def _status(self) -> Dict[str, Any]:
        ok, message = self._ensure_authenticated(force_token_refresh=False)
        if ok:
            return self._success_result(
                f"Connected to VTube Studio ({self._ws_url})",
                metadata={"ws_url": self._ws_url, "authenticated": True},
            )
        return self._error_result(
            message, metadata={"ws_url": self._ws_url, "authenticated": False}
        )

    async def _list_hotkeys(self) -> Dict[str, Any]:
        ok, msg = self._ensure_authenticated(force_token_refresh=False)
        if not ok:
            return self._error_result(msg)

        payload = self._request("HotkeysInCurrentModelRequest", {"modelID": ""})
        try:
            resp = self._send_request(payload)
            hotkeys = resp.get("data", {}).get("availableHotkeys", [])
            if not hotkeys:
                return self._error_result(
                    "No hotkeys found in current VTube Studio model"
                )

            names = [hk.get("name", "") for hk in hotkeys if hk.get("name")]
            return self._success_result(
                "Available hotkeys: " + ", ".join(names[:50]),
                metadata={"count": len(names), "hotkeys": names[:200]},
            )
        except Exception as e:
            return self._error_result(f"Failed to list hotkeys: {e}")

    async def _trigger_hotkey(self, args: List[Any], category: str) -> Dict[str, Any]:
        if not args or not args[0]:
            return self._error_result(
                f"No {category} hotkey name provided",
                guidance=f"Use: vtube_studio.{category} <hotkey_name>",
            )

        hotkey_name = str(args[0]).strip()
        ok, msg = self._ensure_authenticated(force_token_refresh=False)
        if not ok:
            return self._error_result(msg)

        # Resolve hotkey by name first for stable trigger.
        list_payload = self._request("HotkeysInCurrentModelRequest", {"modelID": ""})
        try:
            list_resp = self._send_request(list_payload)
            hotkeys = list_resp.get("data", {}).get("availableHotkeys", [])
        except Exception as e:
            return self._error_result(f"Failed to query hotkeys: {e}")

        selected = None
        target = hotkey_name.lower()
        for hk in hotkeys:
            name = str(hk.get("name", "")).strip()
            if name.lower() == target:
                selected = hk
                break
        if selected is None:
            # Loose fallback contains match
            for hk in hotkeys:
                name = str(hk.get("name", "")).strip()
                if target in name.lower():
                    selected = hk
                    break

        if selected is None:
            available = ", ".join(hk.get("name", "") for hk in hotkeys[:25])
            return self._error_result(
                f"Hotkey not found: {hotkey_name}",
                guidance=f"Use vtube_studio.list_hotkeys. Available: {available}",
            )

        trigger_payload = self._request(
            "HotkeyTriggerRequest", {"hotkeyID": selected.get("hotkeyID", "")}
        )
        try:
            self._send_request(trigger_payload)
            return self._success_result(
                f"Triggered VTube Studio {category}: {selected.get('name', hotkey_name)}",
                metadata={
                    "hotkey_name": selected.get("name", hotkey_name),
                    "hotkey_id": selected.get("hotkeyID", ""),
                },
            )
        except Exception as e:
            return self._error_result(f"Failed to trigger hotkey: {e}")

    def _ensure_authenticated(self, force_token_refresh: bool = False) -> (bool, str):
        token = None if force_token_refresh else self._auth_token

        try:
            if not token:
                token_req = self._request(
                    "AuthenticationTokenRequest",
                    {
                        "pluginName": self._plugin_name,
                        "pluginDeveloper": self._plugin_developer,
                        "pluginIcon": "",
                    },
                )
                token_resp = self._send_request(token_req)
                token = token_resp.get("data", {}).get("authenticationToken", "")
                if not token:
                    return (
                        False,
                        "VTube Studio token request failed. Approve the plugin prompt in VTube Studio.",
                    )
                self._auth_token = token
                self._save_token(token)

            auth_req = self._request(
                "AuthenticationRequest",
                {
                    "pluginName": self._plugin_name,
                    "pluginDeveloper": self._plugin_developer,
                    "authenticationToken": token,
                },
            )
            auth_resp = self._send_request(auth_req)
            authed = bool(auth_resp.get("data", {}).get("authenticated", False))
            if authed:
                return True, "VTube Studio authentication successful"

            # Token may be stale; request once again.
            if not force_token_refresh:
                return self._ensure_authenticated(force_token_refresh=True)
            return False, "VTube Studio authentication denied. Re-approve plugin in VTube Studio."
        except Exception as e:
            return False, f"VTube Studio connection/auth error: {e}"

    def _request(self, message_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "apiName": self._api_name,
            "apiVersion": self._api_version,
            "requestID": str(uuid.uuid4()),
            "messageType": message_type,
            "data": data or {},
        }

    def _send_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        ws = create_connection(self._ws_url, timeout=self._timeout)
        try:
            ws.send(json.dumps(payload))
            raw = ws.recv()
            resp = json.loads(raw)
        finally:
            ws.close()

        msg_type = resp.get("messageType", "")
        if msg_type == "APIError":
            data = resp.get("data", {})
            err = data.get("message", "Unknown VTube Studio API error")
            code = data.get("errorID", "")
            raise RuntimeError(f"{err} (errorID={code})")

        return resp

    def _load_token(self) -> Optional[str]:
        try:
            if self._token_file.exists():
                data = json.loads(self._token_file.read_text(encoding="utf-8"))
                token = data.get("authenticationToken", "")
                return token or None
        except Exception:
            pass
        return None

    def _save_token(self, token: str):
        try:
            self._token_file.parent.mkdir(parents=True, exist_ok=True)
            self._token_file.write_text(
                json.dumps({"authenticationToken": token}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            if self._logger:
                self._logger.warning(f"[VTubeStudio] Failed to save token: {e}")

    def _safe_float(self, value: Any, default: float) -> float:
        try:
            return float(value)
        except Exception:
            return default
