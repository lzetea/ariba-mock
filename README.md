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

# Get high-risk suppliers only
Invoke-RestMethod http://localhost:8081/api/risk/high-risk
```

### Test the MCP Server REST API

```powershell
# Service discovery
Invoke-RestMethod http://localhost:8082/

# List available tools
Invoke-RestMethod http://localhost:8082/api/v1/tools

# Dashboard via REST
Invoke-RestMethod http://localhost:8082/api/v1/dashboard

# Suppliers via REST
Invoke-RestMethod http://localhost:8082/api/v1/suppliers

# OpenAPI spec
Invoke-RestMethod http://localhost:8082/api/v1/openapi.json
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

The MCP server exposes two interfaces:
1. **MCP (SSE)** — for Foundry agents and MCP-compatible clients
2. **REST API** — for Copilot Studio and standard HTTP clients

#### MCP Endpoints (Foundry)

| Endpoint | Description |
|----------|-------------|
| `GET /` | Service discovery (lists all available endpoint paths) |
| `GET /health` | Health check |
| `GET /sse` | SSE connection endpoint |
| `POST /messages` | Message handling endpoint |

**For Microsoft Foundry agents**, configure the MCP client with:
- **SSE URL**: `https://ariba-mcp.<env>.azurecontainerapps.io/sse`

```powershell
# Test MCP server health
Invoke-RestMethod https://ariba-mcp.<env>.azurecontainerapps.io/health
```

#### REST API for Copilot Studio

The MCP server also exposes a full REST API under `/api/v1/` for integration with **Copilot Studio** and other HTTP-based consumers. These endpoints mirror the MCP tools but are accessible via standard HTTP GET requests.

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/tools` | List all available tools (for discovery) |
| `GET /api/v1/openapi.json` | OpenAPI 3.0 specification (auto-generated) |
| `GET /api/v1/dashboard` | Dashboard summary |
| `GET /api/v1/suppliers` | List suppliers (query: `status`, `category`) |
| `GET /api/v1/suppliers/{supplier_id}` | Get supplier by ID |
| `GET /api/v1/purchase-orders` | List POs (query: `status`, `supplier_id`) |
| `GET /api/v1/purchase-orders/{po_id}` | Get PO by ID |
| `GET /api/v1/requisitions` | List requisitions (query: `status`, `requester`) |
| `GET /api/v1/requisitions/{req_id}` | Get requisition by ID |
| `GET /api/v1/invoices` | List invoices (query: `status`, `po_number`) |
| `GET /api/v1/invoices/{invoice_id}` | Get invoice by ID |
| `GET /api/v1/contracts` | List contracts (query: `status`, `supplier_name`) |
| `GET /api/v1/contracts/{contract_id}` | Get contract by ID |
| `GET /api/v1/proposals` | List proposals (query: `rfp_id`, `supplier_id`, `status`) |
| `GET /api/v1/proposals/{proposal_id}` | Get proposal by ID |
| `GET /api/v1/rfps` | List RFPs (query: `status`) |
| `GET /api/v1/rfps/{rfp_id}` | Get RFP by ID |
| `GET /api/v1/risk/{supplier_id}` | Get risk score for a supplier |

**For Copilot Studio**, import the OpenAPI spec at:
- **OpenAPI URL**: `https://ariba-mcp.<env>.azurecontainerapps.io/api/v1/openapi.json`

```powershell
# Test REST API
Invoke-RestMethod https://ariba-mcp.<env>.azurecontainerapps.io/api/v1/dashboard

# Get OpenAPI spec
Invoke-RestMethod https://ariba-mcp.<env>.azurecontainerapps.io/api/v1/openapi.json
```

> **Note:** CORS is enabled on all REST endpoints (`*` origins) to support browser-based integrations.
