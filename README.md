# SAP Ariba Mockup

Mock SAP Ariba + Risk Assessment services with an MCP server for AI agents.

## Architecture

```
ariba-mockup/
 mock/           # Ariba API (port 8080)
 risk/           # Risk Assessment API (port 8081)
 mcp-server/     # MCP Server
 docker-compose.yml
```

All three services run on Azure Container Apps:

| Service | Description | Port |
|---------|-------------|------|
| `ariba-mock` | Mock Ariba data (suppliers, POs, invoices, contracts) | 8080 |
| `risk-service` | Supplier risk scoring | 8081 |
| `ariba-mcp` | MCP server for AI agents (HTTP/SSE) | 8082 |

## Quick Start (Local)

### 1. Start the backend services

```bash
docker-compose up --build
```

### 2. Run the MCP server locally

```powershell
cd mcp-server
pip install -r requirements.txt
$env:MOCK_API_URL="http://localhost:8080"; $env:RISK_API_URL="http://localhost:8081"; python server.py
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `get_dashboard_summary` | Overview of all Ariba data |
| `list_suppliers` | List suppliers (filter by status/category) |
| `get_supplier` | Get supplier by ID |
| `list_purchase_orders` | List POs (filter by status/supplier) |
| `get_purchase_order` | Get PO by ID |
| `list_requisitions` | List requisitions |
| `get_requisition` | Get requisition by ID |
| `list_invoices` | List invoices |
| `get_invoice` | Get invoice by ID |
| `list_contracts` | List contracts |
| `get_contract` | Get contract by ID |
| `list_rfps` | List RFPs with requirements and weights |
| `get_rfp` | Get RFP details (requirements, priorities, weights) |
| `list_proposals` | List vendor proposals (filter by rfp_id/supplier_id/status) |
| `get_proposal` | Get proposal details (pricing, SLA, compliance, functional_coverage) |
| `risk_get_score` | Get risk score for a supplier (from Risk service) |

## MCP Server Configuration

The MCP server connects to the backend services via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MOCK_API_URL` | URL of the Ariba mock service | `http://localhost:8080` |
| `RISK_API_URL` | URL of the Risk service | `http://localhost:8081` |

## Testing

### Test the Mock API

```powershell
# Health check
Invoke-RestMethod http://localhost:8080/health

# Dashboard summary
Invoke-RestMethod http://localhost:8080/api/dashboard/summary

# List suppliers
Invoke-RestMethod http://localhost:8080/api/suppliers

# Get a specific supplier
Invoke-RestMethod http://localhost:8080/api/suppliers/SUP-1000
```

### Test the Risk API

```powershell
# Health check
Invoke-RestMethod http://localhost:8081/health

# Get risk score for a supplier
Invoke-RestMethod http://localhost:8081/api/risk/score/SUP-1000

# List all risk scores
Invoke-RestMethod http://localhost:8081/api/risk/scores
```

## Deploy to Azure Container Apps

```bash
# Build and push all images
az acr build --registry <acr> --image ariba-mock:v1 ./mock
az acr build --registry <acr> --image risk-service:v1 ./risk
az acr build --registry <acr> --image ariba-mcp:v1 ./mcp-server

# Deploy backend services
az containerapp create --name ariba-mock --resource-group <rg> --environment <env> \
  --image <acr>.azurecr.io/ariba-mock:v1 --target-port 8080 --ingress external

az containerapp create --name risk-service --resource-group <rg> --environment <env> \
  --image <acr>.azurecr.io/risk-service:v1 --target-port 8081 --ingress external

# Deploy MCP server (configure env vars to point to backend services)
az containerapp create --name ariba-mcp --resource-group <rg> --environment <env> \
  --image <acr>.azurecr.io/ariba-mcp:v1 --target-port 8082 --ingress external \
  --env-vars MOCK_API_URL=https://ariba-mock.<env>.azurecontainerapps.io \
             RISK_API_URL=https://risk-service.<env>.azurecontainerapps.io
```

### Connect AI agent to MCP server on ACA

The MCP server exposes HTTP/SSE endpoints for remote connections:

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Health check |
| `GET /sse` | SSE connection endpoint |
| `POST /messages` | Message handling endpoint |

**For Microsoft Foundry agents**, configure the MCP client with:
- **SSE URL**: `https://ariba-mcp.<env>.azurecontainerapps.io/sse`

```powershell
# Test MCP server health
Invoke-RestMethod https://ariba-mcp.<env>.azurecontainerapps.io/health
```
