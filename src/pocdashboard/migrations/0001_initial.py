# Generated by Django 4.1.3 on 2022-12-01 06:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('country_name', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('zone_name', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'db_table': 'Country',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('stock_code', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=80, null=True)),
            ],
            options={
                'db_table': 'Product',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('invoice_no', models.CharField(max_length=6, primary_key=True, serialize=False)),
                ('invoice_date', models.DateTimeField(blank=True, null=True)),
                ('customer_id', models.CharField(blank=True, max_length=5, null=True)),
                ('country_name', models.ForeignKey(db_column='country_name', on_delete=django.db.models.deletion.DO_NOTHING, to='pocdashboard.country')),
            ],
            options={
                'db_table': 'Invoice',
            },
        ),
        migrations.CreateModel(
            name='Detailfacture',
            fields=[
                ('unit_price', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('quantity', models.IntegerField(blank=True, null=True)),
                ('detailfacture_id', models.AutoField(primary_key=True, serialize=False)),
                ('invoice_no', models.ForeignKey(blank=True, db_column='invoice_no', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='pocdashboard.invoice')),
                ('stock_code', models.ForeignKey(blank=True, db_column='stock_code', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='pocdashboard.product')),
            ],
            options={
                'db_table': 'Detailfacture',
            },
        ),
    ]
