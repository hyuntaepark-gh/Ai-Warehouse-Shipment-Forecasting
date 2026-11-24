"""Restrict publicly hosted sessions while all study datasets await clearance."""
import os

PUBLIC_HOLD = (
    "Study results are awaiting publication approval. "
    "Charts, tables and downloads are unavailable in this preview."
)


def public_data_blocked(bind_address):
    """Limit data-enabled sessions to local servers outside of Render."""
    return (
        bind_address not in {"127.0.0.1", "::1", "localhost"}
        or bool(os.environ.get("RENDER"))
        or os.environ.get("WIQ_RELEASE_MODE", "local") != "local"
    )
