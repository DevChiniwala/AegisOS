"""Tests for feature store timezone fix."""
import pytest
from datetime import datetime, timezone, timedelta
from services.feature_engine.store import FeatureStore


class TestFeatureStore:
    def setup_method(self):
        self.store = FeatureStore()

    def test_store_and_retrieve(self):
        ts = datetime.now(timezone.utc)
        self.store.store_features("user1", {"f1": 0.5}, ts)
        result = self.store.get_features("user1")
        assert result == {"f1": 0.5}

    def test_get_features_nonexistent(self):
        assert self.store.get_features("unknown") is None

    def test_naive_timestamp_normalized(self):
        naive_ts = datetime(2024, 1, 1, 12, 0, 0)
        self.store.store_features("user2", {"f1": 1.0}, naive_ts)
        history = self.store.get_feature_history("user2", window_seconds=999999999)
        assert len(history) == 1
        assert history[0]['timestamp'].tzinfo is not None

    def test_aware_timestamp_preserved(self):
        aware_ts = datetime.now(timezone.utc)
        self.store.store_features("user3", {"f1": 2.0}, aware_ts)
        history = self.store.get_feature_history("user3", window_seconds=999999999)
        assert len(history) == 1
        assert history[0]['timestamp'].tzinfo == timezone.utc

    def test_history_window_filtering(self):
        now = datetime.now(timezone.utc)
        old_ts = now - timedelta(seconds=3600)
        recent_ts = now - timedelta(seconds=30)

        self.store.store_features("user4", {"f1": 1.0}, old_ts)
        self.store.store_features("user4", {"f1": 2.0}, recent_ts)

        history = self.store.get_feature_history("user4", window_seconds=60)
        assert len(history) == 1
        assert history[0]['features']['f1'] == 2.0

    def test_mixed_naive_aware_no_error(self):
        """Storing naive then querying should not raise TypeError."""
        naive_ts = datetime(2024, 6, 1, 10, 0, 0)
        self.store.store_features("user5", {"f1": 3.0}, naive_ts)
        history = self.store.get_feature_history("user5", window_seconds=999999999)
        assert len(history) == 1
