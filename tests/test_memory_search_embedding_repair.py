"""
Regression tests for memory_search embedding consistency repair + vector retry.
"""

from unittest.mock import MagicMock

from BASE.tools.installed.memory_search.tool import MemorySearchTool


def test_medium_vector_search_repairs_embeddings_and_retries():
    tool = MemorySearchTool(config=MagicMock(), controls=MagicMock(), logger=MagicMock())

    medium_entries = [
        {"role": "user", "content": "alpha one", "embedding": [0.1]},  # wrong dim
        {"role": "assistant", "content": "alpha two"},  # missing embedding
    ]

    memory_manager = MagicMock()
    memory_manager.medium_memory = medium_entries
    memory_manager._save_medium_memory = MagicMock()
    tool.memory_manager = memory_manager

    vector_result = [{"content": "alpha two", "similarity": 0.9}]
    memory_search = MagicMock()
    memory_search.search_medium_memory = MagicMock(side_effect=[[], vector_result])
    memory_search.get_embedding_vector = MagicMock(
        side_effect=[
            [1.0, 2.0, 3.0],  # probe embedding
            [0.2, 0.3, 0.4],  # repaired embedding for alpha one
            [0.5, 0.6, 0.7],  # repaired embedding for alpha two
        ]
    )
    tool.memory_search = memory_search
    tool._vector_repair_attempted = {"medium": False, "long": False}

    results = tool._search_medium_internal("alpha", k=1)

    assert results == vector_result
    assert tool.memory_manager._save_medium_memory.call_count == 1
    assert medium_entries[0]["embedding"] == [0.2, 0.3, 0.4]
    assert medium_entries[1]["embedding"] == [0.5, 0.6, 0.7]
    assert memory_search.search_medium_memory.call_count == 2

