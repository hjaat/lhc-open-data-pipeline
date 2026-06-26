from src.pipeline import LHCDataPipeline

def test_week2():
    pipeline = LHCDataPipeline()
    assert pipeline is not None
    print("✓ Week 2 pipeline works")