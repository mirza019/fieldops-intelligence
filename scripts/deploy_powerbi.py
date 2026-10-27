from __future__ import annotations

import argparse

from fabric_cicd import publish_all_items

from scripts.check_fabric_access import workspace
from scripts.validate_powerbi import validate


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deploy FieldOps Power BI artifacts without deleting unrelated items"
    )
    parser.add_argument(
        "--apply", action="store_true", help="Publish after validation; default is dry-run"
    )
    args = parser.parse_args()
    artifacts = validate()
    print(f"Validated {len(artifacts)} local source artifacts")
    if not args.apply:
        print("Dry-run complete. Re-run with --apply after confirming workspace and identity.")
        return
    result = publish_all_items(workspace())
    print("Deployment request completed." if result is None else f"Deployment result: {result}")
    print(
        "Next: configure cloud-accessible data-source credentials and verify refresh in Power BI Service."
    )


if __name__ == "__main__":
    main()
