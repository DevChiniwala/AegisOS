"""
Behavioral profiles schemas.
"""
from dataclasses import dataclass, field
from typing import Set, Dict, Any

@dataclass
class SpendingProfile:
    mean: float = 0.0
    std: float = 0.0
    min_amt: float = 0.0
    max_amt: float = 0.0
    median: float = 0.0
    count: int = 0
    per_day_means: Dict[int, float] = field(default_factory=dict)

    def update(self, amount: float, day_of_week: int):
        self.count += 1
        # Simplified running mean
        self.mean = self.mean + (amount - self.mean) / self.count
        if self.count == 1:
            self.min_amt = amount
            self.max_amt = amount
        else:
            self.min_amt = min(self.min_amt, amount)
            self.max_amt = max(self.max_amt, amount)
        
        if day_of_week not in self.per_day_means:
            self.per_day_means[day_of_week] = amount
        else:
            # simple EMA for day means
            self.per_day_means[day_of_week] = 0.8 * self.per_day_means[day_of_week] + 0.2 * amount

@dataclass
class TemporalProfile:
    typical_hours_histogram: Dict[int, int] = field(default_factory=dict)
    typical_days_histogram: Dict[int, int] = field(default_factory=dict)

    def update(self, hour: int, day: int):
        self.typical_hours_histogram[hour] = self.typical_hours_histogram.get(hour, 0) + 1
        self.typical_days_histogram[day] = self.typical_days_histogram.get(day, 0) + 1

@dataclass
class GeoProfile:
    known_locations: Set[str] = field(default_factory=set)
    home_location: str = ""
    typical_countries: Set[str] = field(default_factory=set)
    
    def update(self, location: str):
        self.known_locations.add(location)
        if not self.home_location:
            self.home_location = location

@dataclass
class DeviceProfile:
    known_devices: Set[str] = field(default_factory=set)
    primary_device: str = ""

    def update(self, device_id: str):
        self.known_devices.add(device_id)
        if not self.primary_device:
            self.primary_device = device_id

@dataclass
class MerchantBehaviorProfile:
    known_merchants: Set[str] = field(default_factory=set)
    known_categories: Set[str] = field(default_factory=set)
    category_distribution: Dict[str, int] = field(default_factory=dict)

    def update(self, merchant_id: str, category: str):
        self.known_merchants.add(merchant_id)
        self.known_categories.add(category)
        self.category_distribution[category] = self.category_distribution.get(category, 0) + 1

@dataclass
class BehaviorProfile:
    user_id: str
    transaction_count: int
    last_updated: Any
    spending: SpendingProfile
    temporal: TemporalProfile
    geo: GeoProfile
    device: DeviceProfile
    merchant: MerchantBehaviorProfile
