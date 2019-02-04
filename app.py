import DataUpdate
import pandas as pd
import plotly.plotly as py
import plotly
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def WDIData():
    import numpy as np
    import requests
    import matplotlib.pyplot as plt
    import pandas as pd
    import csv
    import xlrd
    import matplotlib.lines as mlines
    import xlsxwriter
    import matplotlib.transforms as mtransforms
    import statsmodels.api as sm
    # from urllib.request import urlopen
    from bs4 import BeautifulSoup
    from xml.dom import minidom
    import xml.etree.cElementTree as et
    import dask.dataframe as dd

    # Step 1: First read in the excel/csv with the relevant WDI codes and print out the WDI codes to be sure we have the right number of values
    datadict = pd.read_excel('C:\\Users\Public\Pythonfiles\WDICodes.xlsx', sheet_name='Sheet1',
                             dtype='str')  # Replace the location of code files for your desktop
    print('Hey User!, you are importing ' + (str(len(datadict[
                                                         'WDI Code'])) + ' series. To import additional series please update the file WDICodes.xlsx located in the Pythonfiles folder'))

    # print(datadict['WDI Code'])

    print('Step 1 Complete: All files read in')

    # Step 2: Prepare columns for series name,country,year,value
    Seriesname = []
    Countryname = []
    SeriesCode = []
    Year = []
    Value = []

    print(
        'We will be starting the loop for all codes now.')
    # Step 3: Create a loop for reading in all the codes into the url and parsing the xml file for relevant values.This helps in pulling in 500 series at a time
    for row in datadict['WDI Code']:
        wiki = 'http://api.worldbank.org/v2/countries/all/indicators/' + str(row) + '/?format=xml&per_page=20000'
        r = requests.get(wiki, stream=True)
        root = et.fromstring(r.content)

        for child in root.iter("{http://www.worldbank.org}indicator"):
            SeriesCode.append(child.attrib['id'])
        for child in root.iter("{http://www.worldbank.org}country"):
            Countryname.append(child.text)
        for child in root.iter("{http://www.worldbank.org}date"):
            Year.append(child.text)
        for child in root.iter("{http://www.worldbank.org}value"):
            Value.append((child.text))
    print('Loop is complete.Hard part is over now!')

    # Step 4: Write all the parsed values to the dataframe in Step 2
    test_df = pd.DataFrame.from_dict({'SeriesName': SeriesCode,
                                      'Country': Countryname,
                                      'Year': Year,
                                      'Value': Value}, orient='index')
    print('Step 4 complete! You have a data frame now!')
    # Step 5: Read in concordance tables for Countries and series
    countryconcord = pd.read_csv('C:\\Users\Public\Pythonfiles\CountryConcordanceWDI.csv', encoding="ISO-8859-1")
    seriesconcord = pd.read_csv('C:\\Users\Public\Pythonfiles\CodeConcordanceWDI.csv', encoding="ISO-8859-1")

    print('Step 5 complete! We have read in the concordance tables')
    # Step 6: Create a transponsed file using the dataframe
    df = test_df.transpose()
    print(df.head())
    print('Step 6 complete! We have a transposed dataset!')

    # Step 7:Concord country and series names
    df = pd.merge(df, countryconcord, how='left', left_on='Country', right_on='Country')
    df = pd.merge(df, seriesconcord, how='left', left_on='SeriesName', right_on='CodeinIfs')

    print('Step 7 complete! We have a merged dataset now!')
    df['Value'].fillna(0,inplace=True)
    # Step 8: Drop null values to keep data managable
    #df = df[pd.notnull(df['Value'])]
    df = df[pd.notnull(df['Country name in IFs'])]
    df = df[pd.notnull(df['Series name in IFs'])]

    print('We have dropped all null values!')
    # Step 9: Write to a pivot table
    #data = pd.pivot_table(df, index=['Country name in IFs', 'CodeinIfs'], columns=['Year'], values=['Value'],
                          #aggfunc=[np.sum])
    data=df
    data.reset_index()
    data=pd.DataFrame(data)
    return (data)





r= WDIData()
print(r.head())

r=r.iloc[1:]
r=r.drop(['Series name in IFs','SeriesName'],axis=1)


app=dash.Dash(__name__)

#plotly.tools.set_credentials_file(username='kanishkan91',api_key='aYeSpFRWLtq4L1a2k6VC')

#fig = dict( data=data, layout=layout )


app.layout  = html.Div([
    dcc.Graph(id='graph-with-slider',style={'height':600}),
    dcc.Slider(id='year-slider',
        min=2010,
        max=2016,
        value=2010,
        marks={'2010':'2010','2011':'2011','2012':'2012','2013':'2013','2014':'2014','2015':'2015','2016':'2016'}
               )

],style={'width':'75%'})
@app.callback(dash.dependencies.Output('graph-with-slider', 'figure'),
    [dash.dependencies.Input('year-slider', 'value')])
   #[dash.dependencies.State('year-slider', 'marks')])

def update_figure(selected_year):
    filtered_r=r[r.Year == str(selected_year)]
    print((filtered_r.head()))


    data = [dict(
        type='choropleth',
        locations=filtered_r['Country name in IFs'],
        z=filtered_r['Value'],
        text=filtered_r['Country'],
        colorscale=[[0, "rgb(0, 0.5, 0.6)"], [0.25, "rgb(40, 60, 190)"], [0.50, "rgb(70, 100, 245)"], \
                    [0.55, "rgb(90, 120, 245)"], [0.7, "rgb(106, 137, 247)"], [0.85, "rgb(150,220,220)"],
                    [0.95, "rgb(175,220,220)"], [1, "rgb(220, 220, 220)"]],
        autocolorscale=False,
        reversescale=True,
        marker=dict(
            line=dict(
                color='rgb(180,180,180)',
                width=0.5
            )),
        colorbar=dict(
            autotick=False,
            ticksuffix=' people',
            title='Displacement'),
    )]
    layout = dict(
        title='<br>\
                <a href="https://data.worldbank.org/indicator/VC.IDP.NWDS">\
                Global displacement of people by conflict (using data from WDI)</a>',
        geo=dict(
            showframe=False,
            showcoastlines=False,
            hovermode='closest',
            projection=dict(
                type='Mercator'
            ),
            resolution=200
        )
    )
    return {
        'data':data,
        'layout':layout

    }

if __name__ == '__main__':
    app.run_server(debug=True)