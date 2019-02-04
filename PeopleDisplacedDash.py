import DataUpdate
import pandas as pd
import plotly.plotly as py
import plotly
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_html_components as html


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


r= DataUpdate.WDIData()
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