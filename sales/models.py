from django.db import models
import numpy as np
import pandas as pd
# Create your models here.

class Expenses(models.Model):
    Year = models.IntegerField(primary_key =True)
    TotalCost = models.FloatField()
    RecordDateTime = models.DateTimeField(auto_now=True)

    def __init__(self, Year, TotalCost):
        self.Year = Year
        self.TotalCost = TotalCost

    def __repr__(self):
        return '<Year %r>' % self.Year

class ExpenseDetails(models.Model):
    ExpenseID = models.IntegerField(primary_key =True)
    ExpenseName = models.CharField(max_length=80)
    Quantity = models.IntegerField()
    UnitCost = models.FloatField()
    TotalCost = models.FloatField()
    ExpenseGroup = models.CharField(max_length=20)
    Year = models.IntegerField()
    RecordDateTime = models.DateTimeField(auto_now=True)

    def __init__(self, ExpenseName, Quantity, UnitCost, TotalCost, ExpenseGroup, Year):
        self.ExpenseName = ExpenseName
        self.Quantity = Quantity
        self.UnitCost = UnitCost
        self.TotalCost = TotalCost
        self.ExpenseGroup = ExpenseGroup
        self.Year = Year

    def __repr__(self):
        return '<Expense %r>' % self.ExpenseName

class Income(models.Model):
    IncomeID = models.IntegerField(primary_key =True)
    Revenue = models.FloatField()
    Year = models.IntegerField()
    ReceivedDate = models.DateTimeField()
    RecordDateTime = models.DateTimeField(auto_now=True)

    def __init__(self, Revenue, Year, ReceivedDate):
        self.Revenue = Revenue
        self.Year = Year
        self.UnitCost = UnitCost
        self.ReceivedDate = ReceivedDate

    def __repr__(self):
        return '<Year %r>' % self.Year
