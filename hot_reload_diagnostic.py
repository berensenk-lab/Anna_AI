#!/usr/bin/env python3
"""
Hot Reload Diagnostic Script
Checks why hot reloading isn't working
"""

def check_hot_reload_status():
    """Run diagnostic checks on hot reload system"""
    
    print("=" * 70)
    print("HOT RELOAD DIAGNOSTIC")
    print("=" * 70)
    
    # Check 1: Watchdog availability
    print("\n[1] Checking watchdog installation...")
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        print("    [OK] watchdog is installed")
        watchdog_available = True
    except ImportError:
        print("    [FAIL] watchdog is NOT installed")
        print("    Run: pip install watchdog")
        watchdog_available = False
    
    # Check 2: Controls setting
    print("\n[2] Checking ENABLE_CORE_HOT_RELOAD setting...")
    try:
        from personality import controls
        enable_core = getattr(controls, 'ENABLE_CORE_HOT_RELOAD', None)
        enable_tool = getattr(controls, 'ENABLE_TOOL_HOT_RELOAD', None)
        
        print(f"    ENABLE_CORE_HOT_RELOAD = {enable_core}")
        print(f"    ENABLE_TOOL_HOT_RELOAD = {enable_tool}")
        
        if not enable_core:
            print("    [WARNING] ENABLE_CORE_HOT_RELOAD is False")
            print("    Set to True in personality/controls.py")
    except Exception as e:
        print(f"    [ERROR] Could not check controls: {e}")
    
    # Check 3: File paths
    print("\n[3] Checking constructor file paths...")
    from pathlib import Path
    
    project_root = Path.cwd()
    base_path = project_root / 'BASE' / 'core'
    
    constructors = [
        ('reactive', base_path / 'reactive' / 'reactive_constructor.py'),
        ('reflective', base_path / 'reflective' / 'reflective_constructor.py'),
        ('proactive', base_path / 'proactive' / 'proactive_constructor.py'),
        ('action', base_path / 'action' / 'action_constructor.py'),
        ('responsive', base_path / 'responsive' / 'responsive_constructor.py'),
    ]
    
    for name, path in constructors:
        exists = path.exists()
        status = "[OK]" if exists else "[MISSING]"
        print(f"    {status} {name}: {path}")
    
    # Check 4: Module imports
    print("\n[4] Checking module imports...")
    import sys
    
    modules_to_check = [
        'BASE.core.reactive.reactive_constructor',
        'BASE.core.reflective.reflective_constructor',
        'BASE.core.proactive.proactive_constructor',
        'BASE.core.action.action_constructor',
        'BASE.core.responsive.responsive_constructor',
    ]
    
    for module_name in modules_to_check:
        if module_name in sys.modules:
            print(f"    [OK] {module_name} is loaded")
        else:
            print(f"    [NOT LOADED] {module_name}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    issues = []
    if not watchdog_available:
        issues.append("Install watchdog: pip install watchdog")
    
    if not enable_core:
        issues.append("Set ENABLE_CORE_HOT_RELOAD = True in personality/controls.py")
    
    if issues:
        print("\n[ACTION REQUIRED]")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print("\n[OK] Hot reload should be working!")
        print("\nTo test:")
        print("  1. Start the application")
        print("  2. Edit a constructor file (e.g., reactive_constructor.py)")
        print("  3. Save the file")
        print("  4. Check logs for '[Hot Reload] Reloading:' messages")
    
    print("\n")


if __name__ == "__main__":
    check_hot_reload_status()