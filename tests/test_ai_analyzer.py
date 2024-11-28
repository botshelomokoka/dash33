import pytest
import numpy as np
from dash33.ai.analyzer import TransactionAnalyzer, AnalysisResult

def test_analyze_transactions(transaction_analyzer, sample_transactions):
    result = transaction_analyzer.analyze_transactions(sample_transactions)
    assert isinstance(result, AnalysisResult)
    assert 0 <= result.risk_score <= 1.0
    assert len(result.recommendations) > 0
    assert 'price_trend' in result.predicted_trends

def test_empty_transactions(transaction_analyzer):
    result = transaction_analyzer.analyze_transactions([])
    assert result.risk_score == 0.0
    assert "No transactions" in result.recommendations[0]

def test_risk_score_calculation(transaction_analyzer):
    amounts = np.array([1.0, 2.0, 1.5])
    score = transaction_analyzer._calculate_risk_score(amounts)
    assert 0 <= score <= 1.0

def test_trend_prediction(transaction_analyzer):
    amounts = np.array([1.0, 2.0, 3.0])
    times = np.array([1000000, 1000100, 1000200])
    trends = transaction_analyzer._predict_trends(amounts, times)
    assert trends['price_trend'] > 0  # Should show increasing trend
