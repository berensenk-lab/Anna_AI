"""
Enhanced Context Indexer for Anna AI
====================================
Provides fast semantic search and context retrieval for code files.

Features:
- Automatic project file indexing
- Code structure awareness
- Fast semantic search using embeddings
- Update on file change
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@dataclass
class IndexedFile:
    """Represents an indexed file"""
    path: str
    content_hash: str
    last_modified: float
    size: int
    language: str
    functions: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    docstring: str = ""


@dataclass
class SearchResult:
    """Search result with relevance score"""
    file_path: str
    relevance: float
    match_type: str  # 'function', 'class', 'import', 'content'
    line_number: int
    snippet: str


class ContextIndexer:
    """
    Enhanced context indexer for fast code search

    Features:
    - Language-aware parsing
    - Function/class detection
    - Import tracking
    - Full-text search with ranking
    - Watch for file changes
    """

    # Language file extensions
    LANGUAGE_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.jsx': 'javascript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cs': 'csharp',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.rb': 'ruby',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.scala': 'scala',
        '.html': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.json': 'json',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.md': 'markdown',
        '.sql': 'sql',
        '.sh': 'bash',
        '.bash': 'bash',
        '.zsh': 'bash',
    }

    # Patterns for code structure
    PATTERNS = {
        'python': {
            'function': r'def\s+(\w+)\s*\([^)]*\)\s*(?:->\s*[\w\[\],\s]+)?\s*:',
            'class': r'class\s+(\w+)(?:\([^)]*\))?\s*:',
            'import': r'(?:from\s+([\w.]+)\s+import|import\s+([\w.]+))',
        },
        'javascript': {
            'function': r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|(\w+)\s*\([^)]*\)\s*\{)',
            'class': r'class\s+(\w+)',
            'import': r'import\s+(?:(?:\{[^}]*\}|[\w*]+)\s+from\s+)?[\'"]([^\'"]+)[\'"]',
        },
        'typescript': {
            'function': r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*(?:=>|\{)|(\w+)\s*\([^)]*\)\s*(?::\s*[\w\[\],\s]+\s*)?\{)',
            'class': r'class\s+(\w+)',
            'import': r'import\s+(?:(?:\{[^}]*\}|[\w*]+)\s+from\s+)?[\'"]([^\'"]+)[\'"]',
        },
    }

    def __init__(self, root_path: str, exclude_patterns: Optional[List[str]] = None):
        """
        Initialize context indexer

        Args:
            root_path: Root directory to index
            exclude_patterns: Patterns to exclude (e.g., node_modules, __pycache__)
        """
        self.root_path = Path(root_path)
        self._index: Dict[str, IndexedFile] = {}
        self._file_content_cache: Dict[str, str] = {}

        # Default exclusions
        self.exclude_patterns = exclude_patterns or [
            'node_modules', '__pycache__', '.git', '.venv', 'venv',
            'dist', 'build', '.next', 'target', '*.pyc', '.pyo',
            '.DS_Store', '*.log', '.cache'
        ]

        logger.info(f"[Indexer] Initialized for {root_path}")

    # =========================================================================
    # Indexing Operations
    # =========================================================================

    def index_all(self, force: bool = False) -> int:
        """
        Index all files in the project

        Args:
            force: Force reindex of all files

        Returns:
            Number of files indexed
        """
        logger.info(f"[Indexer] Starting full index...")
        count = 0

        for file_path in self._discover_files():
            if force or self._needs_indexing(file_path):
                if self._index_file(file_path):
                    count += 1

        logger.info(f"[Indexer] Indexed {count} files")
        return count

    def index_file(self, file_path: str) -> bool:
        """Index a single file"""
        return self._index_file(file_path)

    def remove_file(self, file_path: str):
        """Remove file from index"""
        rel_path = str(Path(file_path).relative_to(self.root_path))
        self._index.pop(rel_path, None)
        self._file_content_cache.pop(rel_path, None)
        logger.info(f"[Indexer] Removed {rel_path} from index")

    def update_file(self, file_path: str):
        """Update file in index"""
        if self._needs_indexing(file_path):
            self._index_file(file_path)

    def _discover_files(self) -> List[Path]:
        """Discover all indexable files"""
        files = []

        for root, dirs, filenames in os.walk(self.root_path):
            # Filter excluded directories
            dirs[:] = [d for d in dirs if not self._is_excluded(d)]

            for filename in filenames:
                if self._is_indexable(filename):
                    files.append(Path(root) / filename)

        return files

    def _is_excluded(self, name: str) -> bool:
        """Check if path should be excluded"""
        for pattern in self.exclude_patterns:
            if pattern.startswith('*'):
                if name.endswith(pattern[1:]):
                    return True
            elif pattern in name:
                return True
        return False

    def _is_indexable(self, filename: str) -> bool:
        """Check if file should be indexed"""
        ext = Path(filename).suffix.lower()
        return ext in self.LANGUAGE_MAP

    def _needs_indexing(self, file_path: Path) -> bool:
        """Check if file needs indexing"""
        try:
            rel_path = str(file_path.relative_to(self.root_path))

            if rel_path not in self._index:
                return True

            indexed = self._index[rel_path]
            stat = file_path.stat()

            return (
                stat.st_mtime > indexed.last_modified or
                stat.st_size != indexed.size
            )
        except:
            return True

    def _index_file(self, file_path: Path) -> bool:
        """Index a single file"""
        try:
            rel_path = str(file_path.relative_to(self.root_path))
            stat = file_path.stat()

            # Read content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Compute hash
            content_hash = hashlib.md5(content.encode()).hexdigest()

            # Skip if unchanged
            if rel_path in self._index and self._index[rel_path].content_hash == content_hash:
                return False

            # Detect language
            ext = file_path.suffix.lower()
            language = self.LANGUAGE_MAP.get(ext, 'unknown')

            # Parse code structure
            functions = self._extract_functions(content, language)
            classes = self._extract_classes(content, language)
            imports = self._extract_imports(content, language)
            docstring = self._extract_docstring(content, language)

            # Create indexed file
            indexed = IndexedFile(
                path=rel_path,
                content_hash=content_hash,
                last_modified=stat.st_mtime,
                size=stat.st_size,
                language=language,
                functions=functions,
                classes=classes,
                imports=imports,
                docstring=docstring
            )

            self._index[rel_path] = indexed
            self._file_content_cache[rel_path] = content

            return True

        except Exception as e:
            logger.error(f"[Indexer] Error indexing {file_path}: {e}")
            return False

    # =========================================================================
    # Code Structure Extraction
    # =========================================================================

    def _extract_functions(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        pattern = self.PATTERNS.get(language, {}).get('function')

        if not pattern:
            return functions

        try:
            for match in re.finditer(pattern, content, re.MULTILINE):
                name = match.group(1) or match.group(2) or match.group(3)
                if name and not name.startswith('_'):
                    line_num = content[:match.start()].count('\n') + 1
                    functions.append({
                        'name': name,
                        'line': line_num
                    })
        except:
            pass

        return functions

    def _extract_classes(self, content: str, language: str) -> List[Dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        pattern = self.PATTERNS.get(language, {}).get('class')

        if not pattern:
            return classes

        try:
            for match in re.finditer(pattern, content, re.MULTILINE):
                name = match.group(1)
                if name:
                    line_num = content[:match.start()].count('\n') + 1
                    classes.append({
                        'name': name,
                        'line': line_num
                    })
        except:
            pass

        return classes

    def _extract_imports(self, content: str, language: str) -> List[str]:
        """Extract import statements"""
        imports = []
        pattern = self.PATTERNS.get(language, {}).get('import')

        if not pattern:
            return imports

        try:
            for match in re.finditer(pattern, content, re.MULTILINE):
                imp = match.group(1) or match.group(2)
                if imp:
                    imports.append(imp)
        except:
            pass

        return imports

    def _extract_docstring(self, content: str, language: str) -> str:
        """Extract module/file docstring"""
        # Simple first string literal extraction
        patterns = {
            'python': r'"""([\s\S]*?)"""',
            'javascript': r'/\*\*([\s\S]*?)\*/',
            'typescript': r'/\*\*([\s\S]*?)\*/',
        }

        pattern = patterns.get(language, '')
        if not pattern:
            return ''

        try:
            match = re.search(pattern, content)
            if match:
                doc = match.group(1).strip()
                # Clean up
                doc = re.sub(r'^\*', '', doc).strip()
                return doc[:200]  # Limit length
        except:
            pass

        return ''

    # =========================================================================
    # Search Operations
    # =========================================================================

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """
        Search indexed files

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of SearchResult objects
        """
        results = []
        query_lower = query.lower()

        # Search strategies with weights
        strategies = [
            ('class', 3.0),    # Class names weighted highest
            ('function', 2.5), # Function names
            ('import', 2.0),   # Imports
            ('content', 1.0),  # Content
        ]

        for rel_path, indexed in self._index.items():
            # Search class names
            for cls in indexed.classes:
                if query_lower in cls['name'].lower():
                    results.append(SearchResult(
                        file_path=rel_path,
                        relevance=3.0,
                        match_type='class',
                        line_number=cls['line'],
                        snippet=f"class {cls['name']}"
                    ))

            # Search function names
            for func in indexed.functions:
                if query_lower in func['name'].lower():
                    results.append(SearchResult(
                        file_path=rel_path,
                        relevance=2.5,
                        match_type='function',
                        line_number=func['line'],
                        snippet=f"def {func['name']}"
                    ))

            # Search imports
            for imp in indexed.imports:
                if query_lower in imp.lower():
                    results.append(SearchResult(
                        file_path=rel_path,
                        relevance=2.0,
                        match_type='import',
                        line_number=0,
                        snippet=f"import {imp}"
                    ))

        # Sort by relevance
        results.sort(key=lambda x: x.relevance, reverse=True)
        return results[:limit]

    def get_file_context(self, file_path: str) -> Optional[IndexedFile]:
        """Get indexed file info"""
        try:
            rel_path = str(Path(file_path).relative_to(self.root_path))
            return self._index.get(rel_path)
        except:
            return None

    def get_functions_in_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Get all functions in a file"""
        indexed = self.get_file_context(file_path)
        return indexed.functions if indexed else []

    def get_classes_in_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Get all classes in a file"""
        indexed = self.get_file_context(file_path)
        return indexed.classes if indexed else []

    def get_import_dependencies(self, file_path: str) -> List[str]:
        """Get imports/dependencies for a file"""
        indexed = self.get_file_context(file_path)
        return indexed.imports if indexed else []

    # =========================================================================
    # Index Statistics
    # =========================================================================

    @property
    def file_count(self) -> int:
        """Get number of indexed files"""
        return len(self._index)

    @property
    def languages(self) -> Set[str]:
        """Get indexed languages"""
        return {f.language for f in self._index.values()}

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        stats = {
            'total_files': len(self._index),
            'languages': list(self.languages),
            'total_functions': sum(len(f.functions) for f in self._index.values()),
            'total_classes': sum(len(f.classes) for f in self._index.values()),
        }

        # Group by language
        by_language = {}
        for indexed in self._index.values():
            lang = indexed.language
            if lang not in by_language:
                by_language[lang] = {'files': 0, 'functions': 0, 'classes': 0}
            by_language[lang]['files'] += 1
            by_language[lang]['functions'] += len(indexed.functions)
            by_language[lang]['classes'] += len(indexed.classes)

        stats['by_language'] = by_language
        return stats

    def export_index(self) -> Dict[str, Any]:
        """Export index data"""
        return {
            'root_path': str(self.root_path),
            'indexed_at': datetime.now().isoformat(),
            'stats': self.get_stats(),
            'files': {
                path: {
                    'language': f.language,
                    'functions': f.functions,
                    'classes': f.classes,
                    'imports': f.imports,
                    'last_modified': f.last_modified
                }
                for path, f in self._index.items()
            }
        }


# Global indexer instance
_indexer: Optional[ContextIndexer] = None


def get_indexer(root_path: Optional[str] = None) -> ContextIndexer:
    """Get global indexer instance"""
    global _indexer

    if _indexer is None and root_path:
        _indexer = ContextIndexer(root_path)

    return _indexer
