from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User

class Artisan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    specialty = models.CharField(max_length=200)
    experience_years = models.IntegerField(default=0)
    profile_image = models.ImageField(upload_to='artisans/', blank=True, null=True)
    join_date = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # ← ADD THIS
    first_name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def total_sales(self):
        return sum(sale.total_price for sale in self.sales.all())

    @property
    def profit(self):
        material_cost = sum(m.quantity * m.cost_per_unit for m in self.materials.all())
        return self.total_sales - material_cost

class Material(models.Model):
    MATERIAL_TYPES = [
        ('wool', 'Laine'),
        ('cotton', 'Coton'),
        ('silk', 'Soie'),
        ('thread', 'Fil'),
	('Argile','Argile'),
	('Silver','Argent'),
    ]
    UNITS = [
        ('kg', 'Kilogramme'),
        ('g', 'Gramme'),
        ('m', 'Mètre'),
        ('piece', 'Pièce'),
    ]
    
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name='materials')
    material_type = models.CharField(max_length=50, choices=MATERIAL_TYPES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    unit = models.CharField(max_length=20, choices=UNITS, default='kg')
    purchase_date = models.DateField()
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.artisan.full_name} - {self.get_material_type_display()}"

    @property
    def total_cost(self):
        return self.quantity * self.cost_per_unit

class Sale(models.Model):
    artisan = models.ForeignKey(Artisan, on_delete=models.CASCADE, related_name='sales')
    product_name = models.CharField(max_length=200)
    quantity_sold = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    sale_date = models.DateField()
    customer_name = models.CharField(max_length=200, blank=True, null=True)  # ← AJOUTER CETTE LIGNE

    def __str__(self):
        return f"{self.artisan.full_name} - {self.product_name}"

    @property
    def total_price(self):
        return self.quantity_sold * self.unit_price

    class Meta:
        ordering = ['-sale_date']