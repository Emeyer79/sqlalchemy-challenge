import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect = True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """precipitation with dates"""
    # retrieve the last 12 months of precipitation data 
    # Query all precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()
    
    precip_date = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["Date"] = date
        precipitation_dict["Precipitation"] = prcp
        precip_date.append(prcp_dict)

        return jsonify(precip_date)
    
####################################################################################################################################
        
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    """List of Stations"""
    # Return a JSON list of stations from the dataset.
    results = session.query(Station.station, Station.name).all()
    
    session.close()

    all_stations = []
    for station, name in results:
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Station Name"] = name
        all_stations.append(station_dict)
    
    return jsonify(all_stations)
    
####################################################################################################################################
    
@app.route("/api/v1.0/tobs")
def tobs():
    # Create session from Python to the DB
    session = Session(engine)
    
    # Find the most recent date in the data set.
    rec_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    rec_date = datetime.strptime(rec_date[0], '%Y-%m-%d').date()
    
    #find the date from 12 months ago
    months = dt.datetime.strptime(rec_date, '%Y-%m-%d')  - dt.timedelta(days=365)
    
    
    #Query the dates and temperature observations of the most active station for the last year of data.
    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= months).all()
    
    session.close()
    
    all_temps = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["Date"] = date
        temp_dict["Temperature"] = tobs
        all_temps.append(temp_dict)  

    return jsonify(all_temps)


########################################################################################################################################

@app.route("/api/v1.0/<start>")
def start_dt(start):
    # Create session from Python to the DB
    session = Session(engine)
    
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

    start_dt = datetime.strptime(start, '%Y-%m-%d').date()

    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start_dt).all()
    temp_stats = list(np.ravel(temperature_stats))
    return jsonify(temp_stats)


#################################################################################################################################################

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create session from Python to the DB
    session = Session(engine)

    start_date = datetime.strptime(start, '%Y-%m-%d').date()
    end_date = datetime.strptime(end, '%Y-%m-%d').date()
    start = dt.datetime.strptime(start_date, '%Y-%m-%d')  - dt.timedelta(days=365)
    end = dt.datetime.strptime(end_date, '%Y-%m-%d')  - dt.timedelta(days=365)
    

    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    temps_stats_results = list(np.ravel(temperature_stats))    
    return jsonify(temps_stats_results)


###############################################################################################################################

if __name__ == '__main__':
    app.run(debug=True)
    
    