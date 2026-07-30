"""Lightweight structured audit logging for M1.

PRD §22.3 calls for a persisted audit_logs table with full querying — that's
explicit Milestone 9 (Security Hardening) scope. Until then, security-relevant
events are still captured as structured log lines (parseable by any log
aggregator) so nothing is silently unobserved in the meantime.
"""

import logging
import uuid

audit_logger = logging.getLogger("billwise.audit")


def log_audit_event(action: str, *, user_id: uuid.UUID | str | None, metadata: dict | None = None) -> None:
    audit_logger.info("action=%s user_id=%s metadata=%s", action, user_id, metadata or {})
