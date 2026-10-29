"""Rule-based warning-sign analysis for pasted job offers.

This module deliberately does not make claims about an employer's identity or
intent. It matches a small set of common warning signs and returns the matched
text so users can review why each signal was raised.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


MAX_TEXT_LENGTH = 12_000


@dataclass(frozen=True)
class Rule:
    key: str
    title: str
    weight: int
    explanation: str
    patterns: tuple[re.Pattern[str], ...]


@dataclass(frozen=True)
class Finding:
    key: str
    title: str
    weight: int
    evidence: str
    explanation: str


@dataclass(frozen=True)
class AnalysisResult:
    score: int
    category: str
    category_key: str
    summary: str
    findings: tuple[Finding, ...]


def _patterns(*expressions: str) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(expression, re.IGNORECASE) for expression in expressions)


RULES = (
    Rule(
        key="upfront_payment",
        title="An upfront payment is requested",
        weight=35,
        explanation=(
            "Legitimate employers generally do not require applicants to pay "
            "to apply, interview, get hired, or receive basic training. Verify "
            "any fee independently before sending money."
        ),
        patterns=_patterns(
            r"\b(?:pay|send|transfer|deposit|top\s*up|purchase)\s+"
            r"(?:(?:a|an|the|your|initial)\s+)?"
            r"(?:(?:registration|application|processing|training|interview|"
            r"security|activation|placement|clearance|administrative)\s+)?"
            r"(?:fees?|deposits?|payments?|charges?)\b",
            r"\b(?:registration|application|processing|training|interview|"
            r"security|activation|placement|clearance|administrative)\s+fees?\b",
            r"\bfees?\s+(?:are\s+)?(?:required|mandatory|must\s+be\s+paid)\b",
            r"\b(?:deposits?|payments?|charges?)\s+(?:are\s+)?"
            r"(?:required|mandatory|must\s+be\s+paid)\b",
            r"\b(?:pay|send|transfer)\s+(?:ksh|kes|usd|us\$|[$£€])?\s*"
            r"\d[\d,.]*(?:\s?(?:ksh|kes|usd|dollars?|shillings?))?\b"
            r".{0,45}\b(?:fee|deposit|training|registration|processing|slot|placement)\b",
        ),
    ),
    Rule(
        key="guaranteed_earnings",
        title="Guaranteed or unusually high earnings are promised",
        weight=20,
        explanation=(
            "Promises of guaranteed, unusually large, or easy earnings can be "
            "used to rush people into unsafe offers. Compare the pay and duties "
            "with independently verified listings."
        ),
        patterns=_patterns(
            r"\b(?:guaranteed|assured|risk[- ]free)\s+"
            r"(?:high|large|huge|unlimited|easy)\s+"
            r"(?:income|earnings?|salary|pay|profit)\b",
            r"\b(?:guaranteed|assured)\b.{0,45}\b"
            r"(?:income|earnings?|salary|pay|profit|returns?)\b",
            r"\b(?:earn|make|income|salary|pay)\b.{0,45}\b"
            r"(?:up to\s+)?(?:ksh|kes|usd|us\$|[$£€])\s*"
            r"(?:\d{1,3}(?:[,.]\d{3})+|\d{3,})"
            r"(?:\s?(?:k|thousand|million))?\b"
            r".{0,24}\b(?:per\s+(?:day|week|month|hour)|(?:a|each|every)\s+"
            r"(?:day|week|month)|daily|weekly|monthly)\b",
            r"\b(?:earn|make|paid)\b.{0,35}\b(?:up to\s+)?"
            r"(?:\d{1,3}(?:[,.]\d{3})+|\d{4,})"
            r"(?:\s?(?:k|thousand|million))?\s+"
            r"(?:per\s+(?:day|week|month)|(?:a|each|every)\s+"
            r"(?:day|week|month)|daily|weekly|monthly)\b",
        ),
    ),
    Rule(
        key="urgency",
        title="Pressure to act immediately",
        weight=15,
        explanation=(
            "Artificial deadlines and repeated demands to respond at once can "
            "make it harder to check the employer or ask someone you trust."
        ),
        patterns=_patterns(
            r"\b(?:act|apply|respond|reply|confirm|pay)\s+"
            r"(?:right\s+)?(?:now|immediately|today|urgently|within\s+"
            r"\d+\s*(?:minutes?|hours?|days?))\b",
            r"\b(?:today\s+only|limited\s+time|last\s+chance|offer\s+expires|"
            r"hurry|closing\s+soon|limited\s+(?:slots?|positions?|places?))\b",
        ),
    ),
    Rule(
        key="credentials",
        title="A password, PIN, or one-time code is requested",
        weight=35,
        explanation=(
            "Passwords, PINs, one-time passwords (OTPs), and verification "
            "codes can give someone access to your accounts or money. Never "
            "share them with a recruiter."
        ),
        patterns=_patterns(
            r"\b(?:send|share|provide|give|tell|enter|confirm|text|submit|"
            r"reply\s+with|upload)\b.{0,55}\b"
            r"(?:passwords?|passcodes?|pins?|otps?|one[- ]time\s+"
            r"(?:password|code)|verification\s+codes?|security\s+codes?|"
            r"bank(?:ing)?\s+login\s+(?:details|credentials))\b",
            r"\b(?:passwords?|passcodes?|pins?|otps?|one[- ]time\s+"
            r"(?:password|code)|verification\s+codes?|security\s+codes?)\b"
            r".{0,35}\b(?:send|share|provide|give|reply|text|submit|enter)\b",
        ),
    ),
    Rule(
        key="suspicious_contact",
        title="Contact is routed through an unusual channel",
        weight=15,
        explanation=(
            "A personal email address or chat-only contact route can make an "
            "employer harder to verify. Find the company's official website "
            "and use contact details listed there."
        ),
        patterns=_patterns(
            r"\b(?:contact|message|text|chat|call|whatsapp|telegram|signal|"
            r"dm|direct\s+message)\b.{0,45}\b"
            r"(?:whatsapp|telegram|signal|facebook|instagram|gmail|yahoo|"
            r"outlook|hotmail)\b",
            r"\b(?:only|exclusively)\b.{0,30}\b"
            r"(?:whatsapp|telegram|signal|facebook|instagram|gmail|yahoo|"
            r"outlook|hotmail)\b",
            r"\b(?:whatsapp|telegram|signal)\b.{0,30}\b"
            r"(?:only|chat|message|text|number|me)\b",
            r"\b[\w.+-]+@(?:gmail|yahoo|hotmail|outlook|protonmail)\."
            r"(?:com|co\.uk|co\.ke|com\.au)\b",
        ),
    ),
)

_NEGATION = re.compile(
    r"\b(?:no|never|not|don't|do\s+not|doesn't|does\s+not|won't|"
    r"will\s+not|without)\b(?:\W+\w+){0,7}\W*$",
    re.IGNORECASE,
)
_CLAUSE_BREAK = re.compile(r"[\n.!?;]")


def _is_negated(text: str, match_start: int) -> bool:
    """Avoid flagging a warning when the nearby text explicitly rejects it."""
    prefix = text[max(0, match_start - 110) : match_start]
    clause = _CLAUSE_BREAK.split(prefix)[-1]
    return bool(_NEGATION.search(clause))


def _first_non_negated_match(
    text: str, patterns: tuple[re.Pattern[str], ...]
) -> re.Match[str] | None:
    for pattern in patterns:
        for match in pattern.finditer(text):
            if not _is_negated(text, match.start()):
                return match
    return None


def _risk_category(score: int) -> tuple[str, str, str]:
    if score >= 70:
        return (
            "Very high",
            "very-high",
            "Several strong warning signs were matched. Pause and verify the offer independently.",
        )
    if score >= 45:
        return (
            "High",
            "high",
            "Multiple warning signs were matched. Do not send money or sensitive details before checking.",
        )
    if score >= 20:
        return (
            "Elevated",
            "elevated",
            "At least one notable warning sign was matched. Take time to verify the details.",
        )
    return (
        "Low",
        "low",
        "Few or no common warning signs matched. This does not prove the offer is safe.",
    )


def analyze_text(text: str) -> AnalysisResult:
    """Analyze a job advert and return a bounded score plus evidence.

    Raises:
        TypeError: if ``text`` is not a string.
        ValueError: if the text is blank or exceeds ``MAX_TEXT_LENGTH``.
    """
    if not isinstance(text, str):
        raise TypeError("Job advert text must be a string.")

    if not text.strip():
        raise ValueError("Paste a job advert or message to check.")

    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(
            f"Text must be {MAX_TEXT_LENGTH:,} characters or fewer."
        )

    findings: list[Finding] = []
    for rule in RULES:
        match = _first_non_negated_match(text, rule.patterns)
        if match is None:
            continue

        evidence = " ".join(match.group(0).split())
        findings.append(
            Finding(
                key=rule.key,
                title=rule.title,
                weight=rule.weight,
                evidence=evidence[:180],
                explanation=rule.explanation,
            )
        )

    score = min(100, sum(finding.weight for finding in findings))
    category, category_key, summary = _risk_category(score)
    return AnalysisResult(
        score=score,
        category=category,
        category_key=category_key,
        summary=summary,
        findings=tuple(findings),
    )
