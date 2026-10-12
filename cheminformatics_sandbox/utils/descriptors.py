from rdkit import Chem
from rdkit.Chem import Descriptors
from rdkit.Chem import QED

def calculate_molecular_metrics(smiles: str):
  mol = Chem.MolFromSmiles(smiles)
  if not mol:
    return {"error": "Invalid SMILES string"}

  canonical_smiles = Chem.MolToSmiles(mol)
  qed_score = QED.qed(mol)
  mw = Descriptors.MolWt(mol)
  logp = Descriptors.MolLogP(mol)

  h_donors = Descriptors.NumHDonors(mol)
  h_acceptors = Descriptors.NumHAcceptors(mol)

  violations = 0
  if mw > 500:
    violations += 1
  if logp > 5:
    violations += 1
  if h_donors > 5:
    violations += 1
  if h_acceptors > 10:
    violations += 1

  return {
      "canonical_smiles": canonical_smiles,
      "qed": round(qed_score, 2),
      "molecular_weight": round(mw, 2),
      "log_p": round(logp, 2),
      "lipinski_violations": violations,
      "passes_lipinski": violations <= 3,  # Clear, explicit boolean!
  }
