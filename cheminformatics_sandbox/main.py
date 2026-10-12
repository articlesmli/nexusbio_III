from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from utils.descriptors import calculate_molecular_metrics

app = FastAPI(
    title="NexusBio Cheminformatics Sandbox",
    description="Isolated container running RDKit for SMILES string verification and property calculation.",
    version="1.0.0"
)

class EvaluationRequest(BaseModel):
    session_id: str
    compound_id: str
    smiles: str
    target_metrics: Optional[List[str]] = []

@app.post("/evaluate-smiles")
def evaluate_smiles(request: EvaluationRequest):
    """
    Receives compound SMILES and returns RDKit-evaluated structural metrics.
    """
    metrics, success = calculate_molecular_metrics(request.smiles)
    if not success or not metrics:
        raise HTTPException(status_code=400, detail=f"Invalid SMILES string provided: {request.smiles}")
    
    return {
        "compound_id": request.compound_id,
        "valid": True,
        "canonical_smiles": metrics["canonical_smiles"],
        "metrics": {
            "qed": metrics["qed"],
            "molecular_weight": metrics["molecular_weight"],
            "log_p": metrics["log_p"],
            "lipinski_violations": metrics["lipinski_violations"]
        },
        "audit_metadata": {
            "sandbox_engine": "rdkit-python-container",
            "timestamp": datetime.utcnow().isoformat()
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "cheminformatics_sandbox"} 
