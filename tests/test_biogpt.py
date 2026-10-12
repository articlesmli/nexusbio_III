# test/test_biogpt.py

import pytest
from transformers import BioGptTokenizer, BioGptForCausalLM, pipeline

def test_biogpt_initialization_and_generation():
    """
    Tests that the local BioGPT model loads successfully and generates a response.
    """
    model_name = "microsoft/biogpt"
    
    try:
        # Attempt to load tokenizer and model
        tokenizer = BioGptTokenizer.from_pretrained(model_name)
        model = BioGptForCausalLM.from_pretrained(model_name)
        
        # Initialize pipeline
        generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
        
        # Run a short test generation
        outputs = generator("Aspirin is", max_length=15, num_return_sequences=1)
        
        assert len(outputs) > 0
        assert "generated_text" in outputs[0]
        print(f"Test passed! Output: {outputs[0]['generated_text']}")
        
    except Exception as e:
        pytest.fail(f"BioGPT initialization or generation failed: {str(e)}")
