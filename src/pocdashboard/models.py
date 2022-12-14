# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Country(models.Model):
    # country_id = models.AutoField(primary_key=True)
    country_name = models.CharField(primary_key=True, max_length=50)
    zone_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:

        db_table = 'country'


class Detailfacture(models.Model):
    stock_code = models.ForeignKey('Product', models.DO_NOTHING, db_column='stock_code', blank=True, null=True)
    invoice_no = models.ForeignKey('Invoice', models.DO_NOTHING, db_column='invoice_no', blank=True, null=True)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    detailfacture_id = models.AutoField(primary_key=True)

    class Meta:
        unique_together = ('stock_code', 'invoice_no')
        db_table = 'detailfacture'


class Invoice(models.Model):
    invoice_no = models.CharField(primary_key=True, max_length=6)
    invoice_date = models.CharField(max_length=20, blank=True, null=True)
    country_name = models.ForeignKey(Country, models.DO_NOTHING, db_column='country_name')
    customer_id = models.CharField(max_length=5, blank=True, null=True)

    class Meta:

        db_table = 'invoice'


class Product(models.Model):
    stock_code = models.CharField(primary_key=True, max_length=50)
    description = models.CharField(max_length=80, blank=True, null=True)

    class Meta:

        db_table = 'product'

# ======================================= TEMPORARY TABLE ======================================= 

class tempCountry(models.Model):
    # country_id = models.AutoField(primary_key=True)
    country_name = models.CharField(primary_key=True, max_length=50)
    zone_name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:

        db_table = 'tempcountry'


class tempDetailfacture(models.Model):
    stock_code = models.CharField(max_length=50, blank=True, null=False)
    invoice_no = models.CharField(max_length=6, blank=True, null=False)
    unit_price = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)
    detailfacture_id = models.AutoField(primary_key=True)

    class Meta:
        unique_together = ('stock_code', 'invoice_no')
        db_table = 'tempdetailfacture'


class tempInvoice(models.Model):
    invoice_no = models.CharField(primary_key=True, max_length=6)
    invoice_date = models.CharField(max_length=20, blank=True, null=True)
    country_name = models.CharField(max_length=50, blank=True, null=True)
    customer_id = models.CharField(max_length=5, blank=True, null=True)

    class Meta:

        db_table = 'tempinvoice'


class tempProduct(models.Model):
    stock_code = models.CharField(primary_key=True, max_length=50)
    description = models.CharField(max_length=80, blank=True, null=True)

    class Meta:

        db_table = 'tempproduct'