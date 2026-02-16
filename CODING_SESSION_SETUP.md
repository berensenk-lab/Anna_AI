# Session Files Setup Guide for Coding Tasks

## What Are Session Files?

Session Files are a way to upload relevant project files to Anna AI before coding tasks. This gives Anna complete context about your project structure, naming conventions, and architectural patterns without needing to refetch files repeatedly.

---

## Before Every Coding Task: Upload These Files

### 1. **Project Structure File** (NEW - Optional but Recommended)
   - **File**: `personality/base_memory/base_personality/coding_context.py`
   - **Why**: Pre-populate this with your project layout, file mappings, and coding conventions
   - **When**: Do this ONCE at the start of a coding session; Anna remembers it for all tasks
   - **How**: Edit this file with your actual project structure, then upload it as a Session File

### 2. **Key Architecture Files** (Choose the files most relevant to your project)

#### For Python Projects (FastAPI, Django, Flask):
   - `main.py` or `app.py` – entry point
   - `api/routes.py` or `views.py` – HTTP endpoints
   - `models.py` or `schemas.py` – data structures
   - `config/settings.py` – configuration
   - `services/database.py` – database logic
   - `requirements.txt` – dependencies

#### For JavaScript/TypeScript Projects (Node, Express, Next.js):
   - `index.js` or `server.js` – entry point
   - `routes/` or `controllers/` – API endpoints
   - `models.ts` or `types.ts` – type definitions
   - `config.ts` or `.env` – configuration
   - `package.json` – dependencies
   - `tsconfig.json` (if TypeScript) – compiler settings

#### For Go Projects:
   - `main.go` – entry point
   - `routes.go` or `handlers/` – HTTP handlers
   - `models.go` or `types.go` – data structures
   - `config/config.go` – configuration
   - `go.mod` – dependencies

#### For Rust Projects:
   - `main.rs` or `lib.rs` – entry point
   - `routes.rs` or `handlers.rs` – handlers
   - `models.rs` or `types.rs` – data structures
   - `Cargo.toml` – dependencies

---

## Step-by-Step: Setting Up for a Coding Task

### Example Workflow: "Add user authentication to my FastAPI app"

1. **Before asking Anna**: Upload these Session Files:
   ```
   ✓ personality/base_memory/base_personality/coding_context.py (with your project info filled in)
   ✓ main.py (FastAPI entry point)
   ✓ api/routes.py (current routes)
   ✓ api/models.py (data schemas)
   ✓ services/auth.py (existing auth logic, if any)
   ✓ config/settings.py (config)
   ```

2. **Tell Anna**:
   ```
   "I've uploaded my FastAPI project structure. Add user authentication 
    following the same patterns as existing code. Use JWT tokens stored 
    in a database table and add a login endpoint to api/routes.py"
   ```

3. **What Anna will do**:
   - Load your coding_context.py to understand project layout
   - Check each uploaded file to understand existing patterns
   - Add authentication following your project's conventions
   - Use verify to confirm changes

4. **Result**: Consistent, well-integrated authentication code

---

## Why This Matters for Better Context

### Without Session Files (slower, less accurate):
```
You: "Add error handling to my functions"
Anna: (generic response)
   - Doesn't know your error handling pattern
   - Doesn't know your logging setup
   - Makes generic suggestions
   - May not match your project style
```

### With Session Files (better context, faster, more accurate):
```
You: (upload utils.py showing your error handling pattern)
You: "Add error handling to my functions"
Anna: (checks uploaded utils.py pattern)
   - Understands your specific error handling approach
   - Uses the same logging pattern you use
   - Matches your project style exactly
   - Edits are immediately usable
```

---

## Template for coding_context.py

Here's a quick template to fill out for your project:

```python
# Edit these sections in personality/base_memory/base_personality/coding_context.py

project_name = "MyAwesomeProject"
tech_stack = "Python 3.11 + FastAPI + PostgreSQL"

project_structure = """
myproject/
├── main.py (FastAPI app)
├── api/
│   ├── routes.py (all endpoints)
│   └── models.py (Pydantic schemas)
├── services/
│   ├── auth.py (JWT & passwords)
│   └── db.py (database queries)
└── config/
    └── settings.py (env variables)
"""

file_mappings = {
    "entry_point": "main.py",
    "api_routes": "api/routes.py",
    "models": "api/models.py",
    "auth": "services/auth.py",
    "database": "services/db.py",
    "config": "config/settings.py",
}

coding_conventions = """
LANGUAGE: Python 3.11
CODE STYLE: PEP 8, 88-char line length (Black formatter)
NAMING: snake_case for functions, PascalCase for classes
ERROR HANDLING: try/except with specific exception types, log with logging module
TYPE HINTS: Yes, use PEP 484
TESTING: pytest with tests/ directory
"""
```

---

## Best Practices

### ✅ DO:
- Upload `coding_context.py` **once per session** (Anna remembers it)
- Upload **key architecture files** that define patterns
- Upload **related files** for the task (if adding auth, upload auth.py + routes.py)
- Keep uploaded files **up-to-date** if you make changes between tasks
- **Tell Anna**: "Follow the patterns in [filename]"

### ❌ DON'T:
- Upload 50+ files – just key ones (structure, models, entry point)
- Upload **huge monolithic files** – ask Anna to fetch specific line ranges instead
- Forget to **update coding_context.py** when you refactor project structure
- Upload **outdated files** – make sure they match current code

---

## Examples of Good Session File Uploads

### Example 1: Python FastAPI Project
```
Uploading:
1. coding_context.py (with FastAPI setup described)
2. main.py (app creation, middleware setup)
3. api/routes.py (endpoint patterns)
4. api/models.py (Pydantic schema patterns)
5. services/auth.py (existing auth logic)

Task: "Add a new endpoint for creating users"
```

### Example 2: TypeScript/Express Project
```
Uploading:
1. coding_context.py (with Express + TypeScript setup)
2. index.ts (entry point, middleware)
3. routes/users.ts (route patterns)
4. types/User.ts (TypeScript interfaces)
5. middleware/auth.ts (auth pattern)

Task: "Add endpoint validation using Zod schema"
```

### Example 3: Go Project
```
Uploading:
1. coding_context.py (with Go setup)
2. main.go (entry point, server setup)
3. handlers/users.go (handler patterns)
4. models/user.go (struct definitions)
5. config.go (config pattern)

Task: "Add database connection and user queries"
```

---

## How Anna Uses Session Files

1. **Load coding_context.py automatically** on session start
2. **Reference uploaded files** when deciding on:
   - Naming conventions (snake_case vs camelCase)
   - Error handling patterns
   - Where to put new code
   - How to structure responses
3. **Fetch uploaded files** to understand existing patterns
4. **Follow patterns consistently** across all edits

---

## Quick Checklist

Before asking Anna for coding help:

- [ ] I've edited `personality/base_memory/base_personality/coding_context.py` with my project details
- [ ] I'm uploading `coding_context.py` as a Session File
- [ ] I'm uploading 3-5 **key architecture files** that show patterns
- [ ] I've told Anna which files define the patterns to follow
- [ ] The files I'm uploading are **current and accurate**

---

## Troubleshooting

**Problem**: "Anna doesn't understand my project structure"
**Solution**: Upload `coding_context.py` and say "I've uploaded the project context file"

**Problem**: "Anna made changes that don't match my style"
**Solution**: Upload an example file with your style, say "Please follow the patterns in [filename]"

**Problem**: "Anna keeps asking about file paths"
**Solution**: Fill in the `file_mappings` section in `coding_context.py` with your exact paths

**Problem**: "Each coding task seems disconnected"
**Solution**: In `current_session_goals` section of `coding_context.py`, list all tasks for this session

---

## Next Steps

1. **Edit `coding_context.py`** with your project information
2. **Upload it** as a Session File before your next coding task
3. **Tell Anna**: "I've uploaded my project context file with [tech stack] setup"
4. **Ask your coding question** – Anna will use all that context
