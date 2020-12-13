from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.shortcuts import render
import pandas as pd
import datetime
import numpy as np
import csv
import os.path
from django_pandas.io import read_frame
from sales.models import *
from sklearn.linear_model import LinearRegression
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from werkzeug.utils import secure_filename

df2 = pd.read_csv("sales/CSVfiles/KampalaBeansAv.csv")

X = df2[['Year','ItemName','District']].values
Y = df2['AvPrice'].values

regressor = LinearRegression()
regressor.fit(X,Y)

CSV_UPLOADS = "sales/temp"
#app.config["ALLOWED_CSV_EXTENSIONS"] = ["CSV"]
csvEXT = "CSV"
ValidExpenseColumns = ['Name', 'Quantity', 'Unit Cost', 'Total Cost', 'Expense group', 'Year']
ValidIncomeColumns = ['Revenue', 'Year', 'Date Received']

def allowed_files(filename):
    if not "." in filename:
        return False
    
    ext = filename.rsplit(".", 1)[1]

    if ext.upper() == csvEXT.upper():
        return True
    else:
        return False

@login_required(login_url='admin/login/?next=/')
def weather(request):
    return render(request, "weather.html")

@login_required(login_url='admin/login/?next=/')
def prices(request):
    return render(request, "prices.html")

@login_required(login_url='admin/login/?next=/')
def riskassessment(request):
    #mydata = models.Expenses.query.all()
    dfData = read_frame(Expenses.objects.all())
    dfData['ItemName'] = 1
    dfData['District'] = 9
    predictiveData = dfData[['Year','ItemName','District']].values
    prediction = regressor.predict(predictiveData)
    dfData['PredictedPrices'] = prediction
    dfData['Income'] = 450 * dfData['PredictedPrices']
    dfData['Profit'] = dfData['Income'] - dfData['TotalCost']
    final = dfData[['Year','TotalCost','PredictedPrices', 'Income', 'Profit']]
    context = {
        'financial_data': final,
    }
    return render(request, "riskassessment.html", context)

@login_required(login_url='admin/login/?next=/')
def importExpenseCSV(request):
    if request.method == "POST":
        mycsv = request.FILES["fileToUpload"]
        url = ""
        fs = FileSystemStorage()
        try:
            if mycsv.name == "":
                raise Exception("No filename") 

            if allowed_files(mycsv.name):
                #filename = secure_filename(mycsv.name)
                name = fs.save(mycsv.name, mycsv)

                url = fs.url(name)

                df = pd.read_csv(url[1:])
                    
                index = 0
                for col_name in df.columns:
                        
                    if col_name == ValidExpenseColumns[index]:
                        index = index + 1
                        continue
                    else:
                        raise Exception("Invalid Column Name "+col_name) 

                #models.SaveExpense(df.values)
                arr = df.values
                sid = transaction.savepoint()
                for i in range(len(arr)) : 
                    mydata = Expenses.objects.all().filter(Year = arr[i,5])
                    origTotalCost = 0

                    if len(mydata) > 0:
                        origTotalCost = mydata[0].TotalCost
                        
                    expenseDetails = ExpenseDetails(
                    ExpenseName = arr[i,0],
                    Quantity = arr[i,1],
                    UnitCost = arr[i,2],
                    TotalCost = arr[i,3],
                    ExpenseGroup = arr[i,4],
                    Year = arr[i,5]
                    )
                    expenses = Expenses(
                    Year = arr[i,5],
                    TotalCost = arr[i,3] + origTotalCost
                    )
                    expenseDetails.save()
                    expenses.save()
                transaction.savepoint_commit(sid)
                context = {
                'error': "Records successfully inserted",
                }
                return render(request, 'importExpense.html', context)
            else:
                raise Exception("That file extension is not allowed") 
            
        except Exception as e:
            transaction.savepoint_rollback(sid)
            msg = str(e)
            context = {
                'error': msg,
            }
            return render(request, 'importExpense.html', context)
        finally:
            fs.delete(mycsv.name)
            
    return render(request, "importExpense.html")

@login_required(login_url='admin/login/?next=/')
def importIncomeCSV(request):
    if request.method == "POST":
        mycsv = request.FILES["fileToUpload"]
        url = ""
        fs = FileSystemStorage()
        sid = transaction.savepoint()
        try:
            if mycsv.name == "":
                raise Exception("No filename") 

            if allowed_files(mycsv.name):
                #filename = secure_filename(mycsv.name)
                name = fs.save(mycsv.name, mycsv)

                url = fs.url(name)

                df = pd.read_csv(url[1:])
                    
                index = 0
                for col_name in df.columns:
                        
                    if col_name == ValidIncomeColumns[index]:
                        index = index + 1
                        continue
                    else:
                        raise Exception("Invalid Column Name "+col_name) 

                #models.SaveExpense(df.values)
                arr = df.values

                sid = transaction.savepoint()
                for i in range(len(arr)) : 
                    income = Income(
                    Revenue = arr[i,0],
                    Year = arr[i,1],
                    ReceivedDate = arr[i,2],
                    )
                    income.save()
                transaction.savepoint_commit(sid)
                context = {
                'error': "Records successfully inserted",
                }
                return render(request, 'importIncome.html', context)
            else:
                raise Exception("That file extension is not allowed") 
            
        except Exception as e:
            transaction.savepoint_rollback(sid)
            msg = str(e)
            context = {
                'error': msg,
            }
            return render(request, 'importIncome.html', context)
        finally:
            fs.delete(mycsv.name)
            
    return render(request, "importIncome.html")

@login_required(login_url='admin/login/?next=/')
def predictPrice(request):
    int_features = [request.POST.get('Year'), request.POST.get('ItemName'), request.POST.get('District')]
    final = np.array(int_features)
    data_unseen = pd.DataFrame([final])
    prediction = regressor.predict(data_unseen)
    context = {
        'pred': 'Expected Market Price in UGX per Kg will be {}'.format(prediction),
    }
    return render(request, 'prices.html', context)

@login_required(login_url='admin/login/?next=/')
def predict(request):
    df = pd.read_csv("sales/CSVfiles/TestTemplate.csv")

    #MyArray = df.values
    Kampala = df[df.Name == 'KAMPALA']
    Kampala = Kampala[['Year','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']]

    X = Kampala[['Year']].values
    Y = Kampala[['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']].values

    mlp = MLPRegressor()
    mlp.fit(X, Y)

    int_features = [request.POST.get('Year')]
    final = np.array(int_features)
    data_unseen = pd.DataFrame([final])
    prediction = mlp.predict(data_unseen)
    context = {
        'pred': 'Expected Rainfall in mm will be {}'.format(prediction),
    }
    return render(request, 'weather.html', context)

# read data 

@login_required(login_url='admin/login/?next=/')
def index(request):
    df = read_frame(Income.objects.all())
    df["Sales"] = df['Revenue']

    df['Months'] = pd.to_datetime(df['ReceivedDate']).dt.month_name()
    df['Years'] = df['Year']

    rs_bar = df.groupby("Years")["Sales"].agg("sum")
    categoriesbar = list(rs_bar.index)
    valuesbar = list(rs_bar.values)
    
    #Overall Sales total
    total_sum = df['Sales'].sum()
    total_sum = '{:,}'.format(total_sum)
    
    #Average Sales total
    total_average = df['Sales'].mean()
    total_average = '{:,}'.format(total_average)
    
    #Highest Sales
    highest_sales = df['Sales'].max()
    highest_sales = '{:,}'.format(highest_sales)
    
    
    year_table = rs_bar.reset_index().to_html(index=None, table_id='tableExport')
    year_table = year_table.replace("", "")
    year_table = year_table.replace('class="dataframe"', "class='table table-striped'")
    year_table = year_table.replace('border="1"', "")
    
    data = []
    # for index in range(0, len(rs_bar.index)):
    
    #     # print(rs_bar.index[index])
    #     # print('{:,}'.format(rs_bar.values[index]))
    #     value = {'name': rs_bar.index[index], 'y': '{:,}'.format(rs_bar.values[index])  }
    #     data.append(value)

    context = {
        'categoriesbar': categoriesbar,
        'valuesbar': valuesbar,
        'overall_total': total_sum,
        'total_average': total_average,
        'highest_sales': highest_sales,
        'year_table': year_table,
    }
    return render(request,'sales/dashboard.html', context)


@login_required(login_url='admin/login/?next=/')
def salesreport(request):
    df = read_frame(Income.objects.all())
    df["Sales"] = df['Revenue']

    df['Months'] = pd.to_datetime(df['ReceivedDate']).dt.month_name()
    df['Years'] = df['Year']
    rs = df.groupby("Months")["Sales"].agg("sum")
    # print(rs)

    categories = list(rs.index)
    values = list(rs.values)
    
    table_content = df.to_html(index=None, table_id='tableExport')
    table_content = table_content.replace("", "")
    table_content = table_content.replace('class="dataframe"', "class='table table-striped'")
    table_content = table_content.replace('border="1"', "")
    
    context = {
        'table_data': table_content,
        "categories": categories,
        'values': values,
    }
    return render(request, 'sales_table.html', context)  
    