import csv
from django.core.management.base import BaseCommand
from RadioWatch.models import Product

class Command(BaseCommand):
    help = 'Import products from a CSV file'

    def handle(self, *args, **kwargs):
        csv_file_path = 'data/Watch_Products.csv'  # Adjust the path if needed

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                # Track success and errors
                success_count = 0
                error_count = 0

                for row in reader:
                    try:
                        Product.objects.create(
                            product_id=row['product_id'],
                            product_name=row['product_name'],
                            description=row['description'],
                            price=float(row['price']),  # Ensure price is a float
                            category=row['category'],
                            brand_name=row['brand_name'],
                            type=row['type'],
                            rating=float(row['rating']),  # Ensure rating is a float
                        )
                        success_count += 1
                    except Exception as e:
                        self.stderr.write(f"Error adding product: {row['product_name']}. Error: {e}")
                        error_count += 1

            self.stdout.write(self.style.SUCCESS(f'Successfully imported {success_count} products'))
            if error_count > 0:
                self.stdout.write(self.style.WARNING(f'Failed to import {error_count} products'))
        
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"File not found: {csv_file_path}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"An unexpected error occurred: {e}"))
