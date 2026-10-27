# Student Power BI setup

1. Sign in with the university account and inspect the license and workspace capabilities actually granted.
2. Prefer a personal/university workspace only when creation and publish permissions exist.
3. For the simplest service-refresh path, place the approved synthetic analytical snapshot in university OneDrive/SharePoint and configure the report to that URL. Cloud PostgreSQL is the alternative when a free approved instance is available.
4. Do not expose localhost PostgreSQL to the internet. A gateway is required for private/local connectivity.
5. If Fabric capacity, trials, Git integration, or service principals are unavailable, open the PBIP in Windows Power BI Desktop and publish manually to an allowed workspace.
6. Use Publish to web only for the unrestricted synthetic dataset and only after explicit disclosure approval.
