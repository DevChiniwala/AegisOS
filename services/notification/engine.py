"""
Notification Engine.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List
import datetime
from core.utils.logging import get_logger

logger = get_logger(__name__)

@dataclass
class Alert:
    alert_id: str
    severity: str
    title: str
    message: str
    entity_id: str
    transaction_id: str
    metadata: Dict[str, Any]
    timestamp: datetime.datetime
    channels: List[str] = field(default_factory=list)

class Channel:
    def send(self, alert: Alert):
        raise NotImplementedError

class WebSocketChannel(Channel):
    def send(self, alert: Alert):
        logger.info(f"WS Broadcast: {alert.title}")

class LogChannel(Channel):
    def send(self, alert: Alert):
        logger.warning(f"ALERT [{alert.severity}]: {alert.message}")

class WebhookChannel(Channel):
    def __init__(self, url: str):
        self.url = url
        
    def send(self, alert: Alert):
        logger.info(f"Webhook POST to {self.url} for alert {alert.alert_id}")

class NotificationEngine:
    def __init__(self):
        self.channels = {
            "ws": WebSocketChannel(),
            "log": LogChannel(),
            "webhook": WebhookChannel("http://internal-alert-webhook")
        }
        self.sent_alerts_cache = set()
        
    def send_alert(self, alert: Alert):
        # Deduplication
        dedup_key = f"{alert.entity_id}_{alert.title}_{alert.timestamp.date()}"
        if dedup_key in self.sent_alerts_cache:
            logger.debug(f"Skipping duplicate alert {dedup_key}")
            return
            
        self.sent_alerts_cache.add(dedup_key)
        
        # Routing
        for channel_name in alert.channels:
            if channel_name in self.channels:
                try:
                    self.channels[channel_name].send(alert)
                except Exception as e:
                    logger.error(f"Failed to send alert on {channel_name}: {e}")
