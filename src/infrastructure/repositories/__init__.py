from .source import SupabaseSourceRepository
from .run import SupabaseRunRepository
from .page import SupabaseCrawledPageRepository, SupabaseParsedPageRepository
from .queue import SupabaseQueueRepository

__all__ = [
    "SupabaseSourceRepository",
    "SupabaseRunRepository",
    "SupabaseCrawledPageRepository",
    "SupabaseParsedPageRepository",
    "SupabaseQueueRepository",
]
