# agents/admet_agent.py
from rdkit import Chem
from rdkit.Chem import Descriptors

class ADMETAgent:
    def __init__(self):
        self.name = "ADMET_Toxicity_Agent"

    def evaluate_molecule(self, smiles: str) -> dict:
        mol = Chem.MolFromSmiles(smiles)
        if not mol:
            raise ValueError("Invalid SMILES for ADMET evaluation.")
            
        mol_wt = Descriptors.ExactMolWt(mol)
        logp = Descriptors.MolLogP(mol)
        
        # Dynamic risk calculation based on physiological rules
        risk_flags = 0
        if mol_wt > 500: risk_flags += 1
        if logp > 4.5: risk_flags += 1
        
        toxicity_risk = "High" if risk_flags >= 2 else ("Moderate" if risk_flags == 1 else "Low")
        
        return {
            "smiles": smiles,
            "calculated_molecular_weight": mol_wt,
            "calculated_logp": logp,
            "toxicity_risk": toxicity_risk,
            "status": "Evaluated"
        }