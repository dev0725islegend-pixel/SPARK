import pytest
from backend.app.services.model_gateway import ModelGateway, get_model_gateway
import os


def test_gateway_loads_mock_provider(monkeypatch):
    monkeypatch.setenv('MODEL_PROVIDER', 'mock')
    g = ModelGateway()
    assert g._provider is not None
    assert g._provider.name == 'mock'


def test_generate_uses_provider(monkeypatch):
    monkeypatch.setenv('MODEL_PROVIDER', 'mock')
    g = ModelGateway()
    res = g.generate('Hello world')
    assert 'Echo' in res.get('text', '')


def test_stream_yields_tokens(monkeypatch):
    monkeypatch.setenv('MODEL_PROVIDER', 'mock')
    g = ModelGateway()
    chunks = list(g.stream('Hello token stream'))
    assert len(chunks) > 0
    assert any('Hello' in c or 'token' in c for c in chunks)
