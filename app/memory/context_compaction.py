def compact_context(history, max_items=10):
    # simple compaction: keep last N items
    return history[-max_items:]

