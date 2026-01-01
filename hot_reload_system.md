# Hybrid Hot Reload Implementation Guide

## Overview

The hybrid approach combines:
- **Automatic dependency detection** (parses import statements)
- **Directory watching** (auto-registers all files in watched directories)
- **Smart cascade reloading** (automatically reloads dependent modules)
- **Pattern-based helper detection** (links *_parts.py files to constructors)

## Implementation Steps

### Step 1: Replace Core Hot Reload Manager

**File:** `BASE/core/core_hot_reload_manager.py`

**Action:** Replace entire file with `core_hot_reload_manager.py` from outputs

**What changed:**
- Added `watch_directory_recursively()` method
- Added `_detect_dependencies()` for auto-parsing imports
- Added `_find_related_constructor()` for pattern matching
- Added `_reload_with_dependents()` for cascade reloading
- Added `dependents` tracking in ReloadableModule
- Enhanced logging with dependency information

### Step 2: Update ThoughtProcessor Registration

**File:** `BASE/core/thought_processor.py`

**Method:** `_register_constructors_for_hot_reload()` (around line 117)

**Action:** Replace with content from `thought_processor_register_method.py`

**What changed:**
- Removed manual per-file registration
- Added directory watching: `watch_directory_recursively()`
- System now auto-registers ALL .py files in watched directories
- Auto-detects dependencies by parsing imports

**Old approach (manual):**
```python
self.hot_reload_manager.register_constructor(
    name='reactive_constructor',
    file_path=base_path / 'reactive' / 'reactive_constructor.py',
    module_ref=sys.modules.get('BASE.core.reactive.reactive_constructor')
)
# ... repeat for each file
```

**New approach (automatic):**
```python
self.hot_reload_manager.watch_directory_recursively(base_path / 'reactive')
# Automatically finds and registers all .py files with dependency detection!
```

### Step 3: Update ProcessingDelegator Registration

**File:** `BASE/core/processing_delegator.py`

**Method:** `_register_constructors_for_hot_reload()` (around line 169)

**Action:** Replace with content from `processing_delegator_register_method.py`

**What changed:**
- Same as ThoughtProcessor - switched to directory watching
- Auto-registers responsive_constructor and any helper files

### Step 4: Verify Installation

**Run:** `python test_hybrid_hot_reload.py`

This will check:
- New features present in core_hot_reload_manager.py
- Registration methods updated
- Dependency detection working

## How It Works

### Automatic Dependency Detection

When you register a module, the system:

1. Reads the source file
2. Parses for import statements:
   ```python
   from .proactive_parts import get_situation_awareness
   from .proactive_utils import format_context
   ```
3. Extracts dependency names: `['proactive_parts', 'proactive_utils']`
4. Builds a dependency graph automatically

### Directory Watching

When you call `watch_directory_recursively()`:

1. Scans for all `.py` files in directory
2. Skips files starting with `_` or `.`
3. Converts file paths to module paths
4. Checks if module is already loaded in `sys.modules`
5. Auto-registers with dependency detection

### Smart Cascade Reloading

When a file changes:

1. **Direct module:** If changed file is registered, reload it
2. **Helper file:** If file matches pattern (*_parts, *_utils), find parent constructor
3. **Dependents:** After reload, cascade to all modules that depend on it

**Example:**
```
Edit: proactive_parts.py
  → Reload: proactive_parts
    → Cascade to: proactive_constructor (depends on proactive_parts)
      → Update: thought_processor.proactive_constructor
```

### Pattern-Based Helper Detection

If you edit `proactive_parts.py` but it's not explicitly registered:

1. System detects the `_parts` suffix
2. Strips suffix: `proactive_parts` → `proactive`
3. Looks for: `proactive_constructor` in registered modules
4. Reloads the constructor (which will import the updated parts file)

## Usage Examples

### Example 1: Edit Helper File

**Before (old system):** Edit helper → No reload → Restart required

**After (hybrid system):**
```
1. Edit BASE/core/proactive/proactive_parts.py
2. Save file
3. System detects: "proactive_parts.py changed"
4. System reloads: proactive_constructor
5. Change active immediately!
```

### Example 2: Add New Helper File

**Create:** `BASE/core/proactive/proactive_new_helper.py`

```python
def new_function():
    return "This is new!"
```

**Update constructor:**
```python
# In proactive_constructor.py
from .proactive_new_helper import new_function  # Add this line
```

**Next time you start:**
- System auto-detects the import
- Adds `proactive_new_helper` to dependencies
- Future edits to new_helper.py will trigger reload!

### Example 3: View Dependency Graph

Add this to `ai_core.py` after hot reload initialization:

```python
if self.core_hot_reload:
    stats = self.core_hot_reload.get_statistics()
    self.logger.system("\n[Hot Reload] Dependency Graph:")
    for name, info in stats['modules'].items():
        deps = info['dependencies']
        dependents = info['dependents']
        self.logger.system(
            f"  {name}:"
            f"\n    depends on: {deps if deps else 'none'}"
            f"\n    depended by: {dependents if dependents else 'none'}"
        )
```

## Expected Log Output

### Startup:
```
[Hot Reload] Manager initialized
[Hot Reload] Auto-registered 3 modules from reactive/
[Hot Reload] Registered: reactive_constructor (depends on: reactive_parts)
[Hot Reload] Registered: reactive_parts
[Hot Reload] Auto-registered 4 modules from proactive/
[Hot Reload] Registered: proactive_constructor (depends on: proactive_parts, proactive_utils)
[Hot Reload] Registered: proactive_parts
[Hot Reload] Watching 5 directories for 12 modules
```

### File Edit:
```
[Hot Reload] Detected change: proactive_parts.py
[Hot Reload] Reloading: proactive_parts
[Hot Reload] SUCCESS: proactive_parts (#1, 0.05s)
[Hot Reload] Cascading to 1 dependent(s): proactive_constructor
[Hot Reload] Reloading: proactive_constructor
[Hot Reload] SUCCESS: proactive_constructor (#2, 0.08s)
[Hot Reload] Updated: thought_processor.proactive_constructor
```

## Benefits Over Old System

| Feature | Old System | Hybrid System |
|---------|-----------|---------------|
| Register helpers | Manual, per-file | Automatic |
| Dependency tracking | Manual list | Auto-detected from imports |
| Helper file changes | Not detected | Auto-reloads parent |
| New files | Must restart | Auto-registered on startup |
| Debugging | Limited info | Full dependency graph |
| Code maintenance | Update 2 places | Update 1 place |
| Cascade reloading | No | Yes |

## Extending to Other Subsystems

The hybrid system can be extended to any part of your codebase:

```python
# In tool_manager.py or any other system
self.hot_reload_manager.watch_directory_recursively(
    self.project_root / 'BASE' / 'tools' / 'installed'
)
# Now all tools can be hot-reloaded with dependency tracking!
```

## Troubleshooting

### Issue: "Module not found in sys.modules"
**Cause:** Module not imported yet at startup
**Fix:** Module must be imported before hot reload starts

### Issue: "Dependency detection failed"
**Cause:** Non-standard import syntax
**Fix:** Use standard: `from .module import name`

### Issue: "Helper file not triggering reload"
**Cause:** Pattern doesn't match (*_parts, *_utils, *_helpers)
**Fix:** Rename file or manually register

### Issue: "Cascade reload infinite loop"
**Cause:** Circular dependencies
**Fix:** Restructure imports to remove circular references

## Performance Notes

- Dependency detection: ~0.01s per module (one-time at startup)
- File watching: Negligible CPU usage (watchdog is efficient)
- Reload time: ~0.05-0.15s per module
- Cascade reload: Linear with number of dependents

## Future Enhancements

Possible extensions:
- GUI button to manually trigger reload of specific module
- Hot reload for tool files
- Hot reload for personality files
- Dependency visualization graph
- Reload on git checkout/branch switch
- Smart reload based on modified functions (not entire module)