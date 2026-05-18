from __future__ import annotations

import re
from dataclasses import dataclass

from .models import OutboundPayloadPreview
from .utils import sha256_text


SECRET_RE = re.compile(r"(?i)(sk-[a-z0-9_-]+|token\s*=\s*[^ \n]+|api[_-]?key\s*=\s*[^ \n]+)")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
URL_RE = re.compile(r"https?://[^\s)]+")
PHONE_RE = re.compile(r"\b1[3-9]\d{9}\b")
COMPANY_RE = re.compile(r"(?i)(company|customer|client|project)[\s:=_-]+[A-Za-z0-9\u4e00-\u9fff_-]+")


@dataclass
class RedactionFinding:
    type: str
    replacement: str


def redact_text(text: str) -> tuple[str, list[RedactionFinding]]:
    redacted = text
    findings: list[RedactionFinding] = []
    patterns = [
        ("secret", SECRET_RE, "[SECRET_REDACTED]"),
        ("email", EMAIL_RE, "[EMAIL_REDACTED]"),
        ("url", URL_RE, "[URL_REDACTED]"),
        ("phone", PHONE_RE, "[PHONE_REDACTED]"),
        ("business_identifier", COMPANY_RE, "[BUSINESS_IDENTIFIER_REDACTED]"),
    ]
    for finding_type, pattern, replacement in patterns:
        matches = pattern.findall(redacted)
        if matches:
            findings.extend(RedactionFinding(type=finding_type, replacement=replacement) for _ in matches)
            redacted = pattern.sub(replacement, redacted)
    return redacted, findings


def classify_sensitivity(text: str) -> str:
    _, findings = redact_text(text)
    if findings:
        return "redacted"
    if "private key" in text.lower() or "BEGIN RSA PRIVATE KEY" in text:
        return "local_only"
    return "safe"


def create_outbound_preview(target: str, purpose: str, evidence_ids: list[str], findings: list[RedactionFinding], payload: str) -> OutboundPayloadPreview:
    return OutboundPayloadPreview(
        target=target,
        purpose=purpose,
        included_evidence_count=len(evidence_ids),
        redacted_items_count=len(findings),
        contains_raw_code=False,
        contains_original_messages=False,
        payload_digest=sha256_text(payload),
    )


def assert_no_sensitive_content(text: str) -> None:
    _, findings = redact_text(text)
    if findings:
        finding_names = ", ".join(sorted({finding.type for finding in findings}))
        raise ValueError(f"sensitive content detected: {finding_names}")
