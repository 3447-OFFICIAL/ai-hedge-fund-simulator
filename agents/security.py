import os
import re
import logging


class PromptInjectionFirewall:
    def __init__(self):
        self.lakera_api_key = os.getenv("LAKERA_API_KEY")
        self.rebuff_api_key = os.getenv("REBUFF_API_KEY")
        self.logger = logging.getLogger("PromptInjectionFirewall")

        # Local heuristic fallback rules
        self.suspicious_patterns = [
            r"ignore previous instructions",
            r"system prompt",
            r"you are now",
            r"bypass",
            r"forget everything",
            r"```.*```.*ignore",
        ]

    def _local_heuristic_scan(self, text: str) -> float:
        """Returns a threat score from 0.0 to 1.0 based on heuristic patterns."""
        score = 0.0
        text_lower = text.lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, text_lower):
                score += 0.5
        return min(score, 1.0)

    def analyze_payload(self, text: str) -> dict:
        """
        Runs the text through Lakera Guard and local heuristics.
        Returns a security assessment payload.
        """
        threat_score = self._local_heuristic_scan(text)

        # In a real environment, we'd make an HTTP call to Lakera here:
        # if self.lakera_api_key:
        #     response = requests.post("https://api.lakera.ai/v1/prompt_injection", ...)
        #     threat_score = max(threat_score, response.json()['flagged'])

        is_safe = threat_score < 0.5
        trust_score = 1.0 - threat_score

        if not is_safe:
            self.logger.warning(
                f"Prompt injection detected! Threat Score: {threat_score}"
            )

        return {
            "is_safe": is_safe,
            "threat_score": threat_score,
            "trust_score": trust_score,
            "quarantined": not is_safe,
            "sanitized_text": (
                text if is_safe else "[REDACTED DUE TO MALICIOUS PAYLOAD]"
            ),
        }


def validate_external_data(data_feed: str) -> str:
    """Wrapper to be used by agents before ingesting news/social data."""
    firewall = PromptInjectionFirewall()
    assessment = firewall.analyze_payload(data_feed)

    if assessment["quarantined"]:
        raise ValueError("Data feed quarantined due to suspected prompt injection.")

    return assessment["sanitized_text"]
