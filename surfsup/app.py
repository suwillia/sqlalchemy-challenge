# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement= Base.classes.measurement
Station= Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
# set up Flask
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return(
            f"<style>"
            f"body {{"
            f"    font-family: Arial, sans-serif;"
            f"    margin: 20px;"
            f"    background-color: #f0f8ff;"  
            f"}}"
            f"h2 {{"
            f"    color: red;"
            f"    text-align: center;"
            f"}}"
            f"</style>"
            f"<center><h2><font color='red'>Holiday vacation in Honolulu, Hawaii climate analysis homepage.</font></h2></center>"
            f"<h3>List of available routes</h3>"
            f"<ul>"
            f"<li><a href='/api/v1.0/precipitation' target='_blank'>/api/v1.0/precipitation</a><br></li>"
            f"<li><a href='/api/v1.0/stations' target='_blank'>/api/v1.0/stations</a><br></li>"
            f"<li><a href='/api/v1.0/tobs' target='_blank'>/api/v1.0/tobs</a><br></li>"
            f"<li>/api/v1.0/&lt;startdate&gt; <i> enter start date in the format of mmddyyyy</i> <br></li>" 
            f"<li>/api/v1.0/&lt;startdate&gt;/&lt;enddate&gt;<i> enter start and end date in the format of mmddyyyy/mmddyyyy</i><br></li>"
            f"</ul>"
          

    )
#/api/v1.0/precipitation

@app.route("/api/v1.0/precipitation")
def precipitation():
    past_one_year = dt.date(2017,8,23) - dt.timedelta(days= 365)
    #past_one_year
    # Perform a query to retrieve the date and precipitation scores
    one_year_data= session.query(measurement.date,measurement.prcp).filter(measurement.date >= past_one_year).all()

    session.close()
    #create a dictionary with date and precipitation
    precip= {date: prcp for date, prcp in one_year_data}
    return jsonify(precip)

#/api/v1.0/stations

@app.route("/api/v1.0/stations")
def station():
    #show list of stations
    results= session.query(Station.station).all()
    session.close()

    #Return a JSON list of stations from the dataset
    stationList= list(np.ravel(results))
    return jsonify(stationList)

#/api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def temps():
    #Query the dates and temperature observations of the most-active station for the previous year of data
    #Return a JSON list of temperature observations for the previous year.
    past_one_year = dt.date(2017,8,23) - dt.timedelta(days= 365)
    #past_one_year
    # Perform a query to retrieve the date fromt he most active station
    most_active = session.query(measurement.date,measurement.tobs).filter(measurement.station == 'USC00519281').\
                filter(measurement.date >= past_one_year).all()
    session.close()
    tempList={date: tobs for date, tobs in most_active} 
    #Return a JSON list of the data above
    return jsonify(tempList)
#/api/v1.0/<start> and /api/v1.0/<start>/<end>
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def dateStats(start=None, end=None):
    #select statement
    selection = [func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)]

    if not end:

        startDate = dt.datetime.strptime(start,"%m%d%Y")
        results= session.query(*selection).filter(measurement.date >= startDate).all()

        session.close()
        tempList=list(np.ravel(results))
        #Return a JSON list of the data above
        return jsonify(tempList)
    else:
        startDate = dt.datetime.strptime(start,"%m%d%Y")
        endDate = dt.datetime.strptime(end,"%m%d%Y")
        results= session.query(*selection).\
                filter(measurement.date >= startDate).\
                filter(measurement.date >= endDate).all()

        session.close()
        tempList=list(np.ravel(results))
        #Return a JSON list of the data above
        return jsonify(tempList)
# use main to launch flask
if __name__ == '__main__':
    app.run(debug=True)