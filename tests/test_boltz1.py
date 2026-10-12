"""
NexusBio Boltz1 Agent Test Suite
Validates the structural protein prediction agent, 
confidence scoring, and fallback/mock execution logic.
"""

import pytest
from orchestrator.agents.boltz1_agent import Boltz1Agent

def test_boltz1_valid_sequence():
    """Test structural prediction with a valid target protein sequence."""
    agent = Boltz1Agent()
    test_sequence = "MKTAYIAKQRQISFVKSHFSRQ"
    
    result = agent.predict_structure(test_sequence)
    
    assert result is not None
    assert result["success"] is True
    assert result["target_length"] == len(test_sequence)
    assert "confidence_score_plddt" in result
    assert result["confidence_score_plddt"] > 90.0
    assert result["binding_pocket_predicted"] is True
    assert result["audit_metadata"]["engine"] == "boltz1-fallback-mock"

def test_boltz1_invalid_sequence():
    """Ensure invalid or overly short protein sequences are handled gracefully."""
    agent = Boltz1Agent()
    short_sequence = "ABC" # Less than 5 characters
    
    result = agent.predict_structure(short_sequence)
    
    assert result is not None
    assert result["success"] is False
    assert "error" in result

def test_boltz1_empty_sequence():
    """Ensure empty sequences return failure response."""
    agent = Boltz1Agent()
    
    result = agent.predict_structure("")
    
    assert result["success"] is False
    assert "error" in result
