# OpenTofu Infrastructure (POC 1 — Azure)

> **Status: DORMANT for POC 0** — Activated when migrating to POC 1 with $200 Azure credits

## Overview

OpenTofu (open-source Terraform fork, MIT license) IaC for deploying the Compliance Review Agent to Azure.

## POC 1 Resources (Minimal Cost)

| Resource | SKU | Estimated Cost |
|---|---|---|
| Azure OpenAI | S0 + gpt-4o-mini deployment | ~$0.15/1M tokens |
| Azure AI Search | **Free tier** (50MB, 3 indexes) | **$0** |
| Azure Blob Storage | LRS, 5GB | **$0** |
| Azure Container Apps | Scale-to-zero | **$0 when idle** |
| Azure Key Vault | 10k ops/month | **$0** |

## Usage (POC 1)

```bash
# Install OpenTofu
brew install opentofu

# Initialize
cd infra/tofu
tofu init

# Plan (review before applying)
tofu plan -var-file=environments/poc.tfvars

# Apply (uses $200 Azure credits)
tofu apply -var-file=environments/poc.tfvars

# Destroy when not demoing (saves credits)
tofu destroy -var-file=environments/poc.tfvars
```

## Files to Create for POC 1

```
infra/tofu/
├── providers.tf              # Azure provider + backend config
├── main.tf                   # Root module
├── variables.tf              # Input variables
├── outputs.tf                # Output values (endpoints, etc.)
├── versions.tf               # Provider version constraints
├── modules/
│   ├── openai/               # Azure OpenAI + model deployments
│   ├── ai_search/            # Azure AI Search (free tier)
│   ├── storage/              # Azure Blob Storage
│   ├── container_apps/       # Azure Container Apps (scale to zero)
│   ├── key_vault/            # Azure Key Vault for secrets
│   └── aks/                  # AKS (Production only - Phase 2)
└── environments/
    ├── local.tfvars          # POC 0 (no Azure resources)
        ├── poc.tfvars            # POC 1 ($200 credits)
            └── prod.tfvars           # Production (Microsoft funded)
            ```

            ## POC 0 → POC 1 Migration

            When ready to migrate from zero-cost local stack to Azure:

            1. Set up Azure subscription and enable $200 free credits
            2. Run `tofu apply -var-file=environments/poc.tfvars`
            3. Update `.env` with Azure endpoints (see `.env.example` comments)
            4. Uncomment the CD workflow in `.github/workflows/ci.yml`
            5. Push to `main` branch to trigger deployment

            **No application code changes required** — only `.env` configuration changes.
