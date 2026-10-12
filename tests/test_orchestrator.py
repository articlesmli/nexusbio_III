"""
NexusBio Multi-Agent Orchestration Test
Simulates a workflow where a molecule is evaluated for ADMET properties 
and cross-referenced against public patent/clinical trial databases.
"""

from orchestrator.agents.admet_agent import ADMETAgent
from orchestrator.agents.patent_clinical_agent import PatentClinicalAgent

def run_pipeline_orchestration(smiles_input: str, search_term: str):
    print("==================================================")
    print("      NEXUSBIO MULTI-AGENT PIPELINE TEST          ")
    print("==================================================")
    
    # 1. Initialize Agents
    admet_agent = ADMETAgent()
    patent_agent = PatentClinicalAgent()
    
    # 2. Run ADMET & Toxicity Evaluation
    print(f"\n[Step 1] Running ADMET & Toxicity Evaluation...")
    admet_results = admet_agent.evaluate_molecule(smiles_input)
    print(f" -> Results: {admet_results}")
    
    # 3. Run Patent & Clinical Trials Intelligence Search
    print(f"\n[Step 2] Querying Patent and Clinical Intelligence...")
    patent_results = patent_agent.search_chembl(search_term)
    print(f" -> Results: {patent_results}")
    
    print("\n==================================================")
    print(" PIPELINE EXECUTION COMPLETE: SUCCESS ")
    print("==================================================")

if __name__ == "__main__":
    test_smiles = "CC(=O)OC1=CC=CC=C1C(=O)O"
    test_query = "aspirin"
    run_pipeline_orchestration(test_smiles, test_query)