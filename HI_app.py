import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime



engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

app = Flask(__name__)


# last_date_query = session.query(Measurement.date).order_by(Measurement.id.desc()).limit(1)

# for item in last_date_query:
#     last_date = dt.datetime.strptime(item.date, "%Y-%m-%d").date() - dt.timedelta(days=364)

@app.route("/")
def home():
    
    return (
        f"Available Routes:<br/>"
        f"<ul>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"<li>'/api/v1.0/<start>'</li>"
        f"<li>'/api/v1.0/<start>/<end>'</li>"
        f"</ul>")

@app.route("/api/v1.0/precipitation")

def precip():

    last_date_query = session.query(Measurement.date).order_by(Measurement.id.desc()).limit(1)

    for item in last_date_query:
        last_date = dt.datetime.strptime(item.date, "%Y-%m-%d").date() - dt.timedelta(days=364)

    year_precip = session.query(Measurement.date, func.avg(Measurement.prcp).label('Average')).\
        filter(Measurement.date >= last_date).\
        order_by(Measurement.date.asc()).\
        group_by(Measurement.date)

    precip_dict = {}
    for day in year_precip:
        date = day.date
        prcp = day.Average
        precip_dict[date] = prcp
    
    return jsonify(precip_dict)

@app.route("/api/v1.0/stations")

def stations():
    station_info = session.query(Measurement.station, func.count(Measurement.station).label('Count')).\
        order_by(func.count(Measurement.station).desc()).\
        group_by(Measurement.station).all()
    
    all_stations = list(np.ravel(station_info))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")

def tobs():

    last_date_query = session.query(Measurement.date).order_by(Measurement.id.desc()).limit(1)

    for item in last_date_query:
        last_date = dt.datetime.strptime(item.date, "%Y-%m-%d").date() - dt.timedelta(days=364)
        
    year_tobs = session.query(Measurement.date, func.avg(Measurement.tobs).label('Average')).\
        filter(Measurement.date >= last_date).\
        order_by(Measurement.date.asc()).\
        group_by(Measurement.date).all()
    
    all_tobs = list(np.ravel(year_tobs))

    return jsonify(all_tobs)

#   * query for the dates and temperature observations from a year from the last data point.
#   * Return a JSON list of Temperature Observations (tobs) for the previous year.  

@app.route("/api/v1.0/<start>")

def temps(start):
    
    all_temps =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    temps_list = list(np.ravel(all_temps))

    return jsonify(temps_list)

@app.route("/api/v1.0/<start>/<end>")

def temp_range(start,end):
    
    temps_range = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temp_range_list = list(np.ravel(temps_range))

    return jsonify(temp_range_list)

# `/api/v1.0/<start>` and `/api/v1.0/<start>/<end>`

#   * Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

#   * When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date.

#   * When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates between the start and end date inclusive.

if __name__ == '__main__':
    app.run(debug=True)