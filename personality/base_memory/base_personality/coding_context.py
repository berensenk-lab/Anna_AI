# Filename: personality/base_memory/base_personality/coding_context.py
"""
Coding-Specific Base Memory Module
Provides Anna with persistent context about her own codebase and any active external project.

HOW TO USE:
- Anna's own codebase (below) is always loaded — no changes needed.
- When working on an external project, edit the SESSION section at the bottom.
- Save this file and restart Anna (or reload memory) to apply changes.
"""

processing_stage = 'context'

# ========================================================================
# ANNA AI — OWN CODEBASE (PERMANENT, DO NOT CLEAR)
# ========================================================================

project_name = "Anna AI"
tech_stack = "Python 3.11+ | Async/Await | Ollama LLM backend | HTTP REST (requests) | pyttsx3 / XTTS / GPT-SoVITS TTS"

project_root = r"C:\Users\beren\Anna_AI"

project_structure = """
Anna_AI/
├── BASE/                          # Core engine — the brain
│   ├── core/                      # Cognitive loop and AI processing
│   │   ├── ai_core.py             # Main AI orchestrator — start here
│   │   ├── cognitive_loop_manager.py  # Manages think → tool → respond cycle
│   │   ├── cognitive_loop_recovery.py # Handles loop failures/retries
│   │   ├── processing_delegator.py    # Routes work to action/reactive/reflective
│   │   ├── response_decider.py        # Decides whether/how to respond
│   │   ├── thought_processor.py       # Processes model thoughts before acting
│   │   ├── thought_buffer.py          # Buffers streamed thought tokens
│   │   ├── thinking_modes.py          # Switches between thinking strategies
│   │   ├── context_detector.py        # Detects conversation context type
│   │   ├── config.py                  # Runtime config loader
│   │   ├── logger.py                  # Structured logging system
│   │   ├── action/                    # Action execution pipeline
│   │   ├── proactive/                 # Proactive behavior (Anna initiates)
│   │   ├── reactive/                  # Reactive behavior (responds to events)
│   │   └── reflective/                # Reflective/background processing
│   │
│   ├── handlers/                  # Tool and chat infrastructure
│   │   ├── base_tool.py           # BaseTool class — ALL tools inherit this
│   │   ├── tool_manager.py        # Loads, routes, and manages tools
│   │   ├── tool_lifecycle.py      # Tool start/stop/reload lifecycle
│   │   ├── tool_instruction_builder.py  # Builds tool prompts from information.json
│   │   ├── internal_tool_manager.py     # Manages internal (non-user) tools
│   │   ├── internal_tool_interface.py   # Interface for internal tools
│   │   ├── chat_engagement.py     # Chat session management
│   │   ├── chat_event_converter.py # Converts chat events to internal format
│   │   ├── content_filter.py      # Filters/sanitizes content
│   │   └── tts_interface.py       # TTS engine interface
│   │
│   ├── tools/
│   │   ├── installed/             # User-facing tools (coding, calendar, etc.)
│   │   │   └── coding_VS_Code/    # VS Code integration tool
│   │   │       ├── tool.py        # CodingTool class (search/tree/patch added)
│   │   │       └── information.json  # Tool commands and guidance for Anna
│   │   └── internal/              # Internal tools (TTS engines, etc.)
│   │
│   ├── memory/                    # Memory and storage systems
│   ├── services/                  # Shared services (DB, queues, etc.)
│   ├── interface/                 # External interface layer
│   ├── database.py                # Database connection and setup
│   ├── models.py                  # SQLAlchemy/data models
│   ├── structured_logger.py       # Advanced structured logging
│   ├── queue_manager.py           # Async task queue
│   └── performance_monitor.py     # Performance tracking
│
├── personality/                   # Anna's identity and configuration
│   ├── bot_info.py                # Model config, agent name, username
│   ├── controls.py                # Feature flags and tool enable/disable
│   ├── config.json                # Runtime configuration (context size, etc.)
│   ├── base_memory/
│   │   └── base_personality/
│   │       └── coding_context.py  # THIS FILE — coding memory
│   ├── prompts/
│   │   └── personality_prompt_parts.py  # Personality and coding prompts
│   ├── memory/                    # Session and long-term memory
│   ├── voice/                     # Voice configuration
│   └── avatar/                    # Avatar/visual configuration
"""

# ========================================================================
# FILE MAPPINGS — Anna's own codebase
# ========================================================================

file_mappings = {
    # Core engine
    "ai_core":               "BASE/core/ai_core.py",
    "cognitive_loop":        "BASE/core/cognitive_loop_manager.py",
    "thought_processor":     "BASE/core/thought_processor.py",
    "response_decider":      "BASE/core/response_decider.py",
    "processing_delegator":  "BASE/core/processing_delegator.py",
    "config":                "BASE/core/config.py",
    "logger":                "BASE/core/logger.py",

    # Handlers
    "base_tool":             "BASE/handlers/base_tool.py",
    "tool_manager":          "BASE/handlers/tool_manager.py",
    "tool_lifecycle":        "BASE/handlers/tool_lifecycle.py",
    "tool_instruction_builder": "BASE/handlers/tool_instruction_builder.py",
    "tts_interface":         "BASE/handlers/tts_interface.py",

    # Coding tool
    "coding_tool":           "BASE/tools/installed/coding_VS_Code/tool.py",
    "coding_info":           "BASE/tools/installed/coding_VS_Code/information.json",

    # Personality
    "bot_info":              "personality/bot_info.py",
    "controls":              "personality/controls.py",
    "config_json":           "personality/config.json",
    "personality_prompts":   "personality/prompts/personality_prompt_parts.py",
    "coding_context":        "personality/base_memory/base_personality/coding_context.py",
}

# ========================================================================
# CODING CONVENTIONS — Anna AI codebase
# ========================================================================

coding_conventions = """
LANGUAGE: Python 3.11+

ARCHITECTURE PATTERN:
- All tools inherit from BaseTool (BASE/handlers/base_tool.py)
- Tools implement: initialize(), cleanup(), is_available(), execute()
- execute() routes to _handle_<command>() methods
- Helper methods are prefixed with _ and placed after handlers
- Use self._logger for logging, self._config for config access
- Return self._success_result() or self._error_result() — never raw dicts

ASYNC:
- All tool handlers are async (async def _handle_*)
- Internal HTTP helpers (_fetch_file_content, etc.) are synchronous
- Use await only where truly async; don't force async on sync helpers

ERROR HANDLING:
- Always wrap HTTP calls in try/except requests.exceptions.RequestException
- Return self._error_result(message, metadata={...}, guidance='...') on failure
- Never let exceptions bubble up from execute() — catch at the top level
- Log errors with self._logger.error() before returning error result

LOGGING:
- self._logger.system()  → startup/lifecycle messages
- self._logger.tool()    → tool call entry points
- self._logger.success() → successful operations
- self._logger.warning() → non-fatal issues
- self._logger.error()   → failures

CODE STYLE:
- PEP 8, 4-space indentation
- Type hints on all method signatures
- Docstrings on all public methods (Args / Returns format)
- Private helpers: _leading_underscore
- Constants: UPPER_SNAKE_CASE
- No magic numbers — use named variables

IMPORTS:
- Standard library first
- Third-party second (requests, etc.)
- Local/BASE imports third
- Guard optional imports with try/except (see REQUESTS_AVAILABLE pattern)

INFORMATION.JSON:
- Every tool command must have: command, args, description, format
- tool_usage_guidance must include numbered STEP-by-STEP workflow
- proactive_triggers tell Anna when to use the tool unprompted
- Always bump version string when making changes
"""

# ========================================================================
# CRITICAL PATTERNS TO PRESERVE
# ========================================================================

critical_patterns = """
1. BaseTool PATTERN (base_tool.py):
   Every tool MUST follow this structure:
   ```python
   class MyTool(BaseTool):
       @property
       def name(self) -> str: return "mytool"
       async def initialize(self) -> bool: ...
       async def cleanup(self): ...
       def is_available(self) -> bool: ...
       async def execute(self, command: str, args: List[Any]) -> Dict[str, Any]: ...
   ```
   Never skip initialize() or cleanup() — the lifecycle manager calls them.

2. RESULT FORMAT:
   Always use:
   - self._success_result(content_str, metadata={...})
   - self._error_result(message_str, metadata={...}, guidance='...')
   Never return raw {'success': True, ...} dicts from execute().

3. TOOL ROUTING in execute():
   Always use if/elif chain — never dynamic dispatch (getattr).
   Update the error message when adding new commands:
   guidance='Available commands: edit, fetch, verify, files, status, search, tree, patch'

4. INFORMATION.JSON WORKFLOW:
   tool_usage_guidance MUST have numbered STEP 1, STEP 2... steps.
   Anna reads these steps to decide what to do — they are behavioral instructions.

5. GRACEFUL DEGRADATION:
   initialize() always returns True even if the external service is unavailable.
   is_available() handles the live check — tools degrade gracefully.
"""

# ========================================================================
# FILES THAT NEED EXTRA CARE
# ========================================================================

sensitive_files = """
- BASE/handlers/base_tool.py       : ALL tools inherit this. Changes here affect every tool.
- BASE/handlers/tool_manager.py    : Changing tool loading/routing can break all tools at once.
- BASE/core/ai_core.py             : Core orchestrator. Changes here affect the entire cognitive loop.
- BASE/core/cognitive_loop_manager.py : Loop timing/flow changes can cause hangs or missed responses.
- personality/bot_info.py          : Model names must exactly match ollama list output.
- personality/controls.py          : Wrong feature flags can silently disable large subsystems.
- personality/config.json          : JSON syntax errors crash startup.

RULE: Always fetch and read these files fully before suggesting any edits.
      Always ask before making changes that affect more than one tool or subsystem.
"""

# ========================================================================
# KEY DEPENDENCIES
# ========================================================================

dependencies = """
RUNTIME:
- Python 3.11+
- Ollama (local LLM server) — models: qwen2.5-coder:7b, gemma3:12b-it-q4_K_M, nomic-embed-text
- requests — HTTP calls to Cursor/VS Code extension bridge and Ollama
- asyncio — async runtime throughout

VS CODE INTEGRATION:
- Cursor (or VS Code-compatible editor) extension bridge running on localhost:3000
- Endpoints: /edit (POST), /file (GET), /files (GET)

TTS (optional, controlled via controls.py):
- pyttsx3 — system TTS fallback
- XTTS — high quality neural TTS
- GPT-SoVITS — voice cloning TTS

VERIFY INSTALLED MODELS:
  ollama list
PULL A MODEL:
  ollama pull <model_name>
"""

# ========================================================================
# SESSION — EXTERNAL PROJECT (EDIT THIS WHEN SWITCHING PROJECTS)
# ========================================================================
# When working on a project other than Anna AI, fill this in.
# Set active_external_project = True to signal Anna to use this context.

active_external_project = False  # ← Set to True when working on an external project

external_project = {
    "name": "",                    # e.g. "MyWebApp"
    "root": "",                    # e.g. r"C:\Users\beren\Projects\MyWebApp"
    "tech_stack": "",              # e.g. "FastAPI + React + PostgreSQL"
    "entry_point": "",             # e.g. "main.py" or "src/index.ts"
    "key_files": {
        # "logical_name": "relative/path/from/root"
    },
    "conventions": "",             # Brief style notes for this project
    "notes": "",                   # Anything Anna should know before touching code
}

# ========================================================================
# SESSION FOCUS (UPDATE EACH CODING SESSION)
# ========================================================================

current_session_focus = ""
# Example: "Adding search/tree/patch commands to the coding tool"

current_session_goals = []
# Example: ["Improve edit guidance", "Update information.json", "Test via coding.verify"]

files_in_focus_this_session = []
# Example: ["BASE/tools/installed/coding_VS_Code/tool.py",
#           "BASE/tools/installed/coding_VS_Code/information.json"]

# ========================================================================
# TOOL USAGE EXAMPLES — updated for v3.0.0 commands
# ========================================================================

tool_usage_examples = {
    "orient":        'coding.files []',
    "fetch_file":    'coding.fetch ["BASE/tools/installed/coding_VS_Code/tool.py"]',
    "fetch_range":   'coding.fetch ["BASE/core/ai_core.py", 1, 60]',
    "edit":          'coding.edit ["add error handling following BaseTool pattern", "BASE/core/config.py"]',
    "verify":        'coding.verify ["BASE/tools/installed/coding_VS_Code/tool.py", "_handle_edit"]',
    "files":         'coding.files []',
    "status":        'coding.status []',
}

# ========================================================================
# QUICK REFERENCE FOR ANNA
# ========================================================================

quick_reference = """
MANDATORY WORKFLOW (never skip steps):
  1. coding.files   → get workspace context
  2. coding.fetch   → read before touching
  3. coding.edit    → apply focused instruction
  4. coding.verify  → confirm the change landed
  5. coding.status  → check tool state if needed

WHEN UNSURE OF A PATH:
  → coding.files [] then coding.fetch [candidate_file]
  → Never guess paths

SENSITIVE FILES (always ask before editing):
  → base_tool.py, tool_manager.py, ai_core.py, cognitive_loop_manager.py

AFTER ANY EDIT:
  → coding.verify to confirm, then briefly summarize what changed and why

IF CODING BRIDGE IS OFFLINE:
  → Use file_system tools for directory scans, file reads, and workspace cleanup tasks
"""
