import numpy as np
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime



engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

app = Flask(__name__)



@app.route("/")
def home():
    
    return (
        f"Available Routes:<br/>"
        f"<ul>"
        f"<li>/api/v1.0/precipitation</li>"
        f"<li>/api/v1.0/stations</li>"
        f"<li>/api/v1.0/tobs</li>"
        f"<li>/api/v1.0/&ltstart&gt</li>"
        f"<li>/api/v1.0/&ltstart&gt/&ltend&gt</li>"
        f"<li>Example: /api/v1.0/2012-02-28/2012-03-05</li>"
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

    station_names = session.query(Station.name).all()

    return jsonify(station_names)

@app.route("/api/v1.0/tobs")

def tobs():

    last_date_query = session.query(Measurement.date).order_by(Measurement.id.desc()).limit(1)

    for item in last_date_query:
        last_date = dt.datetime.strptime(item.date, "%Y-%m-%d").date() - dt.timedelta(days=364)
        
    year_tobs = session.query(Measurement.date, func.avg(Measurement.tobs).label('Average')).\
        filter(Measurement.date >= last_date).\
        order_by(Measurement.date.asc()).\
        group_by(Measurement.date).all()
    
    all_tobs = list(year_tobs)

    return jsonify(all_tobs)
 

@app.route("/api/v1.0/<start>")

def temps(start):
    
   
    all_temps =  session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    temps_list = list(all_temps)

    return jsonify(temps_list)

@app.route("/api/v1.0/<start>/<end>")

def temp_range(start,end):
    
    temps_range = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temp_range_list = list(temps_range)

    return jsonify(temp_range_list)

if __name__ == '__main__':
    app.run(debug=True)