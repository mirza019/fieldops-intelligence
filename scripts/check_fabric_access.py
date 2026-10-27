from __future__ import annotations

import os
from pathlib import Path

from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from fabric_cicd import FabricWorkspace


def credential():
    if os.getenv("CI") == "true":
        return DefaultAzureCredential(exclude_interactive_browser_credential=True)
    return InteractiveBrowserCredential(tenant_id=os.getenv("AZURE_TENANT_ID") or None)


def workspace() -> FabricWorkspace:
    workspace_id = os.environ.get("FABRIC_WORKSPACE_ID")
    if not workspace_id:
        raise SystemExit("FABRIC_WORKSPACE_ID is required")
    return FabricWorkspace(
        repository_directory=str(Path(__file__).resolve().parents[1] / "powerbi"),
        token_credential=credential(),
        workspace_id=workspace_id,
        item_type_in_scope=["SemanticModel", "Report"],
        environment=os.getenv("FABRIC_ENVIRONMENT", "Development"),
    )


if __name__ == "__main__":
    target = workspace()
    print(f"Fabric workspace configuration accepted; API base is {target.base_api_url}")
