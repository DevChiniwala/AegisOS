"""Tests for deterministic feature encoding."""
import pytest
from unittest.mock import MagicMock
from services.feature_engine.extractors.transaction_features import TransactionFeatureExtractor, _stable_encode
from services.feature_engine.extractors.device_features import DeviceFeatureExtractor
from services.feature_engine.extractors.device_features import _stable_encode as _device_stable_encode


class TestStableEncode:
    def test_deterministic(self):
        """Same input always produces same output."""
        assert _stable_encode("MOBILE") == _stable_encode("MOBILE")
        assert _stable_encode("WEB") == _stable_encode("WEB")

    def test_different_inputs_different_outputs(self):
        assert _stable_encode("MOBILE") != _stable_encode("WEB")

    def test_output_range(self):
        for val in ["MOBILE", "WEB", "ATM", "POS", "API", ""]:
            result = _stable_encode(val)
            assert 0.0 <= result < 1.0

    def test_consistent_across_modules(self):
        """Both modules should produce the same encoding for same input."""
        assert _stable_encode("MOBILE") == _device_stable_encode("MOBILE")


class TestTransactionFeatureExtractor:
    def setup_method(self):
        self.extractor = TransactionFeatureExtractor()

    def _make_context(self):
        ctx = MagicMock()
        ctx.history = []
        ctx.user = None
        return ctx

    def test_channel_encoding_stable(self):
        tx = MagicMock()
        tx.amount = 100
        tx.channel = MagicMock(value="MOBILE")
        tx.type = MagicMock(value="TRANSFER")
        tx.currency = "USD"

        ctx = self._make_context()
        f1 = self.extractor.extract(tx, ctx)
        f2 = self.extractor.extract(tx, ctx)
        assert f1['channel_encoding'] == f2['channel_encoding']
        assert f1['transaction_type_encoding'] == f2['transaction_type_encoding']


class TestDeviceFeatureExtractor:
    def setup_method(self):
        self.extractor = DeviceFeatureExtractor()

    def test_device_type_encoding_stable(self):
        tx = MagicMock()
        ctx = MagicMock()
        ctx.device = MagicMock()
        ctx.device.last_seen_at = "2024-01-01"
        ctx.device.created_at = None
        ctx.device.device_type = "ANDROID"
        ctx.device.os = "Android 14"
        ctx.device.is_emulator = False
        ctx.device.is_rooted = False
        ctx.device.user_count = 1
        ctx.history = []
        ctx.timestamp = MagicMock()
        ctx.timestamp.__sub__ = MagicMock(return_value=MagicMock(total_seconds=MagicMock(return_value=0)))

        f1 = self.extractor.extract(tx, ctx)
        f2 = self.extractor.extract(tx, ctx)
        assert f1['device_type_encoding'] == f2['device_type_encoding']
        assert f1['os_encoding'] == f2['os_encoding']
