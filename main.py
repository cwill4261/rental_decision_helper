from rental import Rental
import math
import json
from dataclasses import asdict
from pathlib import Path

SAVE_FILE = Path(__file__).with_name("rentals.json")

def get_number(prompt, number_type=float, minimum=0):
    while True:
        try:
            value = number_type(input(prompt))

            if not math.isfinite(value) or value < minimum:
                print(f"Enter a finite number that is {minimum} or greater.")
                continue

            return value
        except ValueError:
            print("Enter a valid number.")


def get_yes_no(prompt):
    while True:
        answer = input(prompt).strip().lower()

        if answer in ("yes", "y"):
            return True
        if answer in ("no", "n"):
            return False

        print("Enter yes or no.")


def get_required_text(prompt):
    while True:
        value = input(prompt).strip()

        if value:
            return value

        print("This field cannot be blank.")

def get_menu_choice(prompt, maximum):
    while True:
        choice = get_number(prompt, int)

        if choice <= maximum:
            return choice

        print(f"Enter a number from 0 to {maximum}.")


def edit_rental(rentals):
    if not rentals:
        print("There are no rentals to edit.")
        return

    print("\nChoose a rental to edit:")
    for number, rental in enumerate(rentals, start=1):
        print(f"{number}. {rental.name}")
    print("0. Cancel")

    choice = get_menu_choice("Rental number: ", len(rentals))

    if choice == 0:
        return

    rental = rentals[choice - 1]

    # Attribute name, display label, input type, minimum value
    fields = [
        ("name", "Property name", str, 0),
        ("monthly_rent", "Monthly rent", float, 0),
        ("monthly_utilities", "Monthly utilities", float, 0),
        ("monthly_parking_fee", "Monthly parking fee", float, 0),
        ("bedrooms", "Bedrooms", int, 0),
        ("bathrooms", "Bathrooms", float, 0),
        ("square_feet", "Square footage", int, 1),
        ("commute_minutes", "Commute time in minutes", int, 0),
        ("pets_allowed", "Pets allowed", bool, 0),
        ("in_unit_laundry", "In-unit laundry", bool, 0),
        ("community_gym", "Community gym", bool, 0),
        ("community_pool", "Community pool", bool, 0),
        ("covered_parking", "Covered parking", bool, 0)
    ]

    while True:
        print(f"\nEditing {rental.name}")

        for number, (attribute, label, data_type, minimum) in enumerate(
            fields, start=1
        ):
            current_value = getattr(rental, attribute)

            if data_type is bool:
                current_value = "Yes" if current_value else "No"

            print(f"{number}. {label}: {current_value}")

        print("0. Finish editing")
        choice = get_menu_choice("Field number: ", len(fields))

        if choice == 0:
            break

        attribute, label, data_type, minimum = fields[choice - 1]

        if data_type is str:
            new_value = get_required_text(f"{label}: ")
        elif data_type is bool:
            new_value = get_yes_no(f"{label}? (yes/no): ")
        else:
            new_value = get_number(
                f"{label}: ", data_type, minimum=minimum
            )

        setattr(rental, attribute, new_value)
        print(f"{label} updated.")


def save_rentals(rentals):
    data = [asdict(rental) for rental in rentals]

    try:
        temporary_file = SAVE_FILE.with_suffix(".tmp")
        temporary_file.write_text(
            json.dumps(data, indent=4),
            encoding="utf-8"
        )
        temporary_file.replace(SAVE_FILE)
        return True
    except OSError as error:
        print(f"Could not save rentals: {error}")
        return False


def load_rentals():
    if not SAVE_FILE.exists():
        return []

    try:
        data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))

        if not isinstance(data, list):
            raise ValueError("The saved data must be a list.")

        return [Rental(**details) for details in data]

    except (OSError, ValueError, TypeError) as error:
        print(f"Could not load saved rentals: {error}")
        print("Your saved file has not been changed.")
        return None


def view_rentals(rentals):
    if not rentals:
        print("\nNo rentals have been added yet.")
        return

    print("\nRental Comparison")

    for number, rental in enumerate(rentals, start=1):
        print(f"\n{number}. {rental.name}")
        print(
            f"   {rental.bedrooms} bedrooms | "
            f"{rental.bathrooms:g} bathrooms | "
            f"{rental.square_feet:,} sq ft | "
            f"{rental.commute_minutes} min commute"
        )
        print(
            f"   Rent: ${rental.monthly_rent:,.2f} | "
            f"Utilities: ${rental.monthly_utilities:,.2f} | "
            f"Parking: ${rental.monthly_parking_fee:,.2f}"
        )
        print(
            f"   Estimated monthly total: "
            f"${rental.total_monthly_cost():,.2f}"
        )
        print(
            f"   Pets allowed: {'Yes' if rental.pets_allowed else 'No'} | "
            f"In-unit laundry: {'Yes' if rental.in_unit_laundry else 'No'}"
        )
        print(
            f"   Gym: {'Yes' if rental.community_gym else 'No'} | "
            f"Pool: {'Yes' if rental.community_pool else 'No'} | "
            f"Covered parking: {'Yes' if rental.covered_parking else 'No'}"
        )


def enter_rental():
    print("\nEnter rental details")

    name = get_required_text("Property name: ")
    monthly_rent = get_number("Monthly rent: ")
    monthly_utilities = get_number("Estimated monthly utilities: ")
    monthly_parking_fee = get_number("Monthly parking fee: ")
    bedrooms = get_number("Bedrooms: ", int)
    bathrooms = get_number("Bathrooms: ")
    square_feet = get_number("Square footage: ", int, minimum=1)
    commute_minutes = get_number("Commute time in minutes: ", int)

    pets_allowed = get_yes_no("Pets allowed? (yes/no): ")
    in_unit_laundry = get_yes_no("In-unit laundry? (yes/no): ")
    community_gym = get_yes_no("Community gym? (yes/no): ")
    community_pool = get_yes_no("Community pool? (yes/no): ")
    covered_parking = get_yes_no("Covered parking? (yes/no): ")

    return Rental(
        name=name,
        monthly_rent=monthly_rent,
        monthly_utilities=monthly_utilities,
        monthly_parking_fee=monthly_parking_fee,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        square_feet=square_feet,
        commute_minutes=commute_minutes,
        pets_allowed=pets_allowed,
        in_unit_laundry=in_unit_laundry,
        community_gym=community_gym,
        community_pool=community_pool,
        covered_parking=covered_parking
    )

def main():
    print("Welcome to Rental Decision Helper!")

    rentals = load_rentals()

    # Stop if loading failed so existing data is not overwritten.
    if rentals is None:
        return

    print(f"Loaded {len(rentals)} rental(s).")

    while True:
        print("\nMain Menu")
        print("1. View and compare rentals")
        print("2. Add a rental")
        print("3. Edit a rental")
        print("0. Exit")

        choice = get_menu_choice("Choose an option: ", 3)

        if choice == 1:
            view_rentals(rentals)

        elif choice == 2:
            rental = enter_rental()
            rentals.append(rental)

            if save_rentals(rentals):
                print("Rental added and saved.")

        elif choice == 3:
            edit_rental(rentals)

            if save_rentals(rentals):
                print("Rental list saved.")


            print("\nMonthly Cost Comparison")

            for rental in rentals:
                print(
                    f"{rental.name}: "
                    f"${rental.total_monthly_cost():,.2f}"
                )

        elif choice == 0:
            if save_rentals(rentals):
                print("Rentals saved. Goodbye!")
                break

            print("Your rentals are still available in this session.")


if __name__ == "__main__":
    main()