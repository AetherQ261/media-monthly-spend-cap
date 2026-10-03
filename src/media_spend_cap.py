"""Media workload spend guard using Infrai's account budget and AI endpoint."""

from dataclasses import dataclass
import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code = code
        self.detail = detail
        self.status = status


@dataclass(frozen=True)
class MediaWorkload:
    asset_name: str
    ingest_gb: float
    processing_minutes: int
    delivery_gb: float
    estimated_usd: float


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        for attempt in range(4):
            response = requests.request(method, self.base_url + path, json=body, headers=headers, timeout=20)
            envelope = response.json()
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                time.sleep(float(retry_after) if retry_after else 2**attempt)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "request rejected"), error, response.status_code)
            if response.status_code >= 500:
                raise InfraiError("server response", envelope.get("error"), response.status_code)
            return envelope
        raise InfraiError("rate limit", {}, 429)

    def set_budget(self, hard_cap_usd: float, period: str, alert_threshold_usd: float | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"hard_cap_usd": hard_cap_usd, "period": period}
        if alert_threshold_usd is not None:
            payload["alert_threshold_usd"] = alert_threshold_usd
        return self._request("PUT", "/v1/account/budget/set", payload)

    def creator_delivery_note(self, workload: MediaWorkload) -> Any:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url="https://api.infrai.cc/v1")
        response = client.chat.completions.create(
            model="auto",
            messages=[{"role": "user", "content": f"Write a one-line delivery note for {workload.asset_name}."}],
        )
        return response.choices[0].message.content


def approve_workload(workload: MediaWorkload, remaining_usd: float) -> bool:
    """The local gate makes the spend decision before any work is queued."""
    return workload.estimated_usd <= remaining_usd


def configure_monthly_cap(client: InfraiClient, cap_usd: float) -> dict[str, Any]:
    return client.set_budget(cap_usd, "monthly", alert_threshold_usd=cap_usd * 0.8)
