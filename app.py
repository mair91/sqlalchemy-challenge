import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

Meas = Base.classes.measurement
Stat = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """This is the world famous Surfs Up API"""
    f"------------------------------------<br/>"
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation  -- Precipitation data of the most active station for the last year<br/>"
        f"/api/v1.0/stations   -- A list of weather observation stations<br/>"
        f"/api/v1.0/tobs   -- Temperature data of the of the most active station for the last year<br/>"
        f"/api/v1.0/[startdate]   -- Minimum temperature, the average temperature, and the max temperature from the given date to today, date in format yyyy-mm-dd<br/>"
        f"/api/v1.0/[startdate]/[enddate]   -- Minimum temperature, the average temperature, and the max temperature between the given dates, date in format yyyy-mm-dd")


@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Stat.name).all()
    stationsAll = list(np.ravel(results))
    return jsonify(stationsAll)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    session = Session(engine)
    lastDate = (session.query(Meas.date)
                     .order_by(Meas.date.desc())
                     .first())
    lastDateNum = dt.datetime.strptime(list(np.ravel(lastDate))[0], '%Y-%m-%d')
    lastY = int(dt.datetime.strftime(lastDateNum, '%Y'))
    lastM = int(dt.datetime.strftime(lastDateNum, '%m'))
    lastD = int(dt.datetime.strftime(lastDateNum, '%d'))
    yearAgo = dt.date(lastY, lastM, lastD) - dt.timedelta(days=365)

    results = (session.query(Meas.date, Meas.prcp, Meas.station).order_by(Meas.date)
                      .filter(Meas.date > yearAgo)                      
                      .all())
    
    precipData = []
    for result in results:
        precipList = {result.date: result.prcp, "Station": result.station}
        precipData.append(precipList)
    return jsonify(precipData)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    lastDate = (session.query(Meas.date)
                     .order_by(Meas.date.desc())
                     .first())
    lastDateNum = dt.datetime.strptime(list(np.ravel(lastDate))[0], '%Y-%m-%d')
    lastY = int(dt.datetime.strftime(lastDateNum, '%Y'))
    lastM = int(dt.datetime.strftime(lastDateNum, '%m'))
    lastD = int(dt.datetime.strftime(lastDateNum, '%d'))
    yearAgo = dt.date(lastY, lastM, lastD) - dt.timedelta(days=365)
    
    
    results = (session.query(Meas.date, Meas.tobs, Meas.station).order_by(Meas.date)
                      .filter(Meas.date > yearAgo)
                      .all())

    tempData = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        tempData.append(tempDict)
    return jsonify(tempData)

@app.route("/api/v1.0/<startdate>")
def startdate(startdate):
    session = Session(engine)
    datalist = [Meas.date, func.min(Meas.tobs), func.avg(Meas.tobs), func.max(Meas.tobs)]
    results =  (session.query(*datalist).group_by(Meas.date)
                       .filter(func.strftime("%Y-%m-%d", Meas.date) >= startdate)
                       .all())
    dates = []                       
    for result in results:
        dateList = {}
        dateList["Date"] = result[0]
        dateList["Low Temp"] = result[1]
        dateList["Avg Temp"] = result[2]
        dateList["High Temp"] = result[3]
        dates.append(dateList)
    return jsonify(dates)

@app.route("/api/v1.0/<startdate>/<enddate>")
def startend(startdate, enddate):
    session = Session(engine)
    datalist = [Meas.date, func.min(Meas.tobs), func.avg(Meas.tobs), func.max(Meas.tobs)]
    results =  (session.query(*datalist).group_by(Meas.date)
                       .filter(func.strftime("%Y-%m-%d", Meas.date) >= startdate).filter(func.strftime("%Y-%m-%d", Meas.date) <= enddate)
                       .all())
    dates = []                       
    for result in results:
        dateList = {}
        dateList["Date"] = result[0]
        dateList["Low Temp"] = result[1]
        dateList["Avg Temp"] = result[2]
        dateList["High Temp"] = result[3]
        dates.append(dateList)
    return jsonify(dates)