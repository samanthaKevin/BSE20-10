from django.contrib.auth.decorators import login_required
from django.shortcuts import render
import pandas as pd
from django_pandas.io import read_frame
from sales.models import *


# read data      
df = read_frame(Income.objects.all())

df["Sales"] = df['Revenue']

df['Months'] = pd.to_datetime(df['ReceivedDate']).dt.month_name(locale='English')
df['Years'] = df['Year']

@login_required(login_url='/admin/login/?next=/')
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


@login_required(login_url='/admin/login/?next=/')
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
    