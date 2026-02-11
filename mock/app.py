"""
SAP Ariba Mock Data Service
Provides mock Ariba data via HTTP API.
"""

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
    """Generate initial mock data - hardcoded to match Excel vendor files"""
    
    # Suppliers - matching the 3 Excel vendor files
    suppliers_db["SUP-1000"] = {
        "id": "SUP-1000",
        "name": "ERPMax Solutions",
        "status": "Active",
        "category": "ERP Software",
        "country": "USA",
        "contact_name": "Sarah Mitchell",
        "contact_email": "sarah.mitchell@erpmax.com",
        "contact_phone": "+1-555-0142",
        "risk_score": 2.1,
        "created_date": "2024-03-15T00:00:00"
    }
    
    suppliers_db["SUP-1001"] = {
        "id": "SUP-1001",
        "name": "IntegraPro Systems",
        "status": "Active",
        "category": "ERP Software",
        "country": "USA",
        "contact_name": "Michael Chen",
        "contact_email": "m.chen@integrapro.com",
        "contact_phone": "+1-555-0287",
        "risk_score": 1.8,
        "created_date": "2023-11-20T00:00:00"
    }
    
    suppliers_db["SUP-1002"] = {
        "id": "SUP-1002",
        "name": "CloudFirst ERP",
        "status": "Active",
        "category": "ERP Software",
        "country": "USA",
        "contact_name": "Jennifer Walsh",
        "contact_email": "j.walsh@cloudfirsterp.com",
        "contact_phone": "+1-555-0393",
        "risk_score": 3.5,
        "created_date": "2025-01-10T00:00:00"
    }
    
    # ANOMALY: Duplicate supplier - same company registered twice with slight name variation
    suppliers_db["SUP-1003"] = {
        "id": "SUP-1003",
        "name": "ERP Max Solutions Inc",  # Same as SUP-1000 but with slight name variation
        "status": "Active",
        "category": "ERP Software",
        "country": "USA",
        "contact_name": "Sarah Mitchell",  # Same contact
        "contact_email": "s.mitchell@erpmax.com",  # Slightly different email
        "contact_phone": "+1-555-0142",  # Same phone
        "risk_score": 2.3,
        "created_date": "2025-06-01T00:00:00"  # Created later - possible duplicate entry
    }
    
    # ANOMALY: Supplier with outdated/stale data
    suppliers_db["SUP-1004"] = {
        "id": "SUP-1004",
        "name": "Legacy Systems Corp",
        "status": "Active",  # Still marked active but contract expired 2 years ago
        "category": "Legacy Software",
        "country": "USA",
        "contact_name": "Robert Johnson",
        "contact_email": "r.johnson@legacysystems.com",
        "contact_phone": "+1-555-0199",
        "risk_score": 7.5,  # High risk score
        "created_date": "2019-03-01T00:00:00",
        "last_activity_date": "2023-12-15T00:00:00"  # No activity for over 2 years
    }
    
    # Purchase Orders - Hardcoded historical data for SUP-1000 and SUP-1002
    
    # ERPMax Solutions (SUP-1000) - Long history, reliable
    purchase_orders_db["PO-2024001"] = {
        "id": "PO-2024001",
        "order_number": "PO-2024001",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "status": "Closed",
        "total_amount": 125000.00,
        "currency": "USD",
        "created_date": "2024-06-15T00:00:00",
        "items": [
            {"description": "ERP License - 50 users", "quantity": 50, "unit_price": 2000.00},
            {"description": "Implementation Services", "quantity": 1, "unit_price": 25000.00}
        ]
    }
    purchase_orders_db["PO-2024002"] = {
        "id": "PO-2024002",
        "order_number": "PO-2024002",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "status": "Closed",
        "total_amount": 45000.00,
        "currency": "USD",
        "created_date": "2024-09-20T00:00:00",
        "items": [
            {"description": "Additional User Licenses", "quantity": 20, "unit_price": 1500.00},
            {"description": "Training Services", "quantity": 3, "unit_price": 5000.00}
        ]
    }
    purchase_orders_db["PO-2025001"] = {
        "id": "PO-2025001",
        "order_number": "PO-2025001",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "status": "Closed",
        "total_amount": 97500.00,
        "currency": "USD",
        "created_date": "2025-01-10T00:00:00",
        "items": [
            {"description": "Annual Support Renewal", "quantity": 1, "unit_price": 97500.00}
        ]
    }
    purchase_orders_db["PO-2025002"] = {
        "id": "PO-2025002",
        "order_number": "PO-2025002",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "status": "Received",
        "total_amount": 35000.00,
        "currency": "USD",
        "created_date": "2025-08-05T00:00:00",
        "items": [
            {"description": "Analytics Module Add-on", "quantity": 1, "unit_price": 25000.00},
            {"description": "Configuration Services", "quantity": 2, "unit_price": 5000.00}
        ]
    }
    
    # CloudFirst ERP (SUP-1002) - New vendor, limited history
    purchase_orders_db["PO-2025003"] = {
        "id": "PO-2025003",
        "order_number": "PO-2025003",
        "supplier_id": "SUP-1002",
        "supplier_name": "CloudFirst ERP",
        "status": "Closed",
        "total_amount": 15000.00,
        "currency": "USD",
        "created_date": "2025-03-15T00:00:00",
        "items": [
            {"description": "Pilot License - 10 users", "quantity": 10, "unit_price": 1000.00},
            {"description": "Setup Services", "quantity": 1, "unit_price": 5000.00}
        ]
    }
    purchase_orders_db["PO-2025004"] = {
        "id": "PO-2025004",
        "order_number": "PO-2025004",
        "supplier_id": "SUP-1002",
        "supplier_name": "CloudFirst ERP",
        "status": "Acknowledged",
        "total_amount": 8500.00,
        "currency": "USD",
        "created_date": "2025-11-20T00:00:00",
        "items": [
            {"description": "Extended Pilot - Additional Users", "quantity": 5, "unit_price": 1000.00},
            {"description": "Integration Consulting", "quantity": 1, "unit_price": 3500.00}
        ]
    }
    
    # IntegraPro Systems (SUP-1001) - Some history
    purchase_orders_db["PO-2024003"] = {
        "id": "PO-2024003",
        "order_number": "PO-2024003",
        "supplier_id": "SUP-1001",
        "supplier_name": "IntegraPro Systems",
        "status": "Closed",
        "total_amount": 75000.00,
        "currency": "USD",
        "created_date": "2024-04-10T00:00:00",
        "items": [
            {"description": "Integration Platform License", "quantity": 1, "unit_price": 50000.00},
            {"description": "API Gateway Setup", "quantity": 1, "unit_price": 25000.00}
        ]
    }
    
    # ANOMALY: PO using duplicate supplier (same as SUP-1000 but different ID)
    purchase_orders_db["PO-2025005"] = {
        "id": "PO-2025005",
        "order_number": "PO-2025005",
        "supplier_id": "SUP-1003",  # Duplicate of ERPMax
        "supplier_name": "ERP Max Solutions Inc",
        "status": "Approved",
        "total_amount": 85000.00,
        "currency": "USD",
        "created_date": "2025-07-15T00:00:00",
        "items": [
            {"description": "ERP Module Extension", "quantity": 1, "unit_price": 60000.00},
            {"description": "Configuration Services", "quantity": 1, "unit_price": 25000.00}
        ],
        "notes": "Duplicate supplier entry - should be consolidated with SUP-1000"
    }
    
    # ANOMALY: PO amount exceeds contract value - Price mismatch
    purchase_orders_db["PO-2025006"] = {
        "id": "PO-2025006",
        "order_number": "PO-2025006",
        "supplier_id": "SUP-1002",
        "supplier_name": "CloudFirst ERP",
        "status": "Pending Approval",
        "total_amount": 75000.00,  # Exceeds pilot contract value of $25,000
        "currency": "USD",
        "created_date": "2025-12-01T00:00:00",
        "contract_reference": "CON-5025001",  # Pilot contract with $25K limit
        "items": [
            {"description": "Production License Upgrade", "quantity": 25, "unit_price": 2000.00},
            {"description": "Data Migration", "quantity": 1, "unit_price": 25000.00}
        ],
        "anomaly_flag": "PO amount ($75,000) exceeds contract value ($25,000)"
    }
    
    # ANOMALY: PO referencing expired contract
    purchase_orders_db["PO-2025007"] = {
        "id": "PO-2025007",
        "order_number": "PO-2025007",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "status": "Draft",
        "total_amount": 50000.00,
        "currency": "USD",
        "created_date": "2025-10-01T00:00:00",
        "contract_reference": "CON-5023001",  # Expired contract!
        "items": [
            {"description": "Legacy System Support Extension", "quantity": 1, "unit_price": 50000.00}
        ],
        "anomaly_flag": "References expired contract CON-5023001 (ended 2024-05-31)"
    }
    
    # ANOMALY: PO with obsolete/stale supplier
    purchase_orders_db["PO-2023001"] = {
        "id": "PO-2023001",
        "order_number": "PO-2023001",
        "supplier_id": "SUP-1004",  # Legacy Systems Corp - no activity in 2 years
        "supplier_name": "Legacy Systems Corp",
        "status": "Closed",
        "total_amount": 120000.00,
        "currency": "USD",
        "created_date": "2023-06-15T00:00:00",
        "items": [
            {"description": "Legacy Maintenance Contract", "quantity": 1, "unit_price": 120000.00}
        ]
    }
    
    # Requisitions - Keep some random but add specific ones
    requisitions_db["REQ-3024001"] = {
        "id": "REQ-3024001",
        "requisition_number": "REQ-3024001",
        "requester": "John Smith",
        "status": "Approved",
        "total_amount": 390000.00,
        "currency": "USD",
        "created_date": "2026-01-20T00:00:00",
        "approval_status": "Approved",
        "description": "Enterprise ERP System - ERPMax Solutions proposal"
    }
    requisitions_db["REQ-3024002"] = {
        "id": "REQ-3024002",
        "requisition_number": "REQ-3024002",
        "requester": "Jane Doe",
        "status": "Pending Approval",
        "total_amount": 450000.00,
        "currency": "USD",
        "created_date": "2026-01-22T00:00:00",
        "approval_status": "Pending",
        "description": "Enterprise ERP System - IntegraPro Systems proposal"
    }
    requisitions_db["REQ-3024003"] = {
        "id": "REQ-3024003",
        "requisition_number": "REQ-3024003",
        "requester": "Bob Wilson",
        "status": "Submitted",
        "total_amount": 290000.00,
        "currency": "USD",
        "created_date": "2026-01-25T00:00:00",
        "approval_status": "Pending",
        "description": "Enterprise ERP System - CloudFirst ERP proposal"
    }
    
    # Invoices - Hardcoded historical data
    
    # ERPMax Solutions invoices (paid, good history)
    invoices_db["INV-4024001"] = {
        "id": "INV-4024001",
        "invoice_number": "INV-4024001",
        "po_number": "PO-2024001",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "amount": 125000.00,
        "currency": "USD",
        "status": "Paid",
        "due_date": "2024-07-15T00:00:00",
        "created_date": "2024-06-20T00:00:00",
        "paid_date": "2024-07-10T00:00:00"
    }
    invoices_db["INV-4024002"] = {
        "id": "INV-4024002",
        "invoice_number": "INV-4024002",
        "po_number": "PO-2024002",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "amount": 45000.00,
        "currency": "USD",
        "status": "Paid",
        "due_date": "2024-10-20T00:00:00",
        "created_date": "2024-09-25T00:00:00",
        "paid_date": "2024-10-15T00:00:00"
    }
    invoices_db["INV-4025001"] = {
        "id": "INV-4025001",
        "invoice_number": "INV-4025001",
        "po_number": "PO-2025001",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "amount": 97500.00,
        "currency": "USD",
        "status": "Paid",
        "due_date": "2025-02-10T00:00:00",
        "created_date": "2025-01-15T00:00:00",
        "paid_date": "2025-02-05T00:00:00"
    }
    invoices_db["INV-4025002"] = {
        "id": "INV-4025002",
        "invoice_number": "INV-4025002",
        "po_number": "PO-2025002",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "amount": 35000.00,
        "currency": "USD",
        "status": "Under Review",
        "due_date": "2025-09-05T00:00:00",
        "created_date": "2025-08-10T00:00:00"
    }
    
    # CloudFirst ERP invoices (limited, one late payment)
    invoices_db["INV-4025003"] = {
        "id": "INV-4025003",
        "invoice_number": "INV-4025003",
        "po_number": "PO-2025003",
        "supplier_id": "SUP-1002",
        "supplier_name": "CloudFirst ERP",
        "amount": 15000.00,
        "currency": "USD",
        "status": "Paid",
        "due_date": "2025-04-15T00:00:00",
        "created_date": "2025-03-20T00:00:00",
        "paid_date": "2025-04-25T00:00:00",
        "notes": "Payment delayed due to invoice discrepancy"
    }
    invoices_db["INV-4025004"] = {
        "id": "INV-4025004",
        "invoice_number": "INV-4025004",
        "po_number": "PO-2025004",
        "supplier_id": "SUP-1002",
        "supplier_name": "CloudFirst ERP",
        "amount": 8500.00,
        "currency": "USD",
        "status": "Submitted",
        "due_date": "2025-12-20T00:00:00",
        "created_date": "2025-11-25T00:00:00"
    }
    
    # IntegraPro invoice
    invoices_db["INV-4024003"] = {
        "id": "INV-4024003",
        "invoice_number": "INV-4024003",
        "po_number": "PO-2024003",
        "supplier_id": "SUP-1001",
        "supplier_name": "IntegraPro Systems",
        "amount": 75000.00,
        "currency": "USD",
        "status": "Paid",
        "due_date": "2024-05-10T00:00:00",
        "created_date": "2024-04-15T00:00:00",
        "paid_date": "2024-05-05T00:00:00"
    }
    
    # ANOMALY: Duplicate invoice from duplicate supplier
    invoices_db["INV-4025005"] = {
        "id": "INV-4025005",
        "invoice_number": "INV-4025005",
        "po_number": "PO-2025005",
        "supplier_id": "SUP-1003",  # Duplicate supplier
        "supplier_name": "ERP Max Solutions Inc",
        "amount": 85000.00,
        "currency": "USD",
        "status": "Submitted",
        "due_date": "2025-08-15T00:00:00",
        "created_date": "2025-07-20T00:00:00",
        "anomaly_flag": "Invoice from duplicate supplier SUP-1003 (duplicate of SUP-1000)"
    }
    
    # ANOMALY: Invoice amount doesn't match PO
    invoices_db["INV-4025006"] = {
        "id": "INV-4025006",
        "invoice_number": "INV-4025006",
        "po_number": "PO-2025002",  # PO amount is $35,000
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "amount": 42000.00,  # Invoice is $7,000 more than PO!
        "currency": "USD",
        "status": "Rejected",
        "due_date": "2025-09-15T00:00:00",
        "created_date": "2025-08-20T00:00:00",
        "anomaly_flag": "Invoice amount ($42,000) exceeds PO amount ($35,000) by $7,000",
        "rejection_reason": "Amount mismatch - requires PO amendment or new PO"
    }
    
    # ANOMALY: Overdue invoice from stale supplier
    invoices_db["INV-4023001"] = {
        "id": "INV-4023001",
        "invoice_number": "INV-4023001",
        "po_number": "PO-2023001",
        "supplier_id": "SUP-1004",  # Legacy Systems Corp
        "supplier_name": "Legacy Systems Corp",
        "amount": 120000.00,
        "currency": "USD",
        "status": "Paid",
        "due_date": "2023-07-15T00:00:00",
        "created_date": "2023-06-20T00:00:00",
        "paid_date": "2023-08-01T00:00:00",
        "notes": "Late payment - 17 days overdue"
    }
    
    # Contracts - Hardcoded
    
    # ERPMax Solutions - Active contract with good terms
    contracts_db["CON-5024001"] = {
        "id": "CON-5024001",
        "contract_number": "CON-5024001",
        "title": "Enterprise ERP License and Support Agreement - ERPMax Solutions",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "start_date": "2024-06-01T00:00:00",
        "end_date": "2027-05-31T00:00:00",
        "value": 450000.00,
        "currency": "USD",
        "status": "Active",
        "terms": {
            "payment_terms": "Net 30",
            "renewal": "Auto-renewal with 90-day notice",
            "sla_uptime": "99.95%",
            "support_hours": "24/7"
        }
    }
    
    # CloudFirst ERP - Pilot contract, smaller scope
    contracts_db["CON-5025001"] = {
        "id": "CON-5025001",
        "contract_number": "CON-5025001",
        "title": "Pilot Program Agreement - CloudFirst ERP",
        "supplier_id": "SUP-1002",
        "supplier_name": "CloudFirst ERP",
        "start_date": "2025-03-01T00:00:00",
        "end_date": "2025-12-31T00:00:00",
        "value": 25000.00,
        "currency": "USD",
        "status": "Active",
        "terms": {
            "payment_terms": "Net 15",
            "renewal": "Evaluation required for renewal",
            "sla_uptime": "99.9%",
            "support_hours": "Business hours only"
        }
    }
    
    # IntegraPro Systems - Integration services contract
    contracts_db["CON-5024002"] = {
        "id": "CON-5024002",
        "contract_number": "CON-5024002",
        "title": "Integration Platform Services - IntegraPro Systems",
        "supplier_id": "SUP-1001",
        "supplier_name": "IntegraPro Systems",
        "start_date": "2024-04-01T00:00:00",
        "end_date": "2026-03-31T00:00:00",
        "value": 200000.00,
        "currency": "USD",
        "status": "Active",
        "terms": {
            "payment_terms": "Net 30",
            "renewal": "1-year renewal option",
            "sla_uptime": "99.99%",
            "support_hours": "24/7"
        }
    }
    
    # Expired contract with ERPMax for reference
    contracts_db["CON-5023001"] = {
        "id": "CON-5023001",
        "contract_number": "CON-5023001",
        "title": "Legacy System Maintenance - ERPMax Solutions",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "start_date": "2022-01-01T00:00:00",
        "end_date": "2024-05-31T00:00:00",
        "value": 180000.00,
        "currency": "USD",
        "status": "Expired",
        "terms": {
            "payment_terms": "Net 30",
            "renewal": "Replaced by CON-5024001",
            "sla_uptime": "99.9%",
            "support_hours": "Business hours"
        }
    }
    
    # ANOMALY: Duplicate contract with duplicate supplier
    contracts_db["CON-5025002"] = {
        "id": "CON-5025002",
        "contract_number": "CON-5025002",
        "title": "ERP Extension Services - ERP Max Solutions Inc",
        "supplier_id": "SUP-1003",  # Duplicate supplier
        "supplier_name": "ERP Max Solutions Inc",
        "start_date": "2025-07-01T00:00:00",
        "end_date": "2026-06-30T00:00:00",
        "value": 100000.00,
        "currency": "USD",
        "status": "Active",
        "terms": {
            "payment_terms": "Net 30",
            "renewal": "Annual",
            "sla_uptime": "99.9%",
            "support_hours": "Business hours"
        },
        "anomaly_flag": "Contract with duplicate supplier SUP-1003 (same as SUP-1000 ERPMax Solutions)"
    }
    
    # ANOMALY: Contract with obsolete supplier still marked active
    contracts_db["CON-5022001"] = {
        "id": "CON-5022001",
        "contract_number": "CON-5022001",
        "title": "Legacy Platform Maintenance - Legacy Systems Corp",
        "supplier_id": "SUP-1004",
        "supplier_name": "Legacy Systems Corp",
        "start_date": "2022-01-01T00:00:00",
        "end_date": "2024-12-31T00:00:00",
        "value": 240000.00,
        "currency": "USD",
        "status": "Active",  # Still marked active but end date passed!
        "terms": {
            "payment_terms": "Net 45",
            "renewal": "None",
            "sla_uptime": "99%",
            "support_hours": "Business hours"
        },
        "anomaly_flag": "Contract expired 2024-12-31 but status still marked as Active"
    }
    
    # ANOMALY: Contract value mismatch with cumulative POs
    contracts_db["CON-5024003"] = {
        "id": "CON-5024003",
        "contract_number": "CON-5024003",
        "title": "Additional Services Agreement - ERPMax Solutions",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "start_date": "2024-09-01T00:00:00",
        "end_date": "2025-08-31T00:00:00",
        "value": 30000.00,  # Contract limit is $30K
        "currency": "USD",
        "status": "Active",
        "terms": {
            "payment_terms": "Net 30",
            "renewal": "None",
            "sla_uptime": "99.95%",
            "support_hours": "24/7"
        },
        "total_po_value": 45000.00,  # But POs total $45K - exceeded by $15K
        "anomaly_flag": "Total PO value ($45,000) exceeds contract limit ($30,000) by $15,000"
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
    
    # Proposals - hardcoded to match Excel vendor files for RFP-2026-001
    
    # ERPMax Solutions Proposal
    proposals_db["PROP-6024001"] = {
        "id": "PROP-6024001",
        "rfp_id": "RFP-2026-001",
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "status": "Under Review",
        "submitted_date": "2026-01-25T00:00:00",
        "pricing": {
            "total": 390000,
            "currency": "USD",
            "breakdown": [
                {"item": "Implementation", "amount": 156000},
                {"item": "Licensing", "amount": 136500},
                {"item": "Support (yearly)", "amount": 97500}
            ]
        },
        "sla": {
            "uptime": 99.95,
            "response_time_hours": 1,
            "resolution_time_hours": 4,
            "penalties": True,
            "penalty_details": "5% credit per 0.1% below uptime"
        },
        "compliance": {
            "gdpr": True,
            "iso27001": True,
            "soc2": True,
            "notes": "Annual audit completed Jan 2026"
        },
        "functional_coverage": [
            {"requirement_id": "REQ-001", "status": "Full", "notes": None},
            {"requirement_id": "REQ-002", "status": "Full", "notes": None},
            {"requirement_id": "REQ-003", "status": "Full", "notes": None},
            {"requirement_id": "REQ-004", "status": "Full", "notes": None},
            {"requirement_id": "REQ-005", "status": "Full", "notes": None},
            {"requirement_id": "REQ-006", "status": "Full", "notes": None},
            {"requirement_id": "REQ-007", "status": "Full", "notes": None},
            {"requirement_id": "REQ-008", "status": "Partial", "notes": "Progressive web app available, native app in development"},
            {"requirement_id": "REQ-009", "status": "Full", "notes": None},
            {"requirement_id": "REQ-010", "status": "Partial", "notes": "Basic integration available, advanced features require customization"}
        ],
        "delivery_weeks": 16,
        "validity_days": 90
    }
    
    # IntegraPro Systems Proposal
    proposals_db["PROP-6024002"] = {
        "id": "PROP-6024002",
        "rfp_id": "RFP-2026-001",
        "supplier_id": "SUP-1001",
        "supplier_name": "IntegraPro Systems",
        "status": "Under Review",
        "submitted_date": "2026-01-28T00:00:00",
        "pricing": {
            "total": 450000,
            "currency": "USD",
            "breakdown": [
                {"item": "Implementation", "amount": 180000},
                {"item": "Licensing", "amount": 157500},
                {"item": "Support (yearly)", "amount": 112500}
            ]
        },
        "sla": {
            "uptime": 99.99,
            "response_time_hours": 0.5,
            "resolution_time_hours": 2,
            "penalties": True,
            "penalty_details": "10% credit per 0.1% below uptime"
        },
        "compliance": {
            "gdpr": True,
            "iso27001": True,
            "soc2": True,
            "notes": "Continuous compliance monitoring"
        },
        "functional_coverage": [
            {"requirement_id": "REQ-001", "status": "Full", "notes": None},
            {"requirement_id": "REQ-002", "status": "Full", "notes": None},
            {"requirement_id": "REQ-003", "status": "Full", "notes": None},
            {"requirement_id": "REQ-004", "status": "Full", "notes": None},
            {"requirement_id": "REQ-005", "status": "Full", "notes": None},
            {"requirement_id": "REQ-006", "status": "Full", "notes": None},
            {"requirement_id": "REQ-007", "status": "Full", "notes": None},
            {"requirement_id": "REQ-008", "status": "Full", "notes": None},
            {"requirement_id": "REQ-009", "status": "Full", "notes": None},
            {"requirement_id": "REQ-010", "status": "Full", "notes": None}
        ],
        "delivery_weeks": 20,
        "validity_days": 60
    }
    
    # CloudFirst ERP Proposal
    proposals_db["PROP-6024003"] = {
        "id": "PROP-6024003",
        "rfp_id": "RFP-2026-001",
        "supplier_id": "SUP-1002",
        "supplier_name": "CloudFirst ERP",
        "status": "Under Review",
        "submitted_date": "2026-01-30T00:00:00",
        "pricing": {
            "total": 290000,
            "currency": "USD",
            "breakdown": [
                {"item": "Implementation", "amount": 116000},
                {"item": "Licensing", "amount": 101500},
                {"item": "Support (yearly)", "amount": 72500}
            ]
        },
        "sla": {
            "uptime": 99.9,
            "response_time_hours": 2,
            "resolution_time_hours": 8,
            "penalties": False,
            "penalty_details": "Best effort basis"
        },
        "compliance": {
            "gdpr": True,
            "iso27001": False,
            "soc2": False,
            "notes": "ISO 27001 certification expected Q2 2026, SOC 2 Type I only"
        },
        "functional_coverage": [
            {"requirement_id": "REQ-001", "status": "Full", "notes": None},
            {"requirement_id": "REQ-002", "status": "Partial", "notes": "Real-time updates every 5 minutes, true real-time planned for Q3"},
            {"requirement_id": "REQ-003", "status": "Full", "notes": None},
            {"requirement_id": "REQ-004", "status": "Roadmap", "notes": "Supplier portal module scheduled for Q4 2026 release"},
            {"requirement_id": "REQ-005", "status": "Partial", "notes": "Standard reports available, custom analytics requires additional module"},
            {"requirement_id": "REQ-006", "status": "Full", "notes": None},
            {"requirement_id": "REQ-007", "status": "Full", "notes": None},
            {"requirement_id": "REQ-008", "status": "None", "notes": "Mobile app not currently available, web interface is mobile-responsive"},
            {"requirement_id": "REQ-009", "status": "Partial", "notes": "Basic integration via standard APIs, full iDoc support requires customization"},
            {"requirement_id": "REQ-010", "status": "None", "notes": "Salesforce integration not currently supported"}
        ],
        "delivery_weeks": 12,
        "validity_days": 90
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
