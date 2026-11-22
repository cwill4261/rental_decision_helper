from dataclasses import dataclass


@dataclass
class Rental:
    name: str
    monthly_rent: float
    monthly_utilities: float
    monthly_parking_fee: float
    bedrooms: int
    bathrooms: float
    square_feet: int
    commute_minutes: int
    pets_allowed: bool
    in_unit_laundry: bool
    community_gym: bool
    community_pool: bool
    covered_parking: bool

    def total_monthly_cost(self):
        return (
            self.monthly_rent
            + self.monthly_utilities
            + self.monthly_parking_fee
        )