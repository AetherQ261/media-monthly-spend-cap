import json

from src.media_spend_cap import InfraiClient, MediaWorkload, approve_workload, configure_monthly_cap


def main() -> None:
    workload = MediaWorkload("launch-film.mp4", 4.2, 18, 7.5, 2.01)
    remaining = 2.00
    print(json.dumps({"asset": workload.asset_name, "approved": approve_workload(workload, remaining), "remaining_usd": remaining}))
    if "INFRAI_API_KEY" in __import__("os").environ:
        client = InfraiClient()
        configure_monthly_cap(client, 50.0)
        print(client.creator_delivery_note(workload))


if __name__ == "__main__":
    main()
