import pytest
from cheminformatics_sandbox.utils.descriptors import calculate_molecular_metrics

def test_valid_smiles_aspirin():
    """Test property calculations for a well-known molecule: Aspirin."""
    aspirin_smiles = "CC(=O)Oc1ccccc1C(=O)O"
    
    result = calculate_molecular_metrics(aspirin_smiles)
    
    assert result is not None
    assert "error" not in result
    assert "molecular_weight" in result
    assert "log_p" in result
    assert "qed" in result
    
    # Aspirin molecular weight is roughly 180.16 g/mol
    assert 179.0 <= result["molecular_weight"] <= 181.0
    assert result.get("lipinski_violations", 0) == 0

def test_valid_smiles_caffeine():
    """Test property calculations for Caffeine."""
    caffeine_smiles = "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"
    
    result = calculate_molecular_metrics(caffeine_smiles)
    
    assert result is not None
    assert "error" not in result
    # Caffeine molecular weight is roughly 194.19 g/mol
    assert 193.0 <= result["molecular_weight"] <= 195.0

def test_invalid_smiles_handling():
    """Ensure invalid SMILES strings are handled gracefully and return an error dictionary."""
    invalid_smiles = "INVALID_SMILES_STRING_XYZ"
    
    result = calculate_molecular_metrics(invalid_smiles)
    
    assert result is not None
    assert "error" in result