import json
import numpy as np
import pandas as pd
import plotly.plotly as py
import us_states
from plotly.graph_objs import *
from os import listdir
from os.path import isfile, join

DATASET_DIR = 'yelp_us_top_715_cities_restaurants'

def listFiles(directory): 
  return [f for f in listdir(directory) if (isfile(join(directory, f)) and f.endswith('.json'))]

def readJsonFile(filename):
  with open(filename, 'r') as f:
    return json.load(f)

def readDataFrameFromJson():
  filenames = listFiles(DATASET_DIR)
  print filenames
  # Read from JSON files.
  businesses = []
  for filename in filenames:
    businesses.extend(readJsonFile(join(DATASET_DIR, filename)))
  print "Number of businesses:", len(businesses)
  # Convert businesses into DataFrame.
  df = pd.DataFrame(businesses)
  return df

def plotReviewStatsByStates():
  try: 
    df = pd.read_csv('review_stats_by_states.csv')
  except:
    df_restaurants = readDataFrameFromJson()
    df_restaurants['state_code'] = pd.Series([location['state_code'] for location in df_restaurants['location']])
    df = pd.DataFrame(df_restaurants.groupby(by=['state_code'])['review_count'].mean().round(2).reset_index())
    df.to_csv('review_stats_by_states.csv', encoding='utf-8')  

  df = df.ix[[code in set(us_states.state_code_to_name.keys()) for code in df['state_code']]].reset_index(drop=True)
  df['state_name'] = pd.Series([us_states.state_code_to_name[code] for code in df['state_code']])
  print df
  
  for col in df.columns:
    df[col] = df[col].astype(str)            
  df['text'] = df['state_name'] + ' ' + 'Mean Review Count: ' + df['review_count']

  scl = [[0.0, 'rgb(242,240,247)'],[0.2, 'rgb(218,218,235)'],[0.4, 'rgb(188,189,220)'],\
            [0.6, 'rgb(158,154,200)'],[0.8, 'rgb(117,107,177)'],[1.0, 'rgb(84,39,143)']]
  data = [ dict(
        type='choropleth',
        colorscale = scl,
        autocolorscale = False,
        locations = df['state_code'],
        z = df['review_count'].astype(float),
        locationmode = 'USA-states',
        text = df['text'],
        marker = dict(
            line = dict (
                color = 'rgb(255,255,255)',
                width = 2
            )
        ),
        colorbar = dict(
            title = "Number of Reviews"
        )
    ) ]
  layout = dict(
          title = 'Yelp Restaurant Review Stats by State (Hover for breakdown)',
          geo = dict(
              scope='usa',
              projection=dict( type='albers usa' ),
              showlakes = True,
              lakecolor = 'rgb(255, 255, 255)',
          ),
      )
  fig = dict( data=data, layout=layout )
  url = py.plot( fig, validate=False, filename='d3-cloropleth-map' )

def plotClassifierResults():
  classifiers = ['Logistic Regression', 'Decision Tree']
  features = ['Text Feature', 'Text + Review Count Feature']
  metrics = ['Precision', 'Recall', 'F1-Score']
  traces = []
  traces.append(Bar(
      x=metrics,
      y=[0.67, 0.72, 0.63],
      name="%s (%s)" % (classifiers[0], features[0])
  ))
  traces.append(Bar(
      x=metrics,
      y=[0.66, 0.71, 0.61],
      name="%s (%s)" % (classifiers[0], features[1])
  ))
  traces.append(Bar(
      x=metrics,
      y=[0.78, 0.79, 0.76],
      name="%s (%s)" % (classifiers[1], features[0])
  ))
  traces.append(Bar(
      x=metrics,
      y=[0.88, 0.84, 0.85],
      name="%s (%s)" % (classifiers[1], features[1])
  ))
  data = Data(traces)
  layout = Layout(
      barmode='group'
  )
  fig = Figure(data=data, layout=layout)
  plot_url = py.plot(fig, filename='yelp-prediction-classifier-comparison')

def main():
  plotReviewStatsByStates()
  plotClassifierResults()


if __name__ == "__main__":
  main()