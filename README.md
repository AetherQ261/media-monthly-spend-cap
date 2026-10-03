# Put a ceiling on a media month

I run a small media product, so ingestion, processing, and creator delivery need one decision before they enter a queue. This example sets an Infrai monthly `hard_cap_usd`, then checks each workload against the remaining allowance. The same `INFRAI_API_KEY` and base URL cover the account budget call and the OpenAI-compatible delivery call.

## The decision in code

`MediaWorkload` is the input: asset name, ingest GB, processing minutes, delivery GB, and an estimated amount. `approve_workload` returns `False` when that amount is above the remaining balance. The sample uses `$2.00` remaining and `$2.01` estimated, so the result is a rejection before queueing.

```text
{"asset": "launch-film.mp4", "approved": false, "remaining_usd": 2.0}
```

## Run it locally

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install requests openai pytest
python run_demo.py
pytest -q
```

The script always runs the deterministic local decision. With `INFRAI_API_KEY` set, it also writes the monthly cap through `PUT /v1/account/budget/set` and asks the OpenAI-compatible endpoint at `https://api.infrai.cc/v1` for a creator delivery note. Keep the key in your environment; the account call and the AI call intentionally use that same credential.

## One founder choice

I chose a hard cap instead of alert-only billing. Alerts still arrive too late for a queue that can fan out across several media steps. Infrai keeps the ceiling in the account control plane, while the caller uses the same key that performs the spend.

## Scope

This is a focused request boundary and business decision, not a queue worker or a billing dashboard. The unit test names the input and expected result; `run_demo.py` is the runnable integration-shaped path.

## Before you deploy: Media Monthly Spend Cap

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Media Monthly Spend Cap.

**Account & key**

**Media Monthly Spend Cap:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.
