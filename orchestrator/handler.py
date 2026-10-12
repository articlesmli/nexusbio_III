# orchestrator/handler.py
import json
import uuid
import re
from datetime import datetime
from transformers import pipeline, BioGptTokenizer, BioGptForCausalLM
from rdkit import Chem
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams

from agents.literature_miner import search_biomedical_literature
from agents.molecular_design import evaluate_compound_smiles
from agents.admet_agent import ADMETAgent
from orchestrator.agents.boltz1_agent import AlphaFoldAgent
from agents.patent_clinical_agent import PatentClinicalAgent

# Global singleton cache to prevent reloading multi-gigabyte model weights on every invocation
_CACHED_GENERATOR = None

def get_generator():
    global _CACHED_GENERATOR
    if _CACHED_GENERATOR is None:
        try:
            print("[INFO] Loading BioGPT model and tokenizer into memory (cold start)...")
            tokenizer = BioGptTokenizer.from_pretrained("microsoft/biogpt")
            model = BioGptForCausalLM.from_pretrained("microsoft/biogpt")
            _CACHED_GENERATOR = pipeline("text-generation", model=model, tokenizer=tokenizer)
        except Exception as e:
            print(f"[WARNING] Local BioGPT model load failure: {e}")
            _CACHED_GENERATOR = None
    return _CACHED_GENERATOR

def check_pains_filter(mol) -> bool:
    """
    Checks if a molecule contains PAINS (Pan Assay Interference Compounds) substructures.
    Returns True if PAINS matches are found (meaning it's a false-positive risk).
    """
    params = FilterCatalogParams()
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
    catalog = FilterCatalog(params)
    return catalog.HasMatch(mol)

def generate_smiles_with_intelligence(
    query: str, 
    generator, 
    iteration: int, 
    lit_context: list, 
    patent_context: dict, 
    previous_error: str = None
) -> tuple:
    """
    Generates a SMILES string, parses it, canonicalizes it, and returns both 
    the raw candidate and its canonical representation.
    """
    if not generator:
        raise RuntimeError(
            "Generative model pipeline is unavailable. Cannot generate SMILES from scratch "
            "without an active language model instance."
        )

    lit_summary = "No prior literature precedent found."
    if lit_context:
        lit_summary = f"Literature highlights motifs and targets related to: {str(lit_context[:2])}"

    patent_summary = f"ChEMBL/Patent matches found: {patent_context.get('found', 0)}. Known active scaffolds suggest specific binding characteristics."

    if previous_error:
        prompt = (
            f"Target: {query}\n"
            f"Intelligence Feed - Literature: {lit_summary}\n"
            f"Intelligence Feed - Patents: {patent_summary}\n"
            f"Previous Failed Attempt Error: {previous_error}\n"
            f"Task: Redesign a novel, valid chemical SMILES string for iteration {iteration} "
            f"that corrects the previous error while leveraging the intelligence feed. Output only the SMILES string:"
        )
    else:
        prompt = (
            f"Target: {query}\n"
            f"Intelligence Feed - Literature: {lit_summary}\n"
            f"Intelligence Feed - Patents: {patent_summary}\n"
            f"Task: Synthesize a novel, valid chemical SMILES string for iteration {iteration} "
            f"grounded in the provided scientific intelligence. Output only the SMILES string:"
        )

    outputs = generator(
        prompt, 
        max_length=150, 
        num_return_sequences=1, 
        do_sample=True, 
        temperature=0.7,
        return_full_text=False
    )
    generated_text = outputs[0]['generated_text']

    words = generated_text.split()
    candidate_smiles = None
    canonical_smiles = None
    
    for word in words:
        cleaned_word = re.sub(r'[^A-Za-z0-9@\+\-\=\#\(\)\[\]\/\\.]', '', word)
        if len(cleaned_word) > 3:
            mol = Chem.MolFromSmiles(cleaned_word)
            if mol is not None:
                candidate_smiles = cleaned_word
                canonical_smiles = Chem.MolToSmiles(mol, canonical=True)
                break

    if not candidate_smiles or not canonical_smiles:
        raise ValueError(f"Model generated text contained no valid RDKit-parseable SMILES: {generated_text}")

    return candidate_smiles, canonical_smiles

def run_autonomous_discovery_loop(event: dict = None):
    event = event or {}
    session_id = event.get("session_id", f"sess_loop_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}")
    query = event.get("query", "COX-2 selective inhibitors with novel profiles")
    
    protein_sequence = event.get("sequence", "MKTLLILAVIMIFLLQVQGKVFEEAMKKYKGRVTVGSQLVKGQQVLVFGNK")
    max_iterations = event.get("max_iterations", 3)
    
    print(f"[{session_id}] Starting Autonomous Intelligence-Driven Discovery Loop with Deduplication & PAINS Check...")
    
    generator = get_generator()

    admet_agent = ADMETAgent()
    af_agent = AlphaFoldAgent()
    patent_agent = PatentClinicalAgent()
    
    tried_canonical_smiles = set()
    audit_trail = []
    
    def _log_audit(agent: str, action: str):
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "id": f"{session_id}#{timestamp}#{str(uuid.uuid4())[:8]}",
            "timestamp": timestamp,
            "agent": agent,
            "action": action
        }
        audit_trail.append(entry)
        print(f"[AUDIT] [{agent}] {action}")

    success = False
    final_classification = "REJECTED"
    best_evaluation_results = {}
    current_smiles = None
    last_error = None
    iteration = 0

    _log_audit("Literature Miner", f"Gathering baseline intelligence for target query: '{query}'")
    lit_results = search_biomedical_literature(query)
    has_precedent = len(lit_results) > 0

    _log_audit("Patent & Clinical Agent", f"Executing initial ChEMBL/Patent search for query: '{query}'")
    chembl_results = patent_agent.search_chembl(query)

    for iteration in range(1, max_iterations + 1):
        _log_audit("Orchestrator Loop", f"--- Iteration {iteration} of {max_iterations} --- Generating SMILES using intelligence & feedback...")
        
        try:
            if last_error and iteration > 1:
                lit_results = search_biomedical_literature(f"{query} analog avoiding {last_error[:30]}")

            # 1. GENERATE WITH INTELLIGENCE & CANONICALIZATION
            current_smiles, canonical_smiles = generate_smiles_with_intelligence(
                query, generator, iteration, lit_results, chembl_results, last_error
            )
            
            # 2. DEDUPLICATION CHECK
            if canonical_smiles in tried_canonical_smiles:
                last_error = f"Candidate {current_smiles} (Canonical: {canonical_smiles}) was already tested in a previous iteration."
                _log_audit("Deduplication Filter", f"Duplicate structure detected. Skipping agent evaluation and retrying...")
                continue
            
            tried_canonical_smiles.add(canonical_smiles)
            _log_audit("Generative Agent", f"Successfully generated unique canonical SMILES: {canonical_smiles}")

            # 3. PAINS FILTER CHECK
            mol_obj = Chem.MolFromSmiles(canonical_smiles)
            if check_pains_filter(mol_obj):
                last_error = f"Candidate {current_smiles} failed PAINS filter (Pan Assay Interference Compound false-positive risk)."
                _log_audit("PAINS Filter", f"Compound flagged as promiscuous binder. Rejecting...")
                continue
            
            # 4. CHECK: Run structural folding and property evaluations
            alphafold_results = af_agent.predict_structure(protein_sequence)
            chem_results = evaluate_compound_smiles(current_smiles)
            admet_results = admet_agent.evaluate_molecule(current_smiles)
            
            metrics = chem_results.get("metrics", {})
            qed = metrics.get("qed", 0.0)
            lipinski_violations = metrics.get("lipinski_violations", 0)
            toxicity_risk = admet_results.get("toxicity_risk", "High")
            binding_pocket_valid = alphafold_results.get("binding_pocket_predicted", False)

            _log_audit("Molecular Evaluation", f"QED: {qed} | Lipinski Violations: {lipinski_violations} | Toxicity: {toxicity_risk} | Pocket Valid: {binding_pocket_valid}")

            is_toxic = (toxicity_risk == "High")
            
            # 5. ACCEPTANCE GATE
            if not is_toxic and binding_pocket_valid:
                if lipinski_violations > 0 and qed < 0.6:
                    classification = "BREAKTHROUGH_DETECTED: Beyond-Rule-of-Five (bRoF) Unconventional Molecule with High Binding Potential."
                elif not has_precedent:
                    classification = "BREAKTHROUGH_DETECTED: Novel, unprecedented, but physically valid mechanism."
                else:
                    classification = "INCREMENTAL_DISCOVERY: Validated known pathway with strong precedent."
                
                success = True
                final_classification = classification
                best_evaluation_results = {
                    "iteration": iteration,
                    "literature_support": lit_results,
                    "alphafold_structure": alphafold_results,
                    "molecular_evaluation": chem_results,
                    "admet_profile": admet_results
                }
                _log_audit("Objective Gate", f"Accepted candidate: {classification}")
                break
            else:
                last_error = f"Candidate {current_smiles} failed checks (Toxicity: {toxicity_risk}, Pocket Valid: {binding_pocket_valid})"
                _log_audit("Objective Gate", f"Iteration {iteration} failed criteria. Feeding error feedback into next generation cycle...")

        except Exception as e:
            last_error = str(e)
            _log_audit("Error Handler", f"Exception caught in iteration {iteration}: {last_error}")

    reported_smiles = current_smiles if success else None

    # Construct the final output payload
    output_payload = {
        "statusCode": 200,
        "session_id": session_id,
        "success": success,
        "discovery_classification": final_classification,
        "iterations_run": iteration,
        "final_smiles": reported_smiles,
        "results": best_evaluation_results if success else {"status": "Max iterations reached without meeting constraints."},
        "patent_clinical_data": chembl_results,
        "audit_trail": audit_trail
    }

    # Automatically persist results to disk so breakthroughs are never lost
    filename = f"discovery_run_{session_id}.json"
    try:
        with open(filename, "w") as f:
            json.dump(output_payload, f, indent=2)
        print(f"[AUDIT] [Orchestrator Loop] Results successfully persisted to disk: {filename}")
    except Exception as e:
        print(f"[WARNING] Failed to write run results to disk: {e}")

    return output_payload

if __name__ == "__main__":
    result = run_autonomous_discovery_loop()
    print(json.dumps(result, indent=2))