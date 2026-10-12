# agents/patent_clinical_agent.py
import urllib.request
import json
import urllib.parse

class PatentClinicalAgent:
    def __init__(self):
        self.name = "Patent_Clinical_Agent"
        self.chembl_base_url = "https://www.ebi.ac.uk/chembl/api/data/molecule"

    def search_chembl(self, query_term: str) -> dict:
        """
        Live ChEMBL database query without hardcoded mock overrides.
        """
        print(f"[{self.name}] Querying live ChEMBL API for: {query_term}")
        encoded_query = urllib.parse.quote(query_term)
        url = f"{self.chembl_base_url}.json?q={encoded_query}&limit=3"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'NexusBio-AutonomousAgent'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            molecules = data.get("molecules", [])
            
            if not molecules:
                return {"found": False, "query": query_term, "matches": []}
                
            results = []
            for mol in molecules:
                results.append({
                    "molecule_chembl_id": mol.get("molecule_chembl_id"),
                    "max_phase": mol.get("max_phase"),
                    "pref_name": mol.get("pref_name")
                })
            return {
                "found": True,
                "query": query_term,
                "matches": results,
                "source": "ChEMBL Live API"
            }