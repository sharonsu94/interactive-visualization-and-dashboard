# import dependencies 
import pandas as pd
import numpy as np
from flask import Flask, render_template, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

# Flask Setup
app = Flask(__name__)

# Database Setup, sqlite
dbfile = "belly_button_biodiversity.sqlite"
engine = create_engine(f"sqlite:///{dbfile}")
Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
session = Session(engine)
Samples = Base.classes.samples
OTU = Base.classes.otu
Samples_Metadata = Base.classes.samples_metadata

# Flask Routes
# Homepage
@app.route('/')
def index():
    return render_template('index.html')

# List of Sample Names
@app.route('/names')
def names():
    samples_stmt = session.query(Samples).statement
    samples_df = pd.read_sql_query(samples_stmt, session.bind)
    samples_df.set_index("otu_id", inplace = True)
    return jsonify(list(samples_df.columns))

# List of OTU Descriptions 
@app.route('/otu')
def otu_descriptions():
    otu_stmt = session.query(OTU).statement
    otu_df = pd.read_sql_query(otu_stmt, session.bind)
    otu_df.set_index("otu_id", inplace=True)
    otu_descriptions = list(otu_df.lowest_taxonomic_unit_found)
    return jsonify(otu_descriptions)

# MetaData for a given sample
@app.route('/metadata/<sample>')
def metadata(sample):   
    
    # Grabbing input
    sample_id = int(sample[3:])  

    # Creating an empty dictionary for the data  
    sample_metadata = {}
    
    # Grab metadata table
    results = session.query(Samples_Metadata)
    
    # Loop through query & add info to dictionary
    for result in results:
        if (sample_id == result.SAMPLEID):
            sample_metadata["AGE"] = result.AGE
            sample_metadata["BBTYPE"] = result.BBTYPE
            sample_metadata["ETHNICITY"] = result.ETHNICITY
            sample_metadata["GENDER"] = result.GENDER
            sample_metadata["LOCATION"] = result.LOCATION
            sample_metadata["SAMPLEID"] = result.SAMPLEID
    return jsonify(sample_metadata)

# Weekly Washing Frequency
@app.route('/wfreq/<sample>')
def wfreq(sample):

    # Grabbing input
    sample_id = int(sample[3:])

    # Grab metadata table
    results = session.query(Samples_Metadata)

    #Loop through query & grab wfreq
    for result in results:
        if sample_id == result.SAMPLEID:
            wfreq = result.WFREQ
    return jsonify(wfreq)

# OTU IDs and SAMPLE Values 
@app.route("/samples/<sample>")
def samples(sample):

    # Create a sample query
    sample_query = "Samples." + sample

    # Create empty dictionary & lists
    sample_data = {}
    otu_ids = []
    sample_values = []

    # Grab info
    results = session.query(Samples.otu_id, sample_query).order_by(sample_query).desc()
    for result in results:
        otu_ids.append(result[0])
        sample_values.append(result[1])

    # Add info to dictionary
    sample_data = {
        "otu_ids": otu_ids,
        "sample_values": sample_values
    }
    return jsonify(sample_data)

# Initiate Flask app
if __name__ == "__main__":
    app.run(debug=True)
