"""
SAP Ariba Mock Data Service
Provides mock Ariba data via HTTP API.
"""

import json
import random
import os
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

app = Flask(__name__)

# ============== Mock Data Store ==============

suppliers_db = {}
purchase_orders_db = {}
requisitions_db = {}
invoices_db = {}
contracts_db = {}
rfps_db = {}
proposals_db = {}


def generate_mock_data():
    """Generate initial mock data"""
    
    # Suppliers
    supplier_names = [
        ("Acme Corp", "Manufacturing", "USA"),
        ("Global Tech Solutions", "IT Services", "Germany"),
        ("Prime Materials Ltd", "Raw Materials", "UK"),
        ("FastShip Logistics", "Logistics", "Netherlands"),
        ("Quality Parts Inc", "Components", "Japan"),
    ]
    
    for i, (name, category, country) in enumerate(supplier_names):
        supplier_id = f"SUP-{1000 + i}"
        suppliers_db[supplier_id] = {
            "id": supplier_id,
            "name": name,
            "status": "Active" if random.random() > 0.2 else "Under Review",
            "category": category,
            "country": country,
            "risk_score": round(random.uniform(1, 5), 1),
            "created_date": (datetime.now() - timedelta(days=random.randint(30, 365))).isoformat()
        }
    
    # Purchase Orders
    po_statuses = ["Draft", "Pending Approval", "Approved", "Sent", "Acknowledged", "Received", "Closed"]
    for i in range(10):
        po_id = f"PO-{2024000 + i}"
        supplier = random.choice(list(suppliers_db.values()))
        purchase_orders_db[po_id] = {
            "id": po_id,
            "order_number": po_id,
            "supplier_id": supplier["id"],
            "supplier_name": supplier["name"],
            "status": random.choice(po_statuses),
            "total_amount": round(random.uniform(1000, 100000), 2),
            "currency": "USD",
            "created_date": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            "items": [
                {"description": f"Item {j+1}", "quantity": random.randint(1, 100), "unit_price": round(random.uniform(10, 500), 2)}
                for j in range(random.randint(1, 5))
            ]
        }
    
    # Requisitions
    req_statuses = ["Draft", "Submitted", "Pending Approval", "Approved", "Rejected", "Ordered"]
    requesters = ["John Smith", "Jane Doe", "Bob Wilson", "Alice Johnson", "Charlie Brown"]
    for i in range(8):
        req_id = f"REQ-{3024000 + i}"
        requisitions_db[req_id] = {
            "id": req_id,
            "requisition_number": req_id,
            "requester": random.choice(requesters),
            "status": random.choice(req_statuses),
            "total_amount": round(random.uniform(500, 50000), 2),
            "currency": "USD",
            "created_date": (datetime.now() - timedelta(days=random.randint(1, 60))).isoformat(),
            "approval_status": random.choice(["Pending", "Approved", "Rejected"])
        }
    
    # Invoices
    inv_statuses = ["Draft", "Submitted", "Under Review", "Approved", "Paid", "Rejected"]
    for i in range(12):
        inv_id = f"INV-{4024000 + i}"
        po = random.choice(list(purchase_orders_db.values()))
        invoices_db[inv_id] = {
            "id": inv_id,
            "invoice_number": inv_id,
            "po_number": po["order_number"],
            "supplier_name": po["supplier_name"],
            "amount": round(po["total_amount"] * random.uniform(0.3, 1.0), 2),
            "currency": "USD",
            "status": random.choice(inv_statuses),
            "due_date": (datetime.now() + timedelta(days=random.randint(15, 60))).isoformat(),
            "created_date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        }
    
    # Contracts
    contract_statuses = ["Draft", "In Negotiation", "Pending Approval", "Active", "Expired", "Terminated"]
    for i in range(6):
        contract_id = f"CON-{5024000 + i}"
        supplier = random.choice(list(suppliers_db.values()))
        start = datetime.now() - timedelta(days=random.randint(0, 365))
        contracts_db[contract_id] = {
            "id": contract_id,
            "contract_number": contract_id,
            "title": f"Service Agreement - {supplier['name']}",
            "supplier_name": supplier["name"],
            "start_date": start.isoformat(),
            "end_date": (start + timedelta(days=random.randint(365, 1095))).isoformat(),
            "value": round(random.uniform(50000, 1000000), 2),
            "currency": "USD",
            "status": random.choice(contract_statuses)
        }
    
    # RFPs (Request for Proposals) with requirements
    rfp_requirements = {
        "RFP-2026-001": {
            "id": "RFP-2026-001",
            "title": "Enterprise ERP System Implementation",
            "status": "Open",
            "deadline": (datetime.now() + timedelta(days=30)).isoformat(),
            "budget_max": 500000,
            "currency": "USD",
            "requirements": [
                {"id": "REQ-001", "category": "Functional", "description": "Multi-currency support", "priority": "Must-have", "weight": 10},
                {"id": "REQ-002", "category": "Functional", "description": "Real-time inventory tracking", "priority": "Must-have", "weight": 10},
                {"id": "REQ-003", "category": "Functional", "description": "Automated purchase order generation", "priority": "Must-have", "weight": 10},
                {"id": "REQ-004", "category": "Functional", "description": "Supplier portal integration", "priority": "Should-have", "weight": 8},
                {"id": "REQ-005", "category": "Functional", "description": "Advanced analytics dashboard", "priority": "Should-have", "weight": 7},
                {"id": "REQ-006", "category": "Technical", "description": "REST API availability", "priority": "Must-have", "weight": 10},
                {"id": "REQ-007", "category": "Technical", "description": "Cloud-native architecture", "priority": "Should-have", "weight": 8},
                {"id": "REQ-008", "category": "Technical", "description": "Mobile application support", "priority": "Nice-to-have", "weight": 5},
                {"id": "REQ-009", "category": "Integration", "description": "SAP S/4HANA integration", "priority": "Must-have", "weight": 10},
                {"id": "REQ-010", "category": "Integration", "description": "Salesforce CRM connector", "priority": "Nice-to-have", "weight": 5}
            ]
        },
        "RFP-2026-002": {
            "id": "RFP-2026-002",
            "title": "Logistics Management Platform",
            "status": "Open",
            "deadline": (datetime.now() + timedelta(days=45)).isoformat(),
            "budget_max": 300000,
            "currency": "USD",
            "requirements": [
                {"id": "REQ-001", "category": "Functional", "description": "Route optimization", "priority": "Must-have", "weight": 10},
                {"id": "REQ-002", "category": "Functional", "description": "Real-time shipment tracking", "priority": "Must-have", "weight": 10},
                {"id": "REQ-003", "category": "Functional", "description": "Carrier rate comparison", "priority": "Must-have", "weight": 10},
                {"id": "REQ-004", "category": "Functional", "description": "Automated customs documentation", "priority": "Should-have", "weight": 8},
                {"id": "REQ-005", "category": "Functional", "description": "Warehouse management", "priority": "Should-have", "weight": 7},
                {"id": "REQ-006", "category": "Technical", "description": "EDI support", "priority": "Must-have", "weight": 10},
                {"id": "REQ-007", "category": "Technical", "description": "Multi-tenant SaaS", "priority": "Should-have", "weight": 8},
                {"id": "REQ-008", "category": "Integration", "description": "ERP integration", "priority": "Must-have", "weight": 10}
            ]
        }
    }
    rfps_db.update(rfp_requirements)
    
    # Proposals (for RFP responses) with functional coverage
    proposal_statuses = ["Submitted", "Under Review", "Shortlisted", "Rejected", "Awarded"]
    
    for i, supplier in enumerate(suppliers_db.values()):
        for rfp_id in random.sample(list(rfps_db.keys()), random.randint(1, 2)):
            proposal_id = f"PROP-{6024000 + i * 10 + list(rfps_db.keys()).index(rfp_id)}"
            base_price = round(random.uniform(50000, 500000), 2)
            
            # Generate functional coverage for each RFP requirement
            rfp_reqs = rfps_db[rfp_id]["requirements"]
            functional_coverage = []
            for req in rfp_reqs:
                coverage_status = random.choice(["Full", "Full", "Partial", "Partial", "None", "Roadmap"])
                functional_coverage.append({
                    "requirement_id": req["id"],
                    "status": coverage_status,
                    "notes": None if coverage_status == "Full" else random.choice([
                        "Available in next release",
                        "Requires customization",
                        "Partner solution available",
                        "Not currently supported"
                    ]) if coverage_status != "Full" else None
                })
            
            proposals_db[proposal_id] = {
                "id": proposal_id,
                "rfp_id": rfp_id,
                "supplier_id": supplier["id"],
                "supplier_name": supplier["name"],
                "status": random.choice(proposal_statuses),
                "submitted_date": (datetime.now() - timedelta(days=random.randint(5, 30))).isoformat(),
                "pricing": {
                    "total": base_price,
                    "currency": random.choice(["USD", "EUR", "GBP"]),
                    "breakdown": [
                        {"item": "Implementation", "amount": round(base_price * 0.4, 2)},
                        {"item": "Licensing", "amount": round(base_price * 0.35, 2)},
                        {"item": "Support (yearly)", "amount": round(base_price * 0.25, 2)}
                    ]
                },
                "sla": {
                    "uptime": round(random.uniform(99.0, 99.99), 2),
                    "response_time_hours": random.choice([1, 2, 4, 8, 24]),
                    "resolution_time_hours": random.choice([4, 8, 24, 48, 72]),
                    "penalties": random.choice([True, False])
                },
                "compliance": {
                    "gdpr": random.choice([True, False]),
                    "iso27001": random.choice([True, False]),
                    "soc2": random.choice([True, False]),
                    "notes": random.choice([None, "Certification pending", "Annual audit completed"])
                },
                "functional_coverage": functional_coverage,
                "delivery_weeks": random.randint(4, 24),
                "validity_days": random.choice([30, 60, 90])
            }


# Initialize mock data
generate_mock_data()


# ============== API Endpoints ==============

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})


@app.route("/api/dashboard/summary")
def dashboard_summary():
    return jsonify({
        "suppliers": {
            "total": len(suppliers_db),
            "active": len([s for s in suppliers_db.values() if s["status"] == "Active"])
        },
        "purchase_orders": {
            "total": len(purchase_orders_db),
            "pending": len([p for p in purchase_orders_db.values() if p["status"] in ["Draft", "Pending Approval"]]),
            "total_value": sum(p["total_amount"] for p in purchase_orders_db.values())
        },
        "requisitions": {
            "total": len(requisitions_db),
            "pending_approval": len([r for r in requisitions_db.values() if r["approval_status"] == "Pending"])
        },
        "invoices": {
            "total": len(invoices_db),
            "pending_payment": len([i for i in invoices_db.values() if i["status"] in ["Approved", "Under Review"]]),
            "total_value": sum(i["amount"] for i in invoices_db.values())
        },
        "contracts": {
            "total": len(contracts_db),
            "active": len([c for c in contracts_db.values() if c["status"] == "Active"]),
            "total_value": sum(c["value"] for c in contracts_db.values())
        }
    })


# Suppliers
@app.route("/api/suppliers")
def list_suppliers():
    suppliers = list(suppliers_db.values())
    status = request.args.get("status")
    category = request.args.get("category")
    if status:
        suppliers = [s for s in suppliers if s["status"].lower() == status.lower()]
    if category:
        suppliers = [s for s in suppliers if s["category"].lower() == category.lower()]
    return jsonify(suppliers)


@app.route("/api/suppliers/<supplier_id>")
def get_supplier(supplier_id):
    if supplier_id not in suppliers_db:
        return jsonify({"error": f"Supplier '{supplier_id}' not found"}), 404
    return jsonify(suppliers_db[supplier_id])


# Purchase Orders
@app.route("/api/purchase-orders")
def list_purchase_orders():
    orders = list(purchase_orders_db.values())
    status = request.args.get("status")
    supplier_id = request.args.get("supplier_id")
    if status:
        orders = [o for o in orders if o["status"].lower() == status.lower()]
    if supplier_id:
        orders = [o for o in orders if o["supplier_id"] == supplier_id]
    return jsonify(orders)


@app.route("/api/purchase-orders/<po_id>")
def get_purchase_order(po_id):
    if po_id not in purchase_orders_db:
        return jsonify({"error": f"Purchase order '{po_id}' not found"}), 404
    return jsonify(purchase_orders_db[po_id])


# Requisitions
@app.route("/api/requisitions")
def list_requisitions():
    reqs = list(requisitions_db.values())
    status = request.args.get("status")
    requester = request.args.get("requester")
    if status:
        reqs = [r for r in reqs if r["status"].lower() == status.lower()]
    if requester:
        reqs = [r for r in reqs if requester.lower() in r["requester"].lower()]
    return jsonify(reqs)


@app.route("/api/requisitions/<req_id>")
def get_requisition(req_id):
    if req_id not in requisitions_db:
        return jsonify({"error": f"Requisition '{req_id}' not found"}), 404
    return jsonify(requisitions_db[req_id])


# Invoices
@app.route("/api/invoices")
def list_invoices():
    invs = list(invoices_db.values())
    status = request.args.get("status")
    po_number = request.args.get("po_number")
    if status:
        invs = [i for i in invs if i["status"].lower() == status.lower()]
    if po_number:
        invs = [i for i in invs if i["po_number"] == po_number]
    return jsonify(invs)


@app.route("/api/invoices/<invoice_id>")
def get_invoice(invoice_id):
    if invoice_id not in invoices_db:
        return jsonify({"error": f"Invoice '{invoice_id}' not found"}), 404
    return jsonify(invoices_db[invoice_id])


# Contracts
@app.route("/api/contracts")
def list_contracts():
    cons = list(contracts_db.values())
    status = request.args.get("status")
    supplier_name = request.args.get("supplier_name")
    if status:
        cons = [c for c in cons if c["status"].lower() == status.lower()]
    if supplier_name:
        cons = [c for c in cons if supplier_name.lower() in c["supplier_name"].lower()]
    return jsonify(cons)


@app.route("/api/contracts/<contract_id>")
def get_contract(contract_id):
    if contract_id not in contracts_db:
        return jsonify({"error": f"Contract '{contract_id}' not found"}), 404
    return jsonify(contracts_db[contract_id])


# Proposals
@app.route("/api/proposals")
def list_proposals():
    props = list(proposals_db.values())
    rfp_id = request.args.get("rfp_id")
    supplier_id = request.args.get("supplier_id")
    status = request.args.get("status")
    if rfp_id:
        props = [p for p in props if p["rfp_id"] == rfp_id]
    if supplier_id:
        props = [p for p in props if p["supplier_id"] == supplier_id]
    if status:
        props = [p for p in props if p["status"].lower() == status.lower()]
    return jsonify(props)


@app.route("/api/proposals/<proposal_id>")
def get_proposal(proposal_id):
    if proposal_id not in proposals_db:
        return jsonify({"error": f"Proposal '{proposal_id}' not found"}), 404
    return jsonify(proposals_db[proposal_id])


# RFPs
@app.route("/api/rfps")
def list_rfps():
    rfps = list(rfps_db.values())
    status = request.args.get("status")
    if status:
        rfps = [r for r in rfps if r["status"].lower() == status.lower()]
    return jsonify(rfps)


@app.route("/api/rfps/<rfp_id>")
def get_rfp(rfp_id):
    if rfp_id not in rfps_db:
        return jsonify({"error": f"RFP '{rfp_id}' not found"}), 404
    return jsonify(rfps_db[rfp_id])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
