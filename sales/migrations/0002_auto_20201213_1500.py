# Generated by Django 3.1.4 on 2020-12-13 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expensedetails',
            name='ExpenseID',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='income',
            name='IncomeID',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
