# Azure Task Manager — Terraform add-ons (Insights, Log Analytics, Key Vault, Storage)

This folder provisions **only** these resources into your **existing** resource group (default: `CLOUD_PROJECT`):

1. **Log Analytics Workspace**  
2. **Application Insights** (workspace-based; links to Log Analytics)  
3. **Key Vault**  
4. **Storage Account** (+ private blob container `appdata`)

It does **not** recreate `taskmanager-api-123`, `taskmanagerpg123`, `taskmanageracr1`, or your Static Web App.

### Where to see them in the Portal (fast)

The **Home → Recent** list only shows what you opened lately — **new Terraform resources will not appear there automatically.**

**Do this instead (≈30 seconds):**

1. Portal top search → type **`CLOUD_PROJECT`** → open **Resource group** `CLOUD_PROJECT`.  
2. You should see **Log Analytics workspace**, **Application Insights**, **Key vault**, **Storage account** (names depend on your `terraform.tfvars`).  
3. Alternative: search **`All resources`** → filter **Resource group** = `CLOUD_PROJECT`.

**CLI (same check):**

```bash
az resource list --resource-group CLOUD_PROJECT --output table
```

**If the RG list has no new items:** run `terraform apply` in this folder until it says **Apply complete**, then confirm `az account show` matches the subscription you use in the Portal. See **Troubleshooting** at the bottom.

---

## Prerequisites

| Tool | Install / check |
|------|------------------|
| **Terraform** | [Install Terraform](https://developer.hashicorp.com/terraform/install) — `terraform -version` |
| **Azure CLI** | [Install Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) — `az version` |
| **Azure rights** | Your account needs permission to create resources in the subscription and resource group |

### Windows: `terraform` not found in VS Code (PATH not refreshed)

1. **Fully quit VS Code** (not only the window) and reopen it, then open a new terminal and run:
   ```powershell
   terraform --version
   ```
2. If that works in **Command Prompt** but not in VS Code, the integrated terminal is still using an old environment — restart VS Code again or sign out/in Windows.
3. **Quick workaround:** call Terraform by full path (adjust if your install dir differs):
   ```powershell
   D:\terraform\terraform.exe --version
   ```
   If that works, add **`D:\terraform`** to your user **PATH**: search Windows for **Edit environment variables** → **Environment Variables** → under your user, **Path** → **New** → `D:\terraform` → OK on all dialogs. Then restart VS Code (or reboot once so every app sees the new PATH).

---

## Step 1 — Open a terminal in this folder

**Windows (PowerShell):**

```powershell
cd c:\Users\dayan\taskmanager\infra\terraform\azure-taskmanager-addons
```

**macOS / Linux:**

```bash
cd infra/terraform/azure-taskmanager-addons
```

---

## Step 2 — Sign in to Azure

```bash
az login
```

If you have **more than one subscription**, choose the one that contains `CLOUD_PROJECT`:

```bash
az account list --output table
az account set --subscription "YOUR-SUBSCRIPTION-ID-OR-NAME"
```

Confirm:

```bash
az account show --query "{name:name, id:id}" -o table
```

---

## Step 3 — Create and edit `terraform.tfvars`

**Never commit real secrets in Git.** `terraform.tfvars` is gitignored.

**PowerShell:**

```powershell
Copy-Item terraform.tfvars.example terraform.tfvars
notepad terraform.tfvars
```

**Bash:**

```bash
cp terraform.tfvars.example terraform.tfvars
nano terraform.tfvars
```

**Edit checklist:**

- `resource_group_name` — must match your portal RG (e.g. `CLOUD_PROJECT`).
- `location` — `East Asia` matches your requirement.
- **`key_vault_name`** — change to something **globally unique** (3–24 chars, **letters and digits only**, e.g. `kvtaskmgrdevyourname01`).
- **`storage_account_name`** — change to something **globally unique** (3–24 chars, **lowercase letters and digits only**, e.g. `sttaskmgryourname01`).
- If Terraform reports a **name conflict** for Log Analytics or Application Insights, set `log_analytics_name` and/or `application_insights_name` explicitly in `terraform.tfvars`.

---

## Step 4 — Initialize Terraform

Downloads the Azure provider and prepares the working directory:

```bash
terraform init
```

If you change provider version constraints later, you may need:

```bash
terraform init -upgrade
```

---

## Step 5 — Preview changes (no resources created yet)

```bash
terraform plan
```

Review the plan: you should see **create** actions for the four resource types above, all in your existing resource group.

---

## Step 6 — Apply (create resources)

**Interactive (recommended for learning):**

```bash
terraform apply
```

Type `yes` when prompted.

**Non-interactive (CI/scripts only — use with care):**

```bash
terraform apply -auto-approve
```

---

## Step 7 — Read outputs after apply

**List all outputs:**

```bash
terraform output
```

**Application Insights connection string** (sensitive — for your FastAPI `APPLICATIONINSIGHTS_CONNECTION_STRING`):

```bash
terraform output -raw application_insights_connection_string
```

**Key Vault URI** (for Portal or Key Vault references):

```bash
terraform output -raw key_vault_uri
```

**Storage account name** (non-secret):

```bash
terraform output -raw storage_account_name
```

**Storage connection string** (secret — treat like a password):

```bash
terraform output -raw storage_primary_connection_string
```

---

## Step 8 — Wire Application Insights to App Service (`taskmanager-api-123`)

Your API code already supports telemetry when this app setting exists.

### Option A — Azure Portal

1. Open [Azure Portal](https://portal.azure.com) → **App Services** → **`taskmanager-api-123`**.  
2. **Settings** → **Environment variables** (or **Configuration** → **Application settings**).  
3. **+ Add** application setting:  
   - **Name:** `APPLICATIONINSIGHTS_CONNECTION_STRING`  
   - **Value:** paste the value from `terraform output -raw application_insights_connection_string`  
4. **Save**, then **Restart** the app.

### Option B — Azure CLI

Replace the placeholder with your **resource group** and **web app name** if different:

```bash
RG="CLOUD_PROJECT"
APP="taskmanager-api-123"
CONN=$(terraform output -raw application_insights_connection_string)

az webapp config appsettings set \
  --resource-group "$RG" \
  --name "$APP" \
  --settings APPLICATIONINSIGHTS_CONNECTION_STRING="$CONN"
```

**PowerShell:**

```powershell
$RG = "CLOUD_PROJECT"
$APP = "taskmanager-api-123"
$CONN = terraform output -raw application_insights_connection_string
az webapp config appsettings set --resource-group $RG --name $APP --settings APPLICATIONINSIGHTS_CONNECTION_STRING=$CONN
```

Wait a minute, then open **Application Insights** in the Portal — you should see requests after traffic hits the API.

---

## Step 9 — Key Vault (optional next step)

Terraform created the vault and gave **your current user** (the identity running `az login`) access to manage secrets.

### 9a — Store a secret (example: database password)

**Portal:** Key Vault → **Secrets** → **Generate/Import** → name e.g. `DatabasePassword`.

**CLI:**

```bash
VAULT_NAME=$(terraform output -raw key_vault_name)
az keyvault secret set --vault-name "$VAULT_NAME" --name "DatabasePassword" --value "YOUR-PG-PASSWORD"
```

### 9b — Let App Service read the secret (Managed Identity)

1. App Service → **Identity** → **System assigned** → **On** → **Save**.  
2. Key Vault → **Access policies** (if using policy-based vault) → **Add** → select the App Service’s **principal** → **Secret** permissions: **Get**, **List**.  

   *If your vault uses **Azure RBAC** instead of policies, assign role **Key Vault Secrets User** on the vault to the App Service managed identity.*

### 9c — Reference a secret from App Service

In **Application settings**, set value to (example):

```text
@Microsoft.KeyVault(SecretUri=https://YOUR-VAULT-NAME.vault.azure.net/secrets/DatabasePassword/)
```

Use the exact URI from the secret’s **properties** in the Portal. After saving, restart the Web App.

> Your app currently reads `DATABASE_URL` as one string; for Key Vault you often store the **full** URL or build it from multiple secrets. That wiring is app-specific beyond this Terraform stack.

---

## Step 10 — Storage account

Use outputs for connection strings or SDK configuration. The **private** container name is in `terraform output storage_container_name`.

Do **not** expose the primary connection string in frontend or public repos.

---

## Troubleshooting

| Problem | What to try |
|--------|-------------|
| **I don’t see new services on Azure Home** | Home shows **Recent** visits only. Open **Resource group → `CLOUD_PROJECT`** or run `az resource list -g CLOUD_PROJECT -o table`. |
| **Name already taken** (Key Vault / Storage) | Pick new `key_vault_name` / `storage_account_name` in `terraform.tfvars`. |
| **Authorization failed** | Confirm `az account show` subscription and that you have Contributor (or equivalent) on the RG. |
| **Key Vault access denied** | Run `terraform apply` with the same user you use in `az login`; or add an access policy for your AAD user. |
| **Wrong subscription** | `az account set --subscription ...` then `terraform plan` again. |

---

## Destroy (lab only)

This deletes the Terraform-managed resources (Insights, Log Analytics workspace, Key Vault, Storage). **Data loss** — use only in non-production or after backup.

```bash
terraform destroy
```

---

## Quick command summary

```powershell
cd c:\Users\dayan\taskmanager\infra\terraform\azure-taskmanager-addons
az login
# az account set --subscription "YOUR-SUBSCRIPTION"
Copy-Item terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars (unique key_vault_name + storage_account_name)
terraform init
terraform plan
terraform apply
terraform output -raw application_insights_connection_string
```

Then set **`APPLICATIONINSIGHTS_CONNECTION_STRING`** on **`taskmanager-api-123`** and restart the app.
