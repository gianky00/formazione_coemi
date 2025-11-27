from app.services.ai_extraction import _generate_prompt

def test_prompt_contains_surname_instruction():
    prompt = _generate_prompt()
    assert "COGNOME NOME" in prompt
    assert "ROSSI MARIO" in prompt
    assert "Mario Rossi" in prompt # The "convert Mario Rossi" part
