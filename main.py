from rental import Rental


print("Welcome to Rental Decision Helper!")

rental_one = Rental(
    name="Oak Apartments",
    monthly_rent=1800.00,
    monthly_utilities=150.00,
    monthly_parking_fee=50.00,
    bedrooms=2,
    bathrooms=1.0,
    square_feet=900,
    commute_minutes=20,
    pets_allowed=True,
    in_unit_laundry=False,
    community_gym=True,
    community_pool=False,
    covered_parking=True
)

print(rental_one.name)
print(f"Monthly rent: ${rental_one.monthly_rent:,.2f}")
print(f"Community gym: {rental_one.community_gym}")