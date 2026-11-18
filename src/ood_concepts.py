"""
002 - OOD Concept Review File
"""

from datetime import datetime
import threading
# pyrefly: ignore[missing-import]
from __futures__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto

class BedType(Enum):
    GENRERAL = auto()
    ICU = auto()
    PEDIATRIC = auto()

class Currency(Enum):
    USD = "USD"
    AUD = "AUD"
    JPY = "JPY"

@dataclass(frozen=True)
class Money:
    amount: float
    currency: Currency = "USD"

    def init(self) -> None:
        if self.amount < 0:
            raise ValueError("Value can't be negative.")

    def add(self, other: Money) -> Money:
        if not isinstance(other, Money):
            return NotImplemented
        if other.currency != self.currency:
            raise ValueError(f"Currency mismatch: {self.currency} vs. {other.currency}")
        return Money(self.amount + other.amount, self.currency)

"""
BELOW CONTAINS A LIGHT EXAMPLE OF DESIGING A HOSPITAL-PATIENT MATCHING SYSTEM
(NEVER ASSUME): don't ever assume a framework, always ask followup questions.
- Who is this product for?
- Does an existing framework already exist?
- Concerns for extendability (subtype, adhoc, parametric design patterns)
- What is the product communicating
(Understand the core of the problem, then move onto explaining the framework)
"""

# 1. Enum, a fixed set of states (example below!)
# from enum import Enum
class BedStatus(Enum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    CLEANING = "cleaning"

# 2. Dataclasses
# from dataclasses import dataclass
@dataclass
class Patient:
    patient_id: str
    name: str
    acuity: int # document how this system is laid out
    needs_icu: bool

@dataclass
class Bed:
    bed_id: str
    ward: str
    floor: int
    is_icu: bool
    status: BedStatus = BedStatus.AVAILABLE

@dataclass
class Admission:
    patient: Patient
    bed: Bed
    admitted_at: datetime
    discharged_at: datetime | None = None

# 3. Abstract class + strategy pattern
class AssignmentStrategy(ABC):
    @abstractmethod
    def choose_bed(self, patient: Patient, open_beds: list[Bed]) -> Bed | None:
        pass

class FirstAvailableStrategy(AssignmentStrategy):
    def choose_bed(self, patient, open_beds):
        return open_beds[0] if open_beds else None

class LowestFloorStrategy(AssignmentStrategy):
    def choose_bed(self, patient, open_beds):
        return min(open_beds, key=lambda x: x.floor) if open_beds else None
    
# factory to maintain strategies
STRATEGIES = {
    "first_available": FirstAvailableStrategy,
    "lowest_floor": LowestFloorStrategy,
}

# 4. Notiifer interface
class Notifier(ABC):
    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        pass

class PagerNotifier(Notifier):
    def send(self, recipient, message):
        print(f"[page {recipient}] {message}")

# 5. Service: dependencies are injected
class NoBedAvailableError(Exception):
    pass

class AdmissionService:
    def __init__(self, beds: list[Bed], strategy: AssignmentStrategy, notifier: Notifier):
        self.beds = beds
        self.strategy = strategy
        self.notifier = notifier
        self.active_admissions = {}
        self.lock = threading.lock
    
    def admit(self, patient: Patient) -> Admission:
        with self.lock:
            open_beds = [
                bed for bed in self.beds
                if bed.status == BedStatus.AVAILABLE and bed.is_icu == patient.needs_icu
            ]
            bed = self.strategy.choose_bed(patient, open_beds)
            if bed is None:
                raise NoBedAvailableError(f"No bed is available for {patient.patient_id}!")
            bed.status = BedStatus.OCCUPIED
            admission = Admission(patient, bed, datetime.now())
            self.active_admissions[patient.patient_id] = admission
        self.notifier.send(bed.ward, f"{patient.name} assigned to bed {bed.bed_id}")
        return admission
    
    def evict(self, patient_id: str) -> Admission:
        with self.lock:
            admission = self.active_admission.pop(patient_id)
            admission.discharged_at = datetime.now()
            admission.bed_status = BedStatus.CLEANING
        return admission

"""
Most import part of this process is to walk through the code now.
"""

if __name__ == "__main__":
    beds = [
        Bed("B1", "East", floor=3),
        Bed("B2", "West", floor=1),
        Bed("ICU1", "ICU", floor=4, is_icu=True)
    ]
    notifier = PagerNotifier()
    service = AdmissionService(beds, STRATEGIES["lowest_floor"](), notifier)
    ada_admission = service.admit(Patient("P1", "Ada", acuity=2))
    assert ada_admission.bed.bed_id == "B2"