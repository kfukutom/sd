"""
01 - Subtype Polymorphism versus Ad Hoc Polymorphism
polymorphism.py (frame as tradeoff on axis)
"""

from abc import ABC, abstractmethod
from typing import Optional

# (a) Subtype Polymorphism
class PricingStrategy(ABC):
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    # an abstract method must be implemented by its subclasses
    def price(self, price: float) -> float: ...

class FlatPricing(PricingStrategy):
    def __init__(self, name: str, flat_rate: int):
        super().__init__(name)
        self.flat_rate = float(flat_rate)
    
    def price(self, price: Optional[float] = None) -> float:
        return self.flat_rate

class PercentagePricing(PricingStrategy):
    def __init__(self, name: str, percentage: float) -> None:
        super().__init__(name)
        self.percentage = percentage
    
    def price(self, price: float) -> float:
        return price * self.percentage

"""
Main tradeoff for subtype polymorphism:
- Easy to add new types of objects
- Hard to add new functions
"""

# (b) Ad Hoc Polymorphism
class PricingCalculator:
    def __init__(self):
        self.strategies = {}
    
    def register_strategy(self, name: str, strategy):
        self.strategies[name] = strategy
    
    def calculate(self, name: str, price: float) -> float:
        if name not in self.strategies:
            raise ValueError(f"Unknown strategy: {name}")
        return self.strategies[name].price(price)

"""
Main tradeoff for ad hoc polymorphism:
- Easy to add new functions
- Hard to add new types of objects
"""

def main():
    calculator = PricingCalculator()
    calculator.register_strategy("flat", FlatPricing("Flat", 10))
    calculator.register_strategy("percentage", PercentagePricing("Percentage", 0.1))
    print(calculator.calculate("flat", 100))
    print(calculator.calculate("percentage", 50))

if __name__ == "__main__":
    main()
