from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import redirect
import pandas as pd
import datetime
import numpy as np
import csv
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
ValidColumns = ['Name', 'Quantity', 'Unit Cost', 'Total Cost', 'Expense group', 'Year']

def allowed_files(filename):
    if not "." in filename:
        return False
    
    ext = filename.rsplit(".", 1)[1]

    if ext.upper() == csvEXT.upper():
        return True
    else:
        return False

@login_required(login_url='admin/login/?next=/')
def home(request):
    return redirect("indexf.html")

@login_required(login_url='admin/login/?next=/')
def weather(request):
    return redirect("weather.html")

@login_required(login_url='admin/login/?next=/')
def prices(request):
    return redirect("prices.html")

@login_required(login_url='admin/login/?next=/')
def riskassessment(request):
    mydata = models.Expenses.query.all()
    dfData = pd.read_sql(models.Expenses.query.statement, db.session.bind)
    dfData['ItemName'] = 1
    dfData['District'] = 9
    predictiveData = dfData[['Year','ItemName','District']].values
    prediction = regressor.predict(predictiveData)
    dfData['PredictedPrices'] = prediction
    return redirect("riskassessment.html", financial_data=dfData, myLength = len(dfData))

@login_required(login_url='admin/login/?next=/')
def importExpenseCSV(request):
    if request.method == "POST":
        if request.files:
            mycsv = request.files["fileToUpload"]
            try:
                if mycsv.filename == "":
                    raise Exception("No filename") 

                if allowed_files(mycsv.filename):
                    filename = secure_filename(mycsv.filename)

                    mycsv.save(os.path.join(CSV_UPLOADS, filename))
                    url = CSV_UPLOADS +"/"+filename
                    df = pd.read_csv(url)
                    
                    index = 0
                    for col_name in df.columns:
                        
                        if col_name == ValidColumns[index]:
                            index = index + 1
                            continue
                        else:
                            raise Exception("Invalid Column Name "+col_name) 

                    #models.SaveExpense(df.values)
                    arr = df.values
                    for i in range(len(arr)) : 
                        mydata = models.Expenses.query.filter_by(Year = arr[i,5]).all()
                        origTotalCost = 0

                        if len(mydata) > 0:
                            origTotalCost = mydata[0].TotalCost
                        
                        expenseDetails = models.ExpenseDetails(
                        ExpenseName = arr[i,0],
                        Quantity = arr[i,1],
                        UnitCost = arr[i,2],
                        TotalCost = arr[i,3],
                        ExpenseGroup = arr[i,4],
                        Year = arr[i,5]
                        )
                        expense = models.Expenses(
                        Year = arr[i,5],
                        TotalCost = arr[i,3] + origTotalCost
                        )
                        db.session.add(expenseDetails)
                        db.session.merge(expense)
                        db.session.commit()

                    return render_template('importExpense.html', error="Records successfully inserted")
                else:
                    raise Exception("That file extension is not allowed") 

            except Exception as e:
                db.session.rollback()
                msg = str(e)
                return redirect('importExpense.html', error=msg)

    return redirect("importExpense.html")

@login_required(login_url='admin/login/?next=/')
def importIncomeCSV(request):
    if request.method == "POST":
        if request.files:
            mycsv = request.files["fileToUpload"]
            if mycsv.filename == "":
                print("No filename")
                return redirect(request.url)

            if allowed_files(mycsv.filename):
                filename = secure_filename(mycsv.filename)
                mycsv.save(os.path.join(CSV_UPLOADS, filename))
                print("CSV saved")
                return redirect(request.url)
            else:
                print("That file extension is not allowed")
                return redirect(request.url)

    return redirect("importIncome.html")

@login_required(login_url='admin/login/?next=/')
def predictPrice(request):
    int_features = [x for x in request.form.values()]
    final = np.array(int_features)
    data_unseen = pd.DataFrame([final])
    prediction = regressor.predict(data_unseen)
    return redirect('prices.html', pred='Expected Market Price in UGX per Kg will be {}'.format(prediction))

@login_required(login_url='admin/login/?next=/')
def predict(request):
    df = pd.read_csv("sales/CSVfiles/TestTemplate.csv")

    #MyArray = df.values
    Kampala = df2[df2.Name == 'KAMPALA']
    Kampala = Kampala[['Year','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']]

    X = Kampala[['Year']].values
    Y = Kampala[['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']].values

    mlp = MLPRegressor()
    mlp.fit(X, Y)

    int_features = [x for x in request.form.values()]
    final = np.array(int_features)
    data_unseen = pd.DataFrame([final])
    prediction = mlp.predict(data_unseen)
    return redirect('weather.html', pred='Expected Rainfall in mm will be {}'.format(prediction))

# read data   
try:
    df = read_frame(Income.objects.all())

    df["Sales"] = df['Revenue']

    df['Months'] = pd.to_datetime(df['ReceivedDate']).dt.month_name(locale='English')
    df['Years'] = df['Year']
except Exception as e:
    df = pd.DataFrame()
    df['Sales'] = 0
    df['Months'] = datetime.datetime.now().month
    df['Years'] = datetime.datetime.now().year

@login_required(login_url='admin/login/?next=/')
def index(request):

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
    