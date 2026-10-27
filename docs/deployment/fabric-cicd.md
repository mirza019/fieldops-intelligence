# Optional Fabric CI/CD

The scripts target the installed `fabric-cicd` 1.4 API: `FabricWorkspace` plus `publish_all_items`. They never call orphan-item deletion. Run `python scripts/deploy_powerbi.py` for local validation and dry-run, then `python scripts/deploy_powerbi.py --apply` only after confirming the tenant and workspace.

Local macOS authentication uses `InteractiveBrowserCredential`. CI uses `DefaultAzureCredential` and therefore requires an explicitly configured tenant-approved workload identity. Set `FABRIC_WORKSPACE_ID`, and optionally `AZURE_TENANT_ID` and `FABRIC_ENVIRONMENT`. Never store tokens in `.env` or source control.

Deployment does not prove refresh. After publishing, configure a cloud-accessible PostgreSQL/OneDrive/Fabric source, credentials, privacy level, and refresh; record the observed result. Missing capacity, tenant restrictions, workspace permissions, authentication, or unsupported item definitions are blockers and must not be described as success.
