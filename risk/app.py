"""
Risk Assessment Service
Provides supplier risk scoring (separate from SAP Ariba).
"""

import os
import random
from datetime import datetime, timedelta
from flask import Flask, jsonify

app = Flask(__name__)

# ============== Mock Risk Data ==============

risk_scores_db = {}


def generate_risk_data():
    """Generate mock risk scores for suppliers"""
    
    # Known supplier IDs (matching Ariba mock)
    supplier_ids = [f"SUP-{1000 + i}" for i in range(5)]
    
    risk_factors = [
        "Financial Stability",
        "Compliance History", 
        "Delivery Performance",
        "Quality Issues",
        "Geopolitical Risk",
        "Cybersecurity",
        "ESG Score"
    ]
    
    risk_levels = ["Low", "Medium", "High", "Critical"]
    
    for supplier_id in supplier_ids:
        overall_score = round(random.uniform(1, 10), 1)
        
        risk_scores_db[supplier_id] = {
            "supplier_id": supplier_id,
            "overall_risk_score": overall_score,
            "risk_level": risk_levels[min(int(overall_score / 2.5), 3)],
            "last_assessed": (datetime.now() - timedelta(days=random.randint(1, 90))).isoformat(),
            "next_review": (datetime.now() + timedelta(days=random.randint(30, 180))).isoformat(),
            "factors": [
                {
                    "name": factor,
                    "score": round(random.uniform(1, 10), 1),
                    "weight": round(random.uniform(0.1, 0.3), 2),
                    "trend": random.choice(["improving", "stable", "declining"])
                }
                for factor in random.sample(risk_factors, random.randint(3, 6))
            ],
            "alerts": [
                {
                    "type": random.choice(["warning", "critical", "info"]),
                    "message": random.choice([
                        "Payment delays reported in last quarter",
                        "Pending compliance certification renewal",
                        "New sanctions screening required",
                        "Quality audit scheduled",
                        "Financial statement review pending"
                    ]),
                    "date": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
                }
                for _ in range(random.randint(0, 3))
            ]
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
    if supplier_id not in risk_scores_db:
        return jsonify({
            "error": f"No risk data for supplier '{supplier_id}'",
            "supplier_id": supplier_id,
            "status": "not_found"
        }), 404
    
    return jsonify(risk_scores_db[supplier_id])


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
