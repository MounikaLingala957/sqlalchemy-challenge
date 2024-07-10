# Import the dependencies.
import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine,func,desc
from flask import Flask, jsonify
from sqlalchemy.orm import Session


#################################################
# Database Setup
#################################################
engine=create_engine("sqlite:///Homework\sqlalchemy-challenge\Starter_Code\Resources\hawaii.sqlite")

# reflect an existing database into a new model
Base= automap_base()
# reflect the tables
Base.prepare(autoload_with =engine)

# Save references to each table

Base.classes.keys()
Measurment = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session=Session(engine)

#################################################
# Flask Setup
#################################################
app=Flask(__name__)

#app routes
#app route for homepage
@app.route("/")
def homepage():
   """List all available api routes
   """
   return(
      f"Available Routes:<br/>"
      f"/api/v1.0/precipitation<br>"
      f"/api/v1.0/stations<br>"
      f"/api/v1.0/tobs<br>"
      f"/api/v1.0/&lt;start&gt;<br/>"
      f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
   )
@app.route("/api/v1.0/precipitation")
def precp():
   # Starting from the most recent data point in the database.
    recent_date= session.query(Measurment.date).order_by(desc(Measurment.date)).first()
    recent_date=recent_date[0]
    recent_date

    # Calculate the date one year from the last date in data set.
    Previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    oneyear_data=session.query(Measurment.date, Measurment.prcp).filter(Measurment.date >=Previous_year,Measurment.date<=recent_date).all()

    session.close()

    # dictionary- date=key / prcp=value
    precipitation = {date: prcp for date, prcp in oneyear_data}
    
    # convert to json
    return jsonify(precipitation)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def station():
   station_list=session.query(Station.station).all()
   session.close()
   station_list = list(np.ravel(station_list))
   return(
      jsonify(station_list)
   )
#Query the dates and temperature observations of the most-active station for the previous year of data.

@app.route("/api/v1.0/tobs")
def temp():
   # Starting from the most recent data point in the database.
    recent_date= session.query(Measurment.date).order_by(desc(Measurment.date)).first()
    recent_date=recent_date[0]
    recent_date

   # Calculate the date one year from the latest date in data set.
    Previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)


    previousyear_data=session.query(Measurment.tobs).\
    filter(Measurment.date <=recent_date, Measurment.date>=Previous_year).\
    filter(Measurment.station == 'USC00519281').all()
    session.close()
    previousyear_list=list(np.ravel(previousyear_data))

    return(
       jsonify(previousyear_list)
    )
#Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_temps(start=None,end=None):
   calculations=[func.min(Measurment.tobs),func.max(Measurment.tobs),func.avg(Measurment.tobs)]
   
   if not end:
      startdate=dt.datetime.strptime(start,"%m%d%Y")
      result=session.query(*calculations).filter((Measurment.date)>=startdate).all()
      session.close()
      temp_list=list(np.ravel(result))
      return jsonify(temp_list)
   else:
      startdate=dt.datetime.strptime(start,"%m%d%Y")
      enddate = dt.datetime.strptime(end,"%m%d%Y")
      result=session.query(*calculations).filter((Measurment.date)>=startdate,(Measurment.date)<=enddate).all()
      session.close()
      temp_list=list(np.ravel(result))
      return jsonify(temp_list)
#example date format to test api : http://localhost:5000/api/v1.0/01012017


#################################################
# Flask Routes
#################################################
if __name__== '__main__':
   app.run(debug=True)