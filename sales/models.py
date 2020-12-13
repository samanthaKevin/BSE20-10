from django.db import models
import numpy as np
import pandas as pd
# Create your models here.

class Expenses(models.Model):
    Year = models.IntegerField(primary_key =True)
    TotalCost = models.FloatField()
    RecordDateTime = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<Year %r>' % self.Year

class ExpenseDetails(models.Model):
    ExpenseID = models.AutoField(primary_key =True)
    ExpenseName = models.CharField(max_length=80)
    Quantity = models.IntegerField()
    UnitCost = models.FloatField()
    TotalCost = models.FloatField()
    ExpenseGroup = models.CharField(max_length=20)
    Year = models.IntegerField()
    RecordDateTime = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<Expense %r>' % self.ExpenseName

class Income(models.Model):
    IncomeID = models.AutoField(primary_key =True)
    Revenue = models.FloatField()
    Year = models.IntegerField()
    ReceivedDate = models.DateTimeField()
    RecordDateTime = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return '<Year %r>' % self.Year
