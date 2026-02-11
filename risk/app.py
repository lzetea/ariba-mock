"""
Risk Assessment Service
Provides supplier risk scoring (separate from SAP Ariba).
"""

import os
import hashlib
from flask import Flask, jsonify

app = Flask(__name__)

# ============== Mock Risk Data ==============

risk_scores_db = {}


def generate_risk_data():
    """Generate mock risk scores for suppliers - hardcoded to match vendor Excel files"""
    
    # ERPMax Solutions - Low risk, fully compliant
    risk_scores_db["SUP-1000"] = {
        "supplier_id": "SUP-1000",
        "supplier_name": "ERPMax Solutions",
        "overall_risk_score": 2.1,
        "risk_level": "Low",
        "last_assessed": "2026-01-15T00:00:00",
        "next_review": "2026-07-15T00:00:00",
        "factors": [
            {"name": "Financial Stability", "score": 2.0, "weight": 0.25, "trend": "stable"},
            {"name": "Compliance History", "score": 1.5, "weight": 0.20, "trend": "improving"},
            {"name": "Delivery Performance", "score": 2.5, "weight": 0.20, "trend": "stable"},
            {"name": "Quality Issues", "score": 2.0, "weight": 0.15, "trend": "stable"},
            {"name": "Cybersecurity", "score": 2.0, "weight": 0.10, "trend": "improving"},
            {"name": "ESG Score", "score": 3.0, "weight": 0.10, "trend": "stable"}
        ],
        "alerts": [
            {
                "type": "info",
                "message": "Annual security audit completed successfully",
                "date": "2026-01-10T00:00:00"
            }
        ]
    }
    
    # IntegraPro Systems - Very low risk, excellent track record
    risk_scores_db["SUP-1001"] = {
        "supplier_id": "SUP-1001",
        "supplier_name": "IntegraPro Systems",
        "overall_risk_score": 1.8,
        "risk_level": "Low",
        "last_assessed": "2026-01-20T00:00:00",
        "next_review": "2026-07-20T00:00:00",
        "factors": [
            {"name": "Financial Stability", "score": 1.5, "weight": 0.25, "trend": "improving"},
            {"name": "Compliance History", "score": 1.0, "weight": 0.20, "trend": "stable"},
            {"name": "Delivery Performance", "score": 2.0, "weight": 0.20, "trend": "stable"},
            {"name": "Quality Issues", "score": 2.0, "weight": 0.15, "trend": "improving"},
            {"name": "Cybersecurity", "score": 1.5, "weight": 0.10, "trend": "stable"},
            {"name": "ESG Score", "score": 2.5, "weight": 0.10, "trend": "improving"}
        ],
        "alerts": []
    }
    
    # CloudFirst ERP - Medium risk, newer company with compliance gaps
    risk_scores_db["SUP-1002"] = {
        "supplier_id": "SUP-1002",
        "supplier_name": "CloudFirst ERP",
        "overall_risk_score": 4.5,
        "risk_level": "Medium",
        "last_assessed": "2026-01-25T00:00:00",
        "next_review": "2026-04-25T00:00:00",
        "factors": [
            {"name": "Financial Stability", "score": 5.0, "weight": 0.25, "trend": "stable"},
            {"name": "Compliance History", "score": 6.0, "weight": 0.20, "trend": "improving"},
            {"name": "Delivery Performance", "score": 3.5, "weight": 0.20, "trend": "stable"},
            {"name": "Quality Issues", "score": 4.0, "weight": 0.15, "trend": "stable"},
            {"name": "Cybersecurity", "score": 5.5, "weight": 0.10, "trend": "declining"},
            {"name": "ESG Score", "score": 3.0, "weight": 0.10, "trend": "stable"}
        ],
        "alerts": [
            {
                "type": "warning",
                "message": "ISO 27001 certification pending - expected Q2 2026",
                "date": "2026-01-20T00:00:00"
            },
            {
                "type": "warning",
                "message": "SOC 2 Type II certification not yet obtained",
                "date": "2026-01-15T00:00:00"
            },
            {
                "type": "info",
                "message": "Company founded in 2024 - limited track record",
                "date": "2026-01-10T00:00:00"
            }
        ]
    }
    
    # ANOMALY: Duplicate supplier - same as SUP-1000 but different ID
    risk_scores_db["SUP-1003"] = {
        "supplier_id": "SUP-1003",
        "supplier_name": "ERP Max Solutions Inc",
        "overall_risk_score": 2.3,
        "risk_level": "Low",
        "last_assessed": "2025-06-15T00:00:00",
        "next_review": "2025-12-15T00:00:00",
        "factors": [
            {"name": "Financial Stability", "score": 2.0, "weight": 0.25, "trend": "stable"},
            {"name": "Compliance History", "score": 1.5, "weight": 0.20, "trend": "stable"},
            {"name": "Delivery Performance", "score": 2.5, "weight": 0.20, "trend": "stable"},
            {"name": "Quality Issues", "score": 2.2, "weight": 0.15, "trend": "stable"},
            {"name": "Cybersecurity", "score": 2.0, "weight": 0.10, "trend": "stable"},
            {"name": "ESG Score", "score": 3.0, "weight": 0.10, "trend": "stable"}
        ],
        "alerts": [
            {
                "type": "critical",
                "message": "DUPLICATE SUPPLIER DETECTED - Same entity as SUP-1000 (ERPMax Solutions)",
                "date": "2025-08-01T00:00:00"
            },
            {
                "type": "warning",
                "message": "Recommend consolidation with master supplier record SUP-1000",
                "date": "2025-08-01T00:00:00"
            }
        ],
        "anomaly_flag": "Duplicate supplier entry - matches SUP-1000 ERPMax Solutions"
    }
    
    # ANOMALY: Obsolete supplier with high risk
    risk_scores_db["SUP-1004"] = {
        "supplier_id": "SUP-1004",
        "supplier_name": "Legacy Systems Corp",
        "overall_risk_score": 7.5,
        "risk_level": "High",
        "last_assessed": "2023-12-01T00:00:00",  # Assessment over 2 years old!
        "next_review": "2024-06-01T00:00:00",  # Review overdue by 2 years!
        "factors": [
            {"name": "Financial Stability", "score": 7.0, "weight": 0.25, "trend": "declining"},
            {"name": "Compliance History", "score": 6.5, "weight": 0.20, "trend": "declining"},
            {"name": "Delivery Performance", "score": 8.0, "weight": 0.20, "trend": "declining"},
            {"name": "Quality Issues", "score": 7.5, "weight": 0.15, "trend": "stable"},
            {"name": "Cybersecurity", "score": 8.5, "weight": 0.10, "trend": "declining"},
            {"name": "ESG Score", "score": 6.0, "weight": 0.10, "trend": "stable"}
        ],
        "alerts": [
            {
                "type": "critical",
                "message": "STALE DATA - Risk assessment overdue by 24+ months",
                "date": "2024-06-01T00:00:00"
            },
            {
                "type": "critical",
                "message": "No activity recorded since December 2023",
                "date": "2024-01-15T00:00:00"
            },
            {
                "type": "warning",
                "message": "Contract expired but supplier still marked active in system",
                "date": "2025-01-05T00:00:00"
            },
            {
                "type": "warning",
                "message": "Financial stability concerns - recommend review before new orders",
                "date": "2023-11-20T00:00:00"
            }
        ],
        "anomaly_flag": "Obsolete supplier - no activity in 24+ months, stale risk assessment"
    }


# Initialize mock data
generate_risk_data()


# ============== API Endpoints ==============

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "service": "risk-assessment"})


@app.route("/api/risk/score/<supplier_id>")
def get_risk_score(supplier_id):
    """Get risk score for a specific supplier"""
    if supplier_id in risk_scores_db:
        return jsonify(risk_scores_db[supplier_id])
    
    # Generate dynamic risk score for unknown suppliers
    # Use supplier_id hash to generate consistent but varied scores
    hash_val = int(hashlib.md5(supplier_id.encode()).hexdigest(), 16)
    
    # Generate deterministic but varied scores based on supplier_id
    base_score = 3.0 + (hash_val % 50) / 10  # Score between 3.0 and 8.0
    
    risk_levels = ["Low", "Medium", "High", "Critical"]
    risk_level = risk_levels[min(int(base_score / 2.5), 3)]
    
    # Generate factor scores
    factors = [
        {"name": "Financial Stability", "score": round(2.0 + (hash_val % 60) / 10, 1), "weight": 0.25, "trend": "unknown"},
        {"name": "Compliance History", "score": round(2.5 + (hash_val % 55) / 10, 1), "weight": 0.20, "trend": "unknown"},
        {"name": "Delivery Performance", "score": round(2.0 + (hash_val % 65) / 10, 1), "weight": 0.20, "trend": "unknown"},
        {"name": "Quality Issues", "score": round(2.5 + (hash_val % 50) / 10, 1), "weight": 0.15, "trend": "unknown"},
        {"name": "Cybersecurity", "score": round(3.0 + (hash_val % 45) / 10, 1), "weight": 0.10, "trend": "unknown"},
        {"name": "ESG Score", "score": round(3.0 + (hash_val % 40) / 10, 1), "weight": 0.10, "trend": "unknown"}
    ]
    
    dynamic_risk = {
        "supplier_id": supplier_id,
        "supplier_name": f"Supplier {supplier_id}",
        "overall_risk_score": round(base_score, 1),
        "risk_level": risk_level,
        "last_assessed": "2026-01-01T00:00:00",
        "next_review": "2026-07-01T00:00:00",
        "factors": factors,
        "alerts": [
            {
                "type": "info",
                "message": "No historical risk data available - baseline assessment generated",
                "date": "2026-01-01T00:00:00"
            }
        ],
        "data_quality": "estimated",
        "note": "Risk score generated dynamically - no historical data in system"
    }
    
    return jsonify(dynamic_risk)


@app.route("/api/risk/scores")
def list_risk_scores():
    """List all supplier risk scores"""
    return jsonify(list(risk_scores_db.values()))


@app.route("/api/risk/high-risk")
def get_high_risk_suppliers():
    """Get suppliers with high or critical risk"""
    high_risk = [
        s for s in risk_scores_db.values() 
        if s["risk_level"] in ["High", "Critical"]
    ]
    return jsonify(high_risk)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8081))
    app.run(host="0.0.0.0", port=port)
