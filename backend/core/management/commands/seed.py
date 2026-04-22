from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from buyers.models import Buyer
from ingredients.models import Ingredient
from orders.models import Order, OrderItem, OrderStatus
from products.models import Product, ProductIngredient
from suppliers.models import Supplier


SUPPLIERS = [
    {
        "name": "Nordic Grains Co.",
        "description": "Specialist grain supplier sourcing from Scandinavian farms. Known for high-quality oats, rye, and ancient grains.",
        "ingredients": [
            {"name": "Organic Rolled Oats", "unit": "kg", "price_per_unit": "1.85", "description": "Whole grain rolled oats, certified organic"},
            {"name": "Dark Rye Flour", "unit": "kg", "price_per_unit": "2.10", "description": "Stone-ground dark rye, rich flavour"},
            {"name": "Spelt Flour", "unit": "kg", "price_per_unit": "3.40", "description": "Ancient grain flour, nutty and nutritious"},
            {"name": "Barley Flakes", "unit": "kg", "price_per_unit": "1.65", "description": "Lightly toasted barley flakes"},
        ],
    },
    {
        "name": "Alpine Dairy Collective",
        "description": "Premium dairy ingredients sourced from Alpine mountain farms. Specialists in butter, cream, and cultured products.",
        "ingredients": [
            {"name": "Unsalted Butter", "unit": "kg", "price_per_unit": "7.50", "description": "84% fat content, European style"},
            {"name": "Double Cream", "unit": "litre", "price_per_unit": "4.20", "description": "48% fat, pasteurised"},
            {"name": "Full-Fat Milk Powder", "unit": "kg", "price_per_unit": "9.80", "description": "Spray-dried, instant dissolving"},
            {"name": "Cultured Buttermilk Powder", "unit": "kg", "price_per_unit": "11.20", "description": "Adds tang and tenderness to baked goods"},
            {"name": "Whey Protein Concentrate", "unit": "kg", "price_per_unit": "14.50", "description": "80% protein, neutral flavour"},
        ],
    },
    {
        "name": "Tropicana Botanicals",
        "description": "Importer and distributor of tropical botanicals, spices, and natural flavourings sourced directly from smallholder farms.",
        "ingredients": [
            {"name": "Vanilla Extract", "unit": "litre", "price_per_unit": "85.00", "description": "Pure Madagascar vanilla, 2-fold concentration"},
            {"name": "Cacao Powder", "unit": "kg", "price_per_unit": "12.50", "description": "Dutch-processed, 22-24% fat"},
            {"name": "Coconut Sugar", "unit": "kg", "price_per_unit": "4.80", "description": "Unrefined, low GI sweetener"},
            {"name": "Desiccated Coconut", "unit": "kg", "price_per_unit": "3.20", "description": "Fine grade, unsweetened"},
        ],
    },
    {
        "name": "BioSeed Oils",
        "description": "Cold-pressed and refined plant oils for food manufacturing. Certified non-GMO, traceable supply chain.",
        "ingredients": [
            {"name": "Sunflower Oil", "unit": "litre", "price_per_unit": "2.10", "description": "High-oleic, refined, neutral flavour"},
            {"name": "Cold-Pressed Rapeseed Oil", "unit": "litre", "price_per_unit": "3.80", "description": "Unrefined, nutty flavour, high omega-3"},
            {"name": "Coconut Oil", "unit": "kg", "price_per_unit": "5.60", "description": "Organic, virgin, unrefined"},
        ],
    },
]

DEMO_USER = {"username": "demo", "password": "demo1234", "email": "demo@opply.com"}
DEMO_COMPANY = "Demo Buying Co."


class Command(BaseCommand):
    help = "Seed the database with demo data (idempotent)"

    def handle(self, *args, **kwargs) -> None:
        self.stdout.write("Seeding database...")

        # --- Buyer ---
        user, created = User.objects.get_or_create(
            username=DEMO_USER["username"],
            defaults={"email": DEMO_USER["email"], "is_staff": True, "is_superuser": True},
        )
        if created or not user.check_password(DEMO_USER["password"]):
            user.set_password(DEMO_USER["password"])
            user.save()

        buyer, _ = Buyer.objects.get_or_create(user=user, defaults={"company_name": DEMO_COMPANY})

        # --- Suppliers & Ingredients ---
        ingredient_pool: list[Ingredient] = []
        for supplier_data in SUPPLIERS:
            supplier, _ = Supplier.objects.get_or_create(
                name=supplier_data["name"],
                defaults={"description": supplier_data["description"]},
            )
            for ing_data in supplier_data["ingredients"]:
                ingredient, _ = Ingredient.objects.get_or_create(
                    supplier=supplier,
                    name=ing_data["name"],
                    defaults={
                        "description": ing_data["description"],
                        "unit": ing_data["unit"],
                        "price_per_unit": ing_data["price_per_unit"],
                    },
                )
                ingredient_pool.append(ingredient)

        # --- Orders ---
        # Only create seed orders if none exist for this buyer
        if not Order.objects.filter(buyer=buyer).exists():
            self._create_order(buyer, [
                (ingredient_pool[0], 50),   # Rolled Oats 50kg
                (ingredient_pool[4], 10),   # Butter 10kg
            ])

            order_confirmed = self._create_order(buyer, [
                (ingredient_pool[8], 2),    # Whey Protein Concentrate 2kg
                (ingredient_pool[9], 20),   # Vanilla Extract 20L
                (ingredient_pool[2], 15),   # Spelt Flour 15kg
            ])
            order_confirmed.transition_to(OrderStatus.CONFIRMED)

            order_delivered = self._create_order(buyer, [
                (ingredient_pool[12], 30),  # Desiccated Coconut 30kg
                (ingredient_pool[5], 10),   # Double Cream 10L
            ])
            order_delivered.transition_to(OrderStatus.CONFIRMED)
            order_delivered.transition_to(OrderStatus.PROCESSING)
            order_delivered.transition_to(OrderStatus.SHIPPED)
            order_delivered.transition_to(OrderStatus.DELIVERED)

        # --- Products ---
        # ingredient_pool indices:
        #  0  Organic Rolled Oats       4  Unsalted Butter          9  Vanilla Extract
        #  1  Dark Rye Flour            5  Double Cream            10  Cacao Powder
        #  2  Spelt Flour               6  Full-Fat Milk Powder    11  Coconut Sugar
        #  3  Barley Flakes             7  Cultured Buttermilk Pwd 12  Desiccated Coconut
        #                               8  Whey Protein Concentrate 13  Sunflower Oil
        #                                                           14  Cold-Pressed Rapeseed Oil
        #                                                           15  Coconut Oil
        if not Product.objects.filter(buyer=buyer).exists():
            self._create_product(buyer,
                name="Oat Milk",
                description="Plant-based milk alternative made from whole grain oats.",
                ingredients=[
                    (ingredient_pool[0], "0.800"),   # Rolled Oats
                    (ingredient_pool[13], "0.050"),  # Sunflower Oil
                ],
            )
            self._create_product(buyer,
                name="Granola",
                description="Toasted oat and coconut granola, lightly sweetened.",
                ingredients=[
                    (ingredient_pool[0], "0.500"),   # Rolled Oats
                    (ingredient_pool[12], "0.150"),  # Desiccated Coconut
                    (ingredient_pool[11], "0.100"),  # Coconut Sugar
                    (ingredient_pool[15], "0.080"),  # Coconut Oil
                ],
            )
            self._create_product(buyer,
                name="Chocolate Protein Bar",
                description="High-protein snack bar with cacao and vanilla.",
                ingredients=[
                    (ingredient_pool[8], "0.300"),   # Whey Protein Concentrate
                    (ingredient_pool[10], "0.150"),  # Cacao Powder
                    (ingredient_pool[11], "0.100"),  # Coconut Sugar
                    (ingredient_pool[12], "0.100"),  # Desiccated Coconut
                    (ingredient_pool[9], "0.005"),   # Vanilla Extract
                ],
            )
            self._create_product(buyer,
                name="Spelt & Rye Loaf",
                description="Dense, wholesome sourdough-style loaf using ancient grains.",
                ingredients=[
                    (ingredient_pool[2], "0.300"),   # Spelt Flour
                    (ingredient_pool[1], "0.200"),   # Dark Rye Flour
                    (ingredient_pool[3], "0.050"),   # Barley Flakes
                ],
            )
            self._create_product(buyer,
                name="Vanilla Butter Cake",
                description="Classic vanilla sponge made with Alpine butter and spelt flour.",
                ingredients=[
                    (ingredient_pool[2], "0.250"),   # Spelt Flour
                    (ingredient_pool[4], "0.150"),   # Unsalted Butter
                    (ingredient_pool[11], "0.120"),  # Coconut Sugar
                    (ingredient_pool[6], "0.050"),   # Full-Fat Milk Powder
                    (ingredient_pool[9], "0.010"),   # Vanilla Extract
                ],
            )

        self.stdout.write(self.style.SUCCESS("Seed complete."))

    def _create_product(
        self,
        buyer: Buyer,
        name: str,
        description: str,
        ingredients: list[tuple[Ingredient, str]],
    ) -> Product:
        product = Product.objects.create(buyer=buyer, name=name, description=description)
        for ingredient, quantity in ingredients:
            ProductIngredient.objects.create(
                product=product,
                ingredient=ingredient,
                quantity=quantity,
            )
        return product

    def _create_order(
        self,
        buyer: Buyer,
        items: list[tuple[Ingredient, int]],
    ) -> Order:
        order = Order.objects.create(buyer=buyer)
        for ingredient, quantity in items:
            OrderItem.objects.create(
                order=order,
                ingredient=ingredient,
                quantity=quantity,
                unit_price=ingredient.price_per_unit,
            )
        return order
