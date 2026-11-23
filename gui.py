import tkinter as tk
from tkinter import ttk, messagebox
from main import SAVE_FILE
import math
from main import (
    load_rentals,
    save_rentals,
    check_requirements,
    rank_rentals
)
from rental import Rental

class RentalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Rental Decision Helper")
        self.root.geometry("1000x450")
        print("Loading rentals from:", SAVE_FILE)
        print("Saved file exists:", SAVE_FILE.exists())

        self.rentals = load_rentals()

        if self.rentals is None:
            messagebox.showerror(
                "Loading Error",
                "Saved rentals could not be loaded."
            )
            self.root.destroy()
            return

        ttk.Label(
            root,
            text="Your Rental Shortlist",
            font=("Arial", 18, "bold")
        ).pack(pady=15)

        frame = ttk.Frame(root)
        frame.pack(fill="both", expand=True, padx=15, pady=5)

        columns = (
            "name", "monthly_cost", "bedrooms",
            "bathrooms", "square_feet", "commute"
        )

        self.table = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        headings = {
            "name": "Property",
            "monthly_cost": "Monthly Total",
            "bedrooms": "Bedrooms",
            "bathrooms": "Bathrooms",
            "square_feet": "Square Feet",
            "commute": "Commute (min)"
        }

        for column, heading in headings.items():
            self.table.heading(column, text=heading)
            self.table.column(column, width=130, anchor="center")

        self.table.column("name", width=220, anchor="w")

        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)

        self.status = ttk.Label(root)
        self.status.pack(pady=10)
        self.requirements = None
        self.weights = None

        toolbar = ttk.Frame(root, padding=10)
        toolbar.pack(side="bottom", fill="x")

        buttons = [
            ("Add Rental", self.add_rental),
            ("Edit Selected", self.edit_selected_rental),
            ("Delete Selected", self.delete_selected_rental),
            ("Set Requirements", self.set_requirements),
            ("Check Requirements", self.show_requirements),
            ("Set Weights", self.set_weights),
            ("Rank Rentals", self.show_rankings)
        ]

        for label, action in buttons:
            ttk.Button(
                toolbar,
                text=label,
                command=action
            ).pack(side="left", padx=4)

        self.refresh_table()

    def refresh_table(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for index, rental in enumerate(self.rentals):
            self.table.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    rental.name,
                    f"${rental.total_monthly_cost():,.2f}",
                    rental.bedrooms,
                    f"{rental.bathrooms:g}",
                    f"{rental.square_feet:,}",
                    rental.commute_minutes
                )
            )
        self.status.config(
        text=f"{len(self.rentals)} rental(s) in your shortlist"
    )

    def edit_selected_rental(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showinfo(
                "Select a Rental",
                "Select a rental in the table first.",
                parent=self.root
            )
            return

        index = int(selected[0])
        self.add_rental(index)


    def add_rental(self, index=None):
        existing = self.rentals[index] if index is not None else None

        window = tk.Toplevel(self.root)
        window.title("Edit Rental" if existing is not None else "Add Rental")
        window.transient(self.root)
        window.grab_set()

        form = ttk.Frame(window, padding=15)
        form.pack(fill="both", expand=True)

        fields = [
            ("name", "Property name", str, 0),
            ("monthly_rent", "Monthly rent", float, 0),
            ("monthly_utilities", "Monthly utilities", float, 0),
            ("monthly_parking_fee", "Monthly parking fee", float, 0),
            ("bedrooms", "Bedrooms", int, 0),
            ("bathrooms", "Bathrooms", float, 0),
            ("square_feet", "Square footage", int, 1),
            ("commute_minutes", "Commute minutes", int, 0)
        ]

        entries = {}

        for row, (attribute, label, data_type, minimum) in enumerate(fields):
            ttk.Label(form, text=label).grid(
                row=row, column=0, sticky="w", pady=4
            )

            entry = ttk.Entry(form, width=30)
            entry.grid(row=row, column=1, pady=4)
            entries[attribute] = entry
            if existing is not None:
                entry.insert(0, str(getattr(existing, attribute)))


        amenities = [
            ("pets_allowed", "Pets allowed"),
            ("in_unit_laundry", "In-unit laundry"),
            ("community_gym", "Community gym"),
            ("community_pool", "Community pool"),
            ("covered_parking", "Covered parking")
        ]

        amenity_values = {}

        for row, (attribute, label) in enumerate(
            amenities, start=len(fields)
        ):
            variable = tk.BooleanVar(
                master=window,
                value=(
                    getattr(existing, attribute)
                    if existing is not None
                    else False
                )
            )
            amenity_values[attribute] = variable

            ttk.Checkbutton(
                form,
                text=label,
                variable=variable
            ).grid(row=row, column=0, columnspan=2, sticky="w", pady=3)

        def save():
            details = {}

            for attribute, label, data_type, minimum in fields:
                text = entries[attribute].get().strip()

                if data_type is str:
                    if not text:
                        messagebox.showerror(
                            "Invalid Entry",
                            f"{label} cannot be blank.",
                            parent=window
                        )
                        entries[attribute].focus_set()
                        return

                    details[attribute] = text
                    continue

                try:
                    value = data_type(text)

                    if not math.isfinite(value) or value < minimum:
                        raise ValueError

                except ValueError:
                    number_description = (
                        "a whole number" if data_type is int else "a number"
                    )
                    messagebox.showerror(
                        "Invalid Entry",
                        f"{label} must be {number_description} "
                        f"that is {minimum} or greater. "
                        "Do not include commas or dollar signs.",
                        parent=window
                    )
                    entries[attribute].focus_set()
                    return

                details[attribute] = value

            for attribute, variable in amenity_values.items():
                details[attribute] = variable.get()

            new_rental = Rental(**details)
            updated_rentals = self.rentals.copy()

            if index is None:
                updated_rentals.append(new_rental)
            else:
                updated_rentals[index] = new_rental

            if not save_rentals(updated_rentals):
                messagebox.showerror(
                    "Save Error",
                    "The rental could not be saved. "
                    "Your entries are still available in this form.",
                    parent=window
                )
                return

            self.rentals = updated_rentals
            self.refresh_table()
            window.destroy()

        buttons = ttk.Frame(form)
        buttons.grid(
            row=len(fields) + len(amenities),
            column=0,
            columnspan=2,
            pady=(15, 0)
        )

        ttk.Button(
            buttons, text="Save Rental", command=save
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons, text="Cancel", command=window.destroy
        ).pack(side="left", padx=5)

        entries["name"].focus_set()


        self.status.config(
            text=f"{len(self.rentals)} rental(s) in your shortlist"
        )


    def delete_selected_rental(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showinfo(
                "Select a Rental",
                "Select a rental in the table first.",
                parent=self.root
            )
            return

        index = int(selected[0])
        rental = self.rentals[index]

        confirmed = messagebox.askyesno(
            "Delete Rental",
            f"Delete {rental.name} from your shortlist?",
            parent=self.root
        )

        if not confirmed:
            return

        updated_rentals = self.rentals.copy()
        del updated_rentals[index]

        if not save_rentals(updated_rentals):
            messagebox.showerror(
                "Save Error",
                "The rental could not be deleted. Your list is unchanged.",
                parent=self.root
            )
            return

        self.rentals = updated_rentals
        self.refresh_table()


    def set_requirements(self):
        window = tk.Toplevel(self.root)
        window.title("Rental Requirements")
        window.transient(self.root)
        window.grab_set()

        form = ttk.Frame(window, padding=15)
        form.pack()

        ttk.Label(
            form,
            text="Leave numeric fields blank for no limit."
        ).grid(row=0, column=0, columnspan=2, pady=10)

        fields = [
            ("maximum_cost", "Maximum monthly total", float, 0),
            ("minimum_bedrooms", "Minimum bedrooms", int, 0),
            ("minimum_bathrooms", "Minimum bathrooms", float, 0),
            ("minimum_square_feet", "Minimum square footage", int, 1),
            ("maximum_commute", "Maximum commute minutes", int, 0)
        ]

        entries = {}

        for row, (key, label, data_type, minimum) in enumerate(
            fields, start=1
        ):
            ttk.Label(form, text=label).grid(
                row=row, column=0, sticky="w", pady=4
            )

            entry = ttk.Entry(form)
            entry.grid(row=row, column=1, pady=4)
            entries[key] = entry

            if self.requirements is not None:
                current = self.requirements[key]
                if current is not None:
                    entry.insert(0, str(current))

        amenities = [
            ("pets_allowed", "Require pets allowed"),
            ("in_unit_laundry", "Require in-unit laundry"),
            ("community_gym", "Require community gym"),
            ("community_pool", "Require community pool"),
            ("covered_parking", "Require covered parking")
        ]

        variables = {}

        for row, (key, label) in enumerate(amenities, start=6):
            variable = tk.BooleanVar(
                master=window,
                value=(
                    self.requirements[key]
                    if self.requirements is not None
                    else False
                )
            )
            variables[key] = variable

            ttk.Checkbutton(
                form, text=label, variable=variable
            ).grid(
                row=row, column=0, columnspan=2,
                sticky="w", pady=3
            )

        def apply():
            requirements = {}

            for key, label, data_type, minimum in fields:
                text = entries[key].get().strip()

                if not text:
                    requirements[key] = None
                    continue

                try:
                    value = data_type(text)

                    if not math.isfinite(value) or value < minimum:
                        raise ValueError

                except ValueError:
                    number_type = (
                        "a whole number" if data_type is int
                        else "a number"
                    )
                    messagebox.showerror(
                        "Invalid Requirement",
                        f"{label} must be {number_type} "
                        f"that is {minimum} or greater, or blank.",
                        parent=window
                    )
                    entries[key].focus_set()
                    return

                requirements[key] = value

            for key, variable in variables.items():
                requirements[key] = variable.get()

            self.requirements = requirements
            window.destroy()

        buttons = ttk.Frame(form)
        buttons.grid(row=11, column=0, columnspan=2, pady=15)

        ttk.Button(
            buttons, text="Apply", command=apply
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons, text="Cancel", command=window.destroy
        ).pack(side="left", padx=5)

    def show_requirements(self):
        if self.requirements is None:
            messagebox.showinfo(
                "Set Requirements",
                "Set your requirements first.",
                parent=self.root
            )
            return

        if not self.rentals:
            messagebox.showinfo(
                "No Rentals",
                "Add a rental first.",
                parent=self.root
            )
            return

        results = []

        for rental in self.rentals:
            failures = check_requirements(
                rental, self.requirements
            )

            if failures:
                result = "; ".join(failures)
            else:
                result = "Meets all requirements"

            results.append(f"{rental.name}\n{result}")

        messagebox.showinfo(
            "Requirement Results",
            "\n\n".join(results),
            parent=self.root
        )


    def show_rankings(self):
        if not self.rentals:
            messagebox.showinfo(
                "No Rentals", "Add a rental first.", parent=self.root
            )
            return

        if self.requirements is None or self.weights is None:
            messagebox.showinfo(
                "Set Your Preferences",
                "Set requirements and preference weights first.",
                parent=self.root
            )
            return

        qualifying = []
        excluded = []

        for rental in self.rentals:
            failures = check_requirements(
                rental, self.requirements
            )

            if failures:
                excluded.append((rental, failures))
            else:
                qualifying.append(rental)

        ranked = rank_rentals(qualifying, self.weights)

        window = tk.Toplevel(self.root)
        window.title("Ranked Rentals")
        window.geometry("750x550")

        ttk.Label(
            window,
            text="Ranked Rental Shortlist",
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        ttk.Label(
            window,
            text=(
                "Scores are relative to qualifying rentals. "
                "Adding properties can change scores."
            ),
            wraplength=700
        ).pack(padx=15, pady=5)

        frame = ttk.Frame(window)
        frame.pack(fill="both", expand=True, padx=15, pady=10)

        text = tk.Text(frame, wrap="word", padx=10, pady=10)
        scrollbar = ttk.Scrollbar(
            frame, orient="vertical", command=text.yview
        )
        text.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        text.pack(side="left", fill="both", expand=True)

        if not ranked:
            text.insert("end", "No rentals meet all requirements.\n")

        previous_score = None
        rank = 0

        for position, (rental, score, details) in enumerate(
            ranked, start=1
        ):
            displayed_score = round(score, 1)

            if displayed_score != previous_score:
                rank = position

            previous_score = displayed_score

            text.insert(
                "end",
                f"{rank}. {rental.name} — {score:.1f}/100\n"
                f"Monthly total: "
                f"${rental.total_monthly_cost():,.2f}\n"
            )

            for detail in details:
                text.insert("end", f"  {detail}\n")

            text.insert("end", "\n")

        if excluded:
            text.insert("end", "EXCLUDED RENTALS\n\n")

            for rental, failures in excluded:
                text.insert(
                    "end",
                    f"{rental.name}\n"
                    f"  {'; '.join(failures)}\n\n"
                )

        text.configure(state="disabled")

        ttk.Button(
            window, text="Close", command=window.destroy
        ).pack(pady=10)


    def set_weights(self):
        window = tk.Toplevel(self.root)
        window.title("Preference Weights")
        window.transient(self.root)
        window.grab_set()

        form = ttk.Frame(window, padding=15)
        form.pack()

        ttk.Label(
            form,
            text="0 = ignore | 1 = slightly important | 5 = very important"
        ).grid(row=0, column=0, columnspan=2, pady=10)

        fields = [
            ("monthly_cost", "Lower total monthly cost"),
            ("bedrooms", "More bedrooms"),
            ("bathrooms", "More bathrooms"),
            ("square_feet", "More square footage"),
            ("commute_minutes", "Shorter commute"),
            ("pets_allowed", "Pets allowed"),
            ("in_unit_laundry", "In-unit laundry"),
            ("community_gym", "Community gym"),
            ("community_pool", "Community pool"),
            ("covered_parking", "Covered parking")
        ]

        entries = {}

        for row, (key, label) in enumerate(fields, start=1):
            ttk.Label(form, text=label).grid(
                row=row, column=0, sticky="w", padx=5, pady=4
            )

            entry = ttk.Spinbox(
                form, from_=0, to=5, increment=1, width=5
            )
            entry.grid(row=row, column=1, padx=5, pady=4)

            current = self.weights[key] if self.weights is not None else 0
            entry.set(str(current))
            entries[key] = entry

        def apply():
            weights = {}

            for key, label in fields:
                try:
                    value = int(entries[key].get())

                    if not 0 <= value <= 5:
                        raise ValueError

                except ValueError:
                    messagebox.showerror(
                        "Invalid Weight",
                        f"{label}: enter a whole number from 0 to 5.",
                        parent=window
                    )
                    entries[key].focus_set()
                    return

                weights[key] = value

            if sum(weights.values()) == 0:
                messagebox.showerror(
                    "Choose a Preference",
                    "At least one weight must be greater than zero.",
                    parent=window
                )
                return

            self.weights = weights
            window.destroy()

        buttons = ttk.Frame(form)
        buttons.grid(
            row=len(fields) + 1,
            column=0,
            columnspan=2,
            pady=15
        )

        ttk.Button(
            buttons, text="Apply", command=apply
        ).pack(side="left", padx=5)

        ttk.Button(
            buttons, text="Cancel", command=window.destroy
        ).pack(side="left", padx=5)

def main():
    root = tk.Tk()
    RentalApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()