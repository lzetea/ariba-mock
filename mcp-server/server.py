"""
MCP Server
Exposes Ariba Mock API & Risk Service as MCP tools for AI agents.
Supports both stdio (local) and HTTP/SSE (remote) transport.
"""

import json
import os
import httpx
import asyncio
from contextlib import asynccontextmanager
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse
import uvicorn

# Service URLs (configurable via environment variables)
MOCK_API_URL = os.environ.get("MOCK_API_URL", "http://localhost:8080")
RISK_API_URL = os.environ.get("RISK_API_URL", "http://localhost:8081")

server = Server("ariba-mcp")

# Persistent HTTP client (initialized on startup)
http_client: httpx.AsyncClient = None


async def call_mock_api(endpoint: str, params: dict = None) -> dict:
    """Call the mock API service"""
    global http_client
    try:
        response = await http_client.get(f"{MOCK_API_URL}{endpoint}", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        return {"error": str(e)}


async def call_risk_api(endpoint: str, params: dict = None) -> dict:
    """Call the Risk Assessment API service"""
    global http_client
    try:
        response = await http_client.get(f"{RISK_API_URL}{endpoint}", params=params, timeout=30.0)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        return {"error": str(e)}


async def warmup_connections():
    """Pre-warm connections to backend services on startup"""
    global http_client
    print("Warming up connections to backend services...")
    try:
        await http_client.get(f"{MOCK_API_URL}/health", timeout=10.0)
        print(f"✓ Mock API ({MOCK_API_URL}) is reachable")
    except Exception as e:
        print(f"⚠ Mock API warmup failed: {e}")
    
    try:
        await http_client.get(f"{RISK_API_URL}/health", timeout=10.0)
        print(f"✓ Risk API ({RISK_API_URL}) is reachable")
    except Exception as e:
        print(f"⚠ Risk API warmup failed: {e}")
    
    print("Warmup complete!")


@asynccontextmanager
async def lifespan(app):
    """Startup and shutdown lifecycle"""
    global http_client
    # Startup: create persistent client and warm up connections
    http_client = httpx.AsyncClient(
        timeout=30.0,
        limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
    )
    await warmup_connections()
    yield
    # Shutdown: close client
    await http_client.aclose()


@server.list_tools()
async def list_tools():
    """List available Ariba tools"""
    return [
        Tool(
            name="get_dashboard_summary",
            description="Get a summary of all Ariba data including supplier counts, PO totals, invoice status, and contract values",
            inputSchema={"type": "object", "properties": {}, "required": []}
        ),
        Tool(
            name="list_suppliers",
            description="List all suppliers in SAP Ariba. Optionally filter by status or category.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status (e.g., 'Active', 'Under Review')"},
                    "category": {"type": "string", "description": "Filter by category (e.g., 'IT Services', 'Manufacturing')"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_supplier",
            description="Get details for a specific supplier by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "supplier_id": {"type": "string", "description": "The supplier ID (e.g., 'SUP-1000')"}
                },
                "required": ["supplier_id"]
            }
        ),
        Tool(
            name="list_purchase_orders",
            description="List all purchase orders. Optionally filter by status or supplier.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status (e.g., 'Approved', 'Pending Approval')"},
                    "supplier_id": {"type": "string", "description": "Filter by supplier ID"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_purchase_order",
            description="Get details for a specific purchase order by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "po_id": {"type": "string", "description": "The purchase order ID (e.g., 'PO-2024000')"}
                },
                "required": ["po_id"]
            }
        ),
        Tool(
            name="list_requisitions",
            description="List all requisitions. Optionally filter by status or requester.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status"},
                    "requester": {"type": "string", "description": "Filter by requester name"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_requisition",
            description="Get details for a specific requisition by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "req_id": {"type": "string", "description": "The requisition ID (e.g., 'REQ-3024000')"}
                },
                "required": ["req_id"]
            }
        ),
        Tool(
            name="list_invoices",
            description="List all invoices. Optionally filter by status or PO number.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status (e.g., 'Paid', 'Approved')"},
                    "po_number": {"type": "string", "description": "Filter by purchase order number"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_invoice",
            description="Get details for a specific invoice by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string", "description": "The invoice ID (e.g., 'INV-4024000')"}
                },
                "required": ["invoice_id"]
            }
        ),
        Tool(
            name="list_contracts",
            description="List all contracts. Optionally filter by status or supplier name.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status (e.g., 'Active', 'Expired')"},
                    "supplier_name": {"type": "string", "description": "Filter by supplier name"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_contract",
            description="Get details for a specific contract by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "contract_id": {"type": "string", "description": "The contract ID (e.g., 'CON-5024000')"}
                },
                "required": ["contract_id"]
            }
        ),
        Tool(
            name="list_proposals",
            description="List vendor proposals/offers. Filter by RFP ID, supplier ID, or status. Returns pricing, SLA, and compliance details.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rfp_id": {"type": "string", "description": "Filter by RFP ID (e.g., 'RFP-2026-001')"},
                    "supplier_id": {"type": "string", "description": "Filter by supplier ID"},
                    "status": {"type": "string", "description": "Filter by status (Submitted, Under Review, Shortlisted, Rejected, Awarded)"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_proposal",
            description="Get details for a specific vendor proposal by ID. Includes pricing breakdown, SLA terms, compliance certifications, and functional coverage for each RFP requirement.",
            inputSchema={
                "type": "object",
                "properties": {
                    "proposal_id": {"type": "string", "description": "The proposal ID (e.g., 'PROP-6024000')"}
                },
                "required": ["proposal_id"]
            }
        ),
        Tool(
            name="list_rfps",
            description="List all RFPs (Request for Proposals). Each RFP contains requirements with priorities and weights for scoring.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status (e.g., 'Open', 'Closed')"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_rfp",
            description="Get RFP details including all requirements with their priorities (Must-have, Should-have, Nice-to-have) and weights for functional scoring.",
            inputSchema={
                "type": "object",
                "properties": {
                    "rfp_id": {"type": "string", "description": "The RFP ID (e.g., 'RFP-2026-001')"}
                },
                "required": ["rfp_id"]
            }
        ),
        Tool(
            name="risk_get_score",
            description="Get risk assessment score for a specific supplier. Returns overall risk score, risk level, risk factors, and alerts from the Risk Assessment service (separate from Ariba).",
            inputSchema={
                "type": "object",
                "properties": {
                    "supplier_id": {"type": "string", "description": "The supplier ID (e.g., 'SUP-1000')"}
                },
                "required": ["supplier_id"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls by forwarding to mock API"""
    
    if name == "get_dashboard_summary":
        result = await call_mock_api("/api/dashboard/summary")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "list_suppliers":
        params = {}
        if arguments.get("status"):
            params["status"] = arguments["status"]
        if arguments.get("category"):
            params["category"] = arguments["category"]
        result = await call_mock_api("/api/suppliers", params)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_supplier":
        supplier_id = arguments.get("supplier_id")
        result = await call_mock_api(f"/api/suppliers/{supplier_id}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "list_purchase_orders":
        params = {}
        if arguments.get("status"):
            params["status"] = arguments["status"]
        if arguments.get("supplier_id"):
            params["supplier_id"] = arguments["supplier_id"]
        result = await call_mock_api("/api/purchase-orders", params)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_purchase_order":
        po_id = arguments.get("po_id")
        result = await call_mock_api(f"/api/purchase-orders/{po_id}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "list_requisitions":
        params = {}
        if arguments.get("status"):
            params["status"] = arguments["status"]
        if arguments.get("requester"):
            params["requester"] = arguments["requester"]
        result = await call_mock_api("/api/requisitions", params)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_requisition":
        req_id = arguments.get("req_id")
        result = await call_mock_api(f"/api/requisitions/{req_id}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "list_invoices":
        params = {}
        if arguments.get("status"):
            params["status"] = arguments["status"]
        if arguments.get("po_number"):
            params["po_number"] = arguments["po_number"]
        result = await call_mock_api("/api/invoices", params)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_invoice":
        invoice_id = arguments.get("invoice_id")
        result = await call_mock_api(f"/api/invoices/{invoice_id}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "list_contracts":
        params = {}
        if arguments.get("status"):
            params["status"] = arguments["status"]
        if arguments.get("supplier_name"):
            params["supplier_name"] = arguments["supplier_name"]
        result = await call_mock_api("/api/contracts", params)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_contract":
        contract_id = arguments.get("contract_id")
        result = await call_mock_api(f"/api/contracts/{contract_id}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "list_proposals":
        params = {}
        if arguments.get("rfp_id"):
            params["rfp_id"] = arguments["rfp_id"]
        if arguments.get("supplier_id"):
            params["supplier_id"] = arguments["supplier_id"]
        if arguments.get("status"):
            params["status"] = arguments["status"]
        result = await call_mock_api("/api/proposals", params)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_proposal":
        proposal_id = arguments.get("proposal_id")
        result = await call_mock_api(f"/api/proposals/{proposal_id}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "list_rfps":
        params = {}
        if arguments.get("status"):
            params["status"] = arguments["status"]
        result = await call_mock_api("/api/rfps", params)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "get_rfp":
        rfp_id = arguments.get("rfp_id")
        result = await call_mock_api(f"/api/rfps/{rfp_id}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    elif name == "risk_get_score":
        supplier_id = arguments.get("supplier_id")
        result = await call_risk_api(f"/api/risk/score/{supplier_id}")
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    else:
        return [TextContent(type="text", text=f"Error: Unknown tool '{name}'")]


# SSE transport for remote connections (Foundry agents)
sse = SseServerTransport("/messages")

async def handle_sse(request):
    """Handle SSE connections from remote MCP clients"""
    async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
        await server.run(streams[0], streams[1], server.create_initialization_options())

async def handle_messages(request):
    """Handle POST messages from MCP clients"""
    await sse.handle_post_message(request.scope, request.receive, request._send)

async def health(request):
    """Health check endpoint"""
    return JSONResponse({"status": "healthy", "service": "ariba-mcp"})

async def root(request):
    """Root endpoint - for MCP discovery"""
    return JSONResponse({
        "name": "ariba-mcp",
        "version": "1.0.0",
        "status": "healthy",
        "endpoints": {
            "sse": "/sse",
            "messages": "/messages",
            "health": "/health"
        }
    })

# Starlette app with SSE routes and lifespan for connection warmup
app = Starlette(
    debug=False,
    lifespan=lifespan,
    routes=[
        Route("/", root),
        Route("/health", health),
        Route("/sse", handle_sse),
        Route("/messages", handle_messages, methods=["POST"]),
    ]
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8082))
    uvicorn.run(app, host="0.0.0.0", port=port)
