import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from dateutil.relativedelta import relativedelta

from flask import Flask, jsonify

# Setting up the database

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

# Setting up Flask

app = Flask(__name__)


##### TO DO #####
#/api/v1.0/api/v1.0/<start>
#/api/v1.0/api/v1.0/<start>/<end>

@app.route("/")
def home():
    list_of_routes = ["/api/v1.0/precipitation","/api/v1.0/stations","/api/v1.0/tobs","/api/v1.0/<start>","/api/v1.0/<start>/<end>"]
    return jsonify(list_of_routes)

@app.route("/api/v1.0/precipitation")
def precipitation():
    #Convert the query results to a dictionary using date as the key and prcp as the value.
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    results_dict = dict((x,y) for x, y in results)
    return jsonify(results_dict)



@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)
    results = session.query(Station.name).all()

    session.close()

    station_names = list(np.ravel(results))
    return jsonify(station_names)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]

    # Use datetime to get the date for one year before the most recent date
    recent_datetime = dt.datetime.strptime(most_recent_date, '%Y-%m-%d')
    last_year_datetime = recent_datetime - relativedelta(years=1)
    last_year = dt.datetime.strftime(last_year_datetime, '%Y-%m-%d')

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= last_year).order_by(Measurement.date).all()
    session.close()

    results_dict = dict((x,y) for x, y in results)
    return jsonify(results_dict)

@app.route("/api/v1.0/<start>")
def start_range(start):
    session = Session(engine)
    lowest_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start)[0][0]
    highest_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start)[0][0]
    average_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start)[0][0]
    session.close()

    results = {
        "TMIN":lowest_temp,
        "TAVG":average_temp,
        "TMAX":highest_temp
    }

    return jsonify(results)

@app.route("/api/v1.0/<start>/<end>")
def start_end_range(start, end):
    session = Session(engine)
    lowest_temp = session.query(func.min(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end)[0][0]
    highest_temp = session.query(func.max(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end)[0][0]
    average_temp = session.query(func.avg(Measurement.tobs)).filter(Measurement.date >= start, Measurement.date <= end)[0][0]
    session.close()

    results = {
        "TMIN":lowest_temp,
        "TAVG":average_temp,
        "TMAX":highest_temp
    }

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)