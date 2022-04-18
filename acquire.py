import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from env import get_db_url
from pydataset import data
import os
import requests

def show_codeup_dbs():
    url = get_db_url('employees')
    codeup_dbs = pd.read_sql('SHOW DATABASES', url)
    print('List of Codeup DBs:\n')
    return codeup_dbs


def get_props_2017():
    '''
    Returns a DataFrame composed of selected data from the properties_2017 table in the zillow database on
    Codeup's SQL server
    '''
    filename = 'props_2017.csv'
    if os.path.exists(filename):
        print('Reading from CSV file...')
        return pd.read_csv(filename)
    query = """
    SELECT 
    bedroomcnt, 
    bathroomcnt, 
    roomcnt,
    numberofstories,
    fireplaceflag,
    poolcnt, 
    buildingqualitytypeid, 
    calculatedfinishedsquarefeet, 
    lotsizesquarefeet,
    latitude,
    longitude,
    structuretaxvaluedollarcnt,
    landtaxvaluedollarcnt,
    taxvaluedollarcnt, 
    yearbuilt, 
    taxamount, 
    fips, 
    logerror 
    FROM properties_2017 prop
    JOIN predictions_2017 pred ON pred.id = prop.id
    JOIN propertylandusetype land ON land.propertylandusetypeid = prop.propertylandusetypeid
    WHERE (
    prop.latitude IS NOT NULL
    AND
    prop.longitude IS NOT NULL
    AND 
    pred.transactiondate LIKE '2017%%'
    );
    """
    print('Getting a fresh copy from SQL database...')
    url = get_db_url('zillow')
    props_2017 = pd.read_sql(query, url)
    print('Copying to CSV...')
    props_2017.to_csv(filename, index=False)
    return props_2017

def zillow_cluster_f():
    '''
    Returns a dataframe from a SQL query of the Zillow data on Codeup's MySQL server
    '''
    filename = 'zillow_cluster_f.csv'
    if os.path.exists(filename):
        print('Reading from CSV file...')
        return pd.read_csv(filename)
    query = '''
    SELECT *
    FROM properties_2017 prop
    JOIN (
        SELECT parcelid, MAX(transactiondate) AS max_transactiondate 
        FROM predictions_2017
        GROUPBY parcelid) pred ON pred.parcelid = prop.parcelid
    LEFT JOIN airconditioningtype ac ON ac.airconditioningtypeid = prop.airconditioningtypeid
    LEFT JOIN architecturalstyletype arch ON arch.architecturalstyletypeid = prop.architecturalstyletypeid
    LEFT JOIN buildingclasstype build ON build.buildingclasstypeid = prop.buildingclasstypeid
    LEFT JOIN heatingorsystemtype heat ON heat.heatingorsystemtypeid = prop.heatingorsystemtypeid
    LEFT JOIN propertylandusetype land on land.propertylandusetypeid = prop.propertylandusetypeid
    LEFT JOIN storytype st ON st.storytypeid = prop.storytypeid
    LEFT JOIN typeconstructiontype con ON con.typeconstructiontypeid = prop.typeconstructiontypeid
    WHERE (
    prop.latitude IS NOT NULL
    AND
    prop.longitude IS NOT NULL
    AND
    pred.transactiondate LIKE '2017%%'
    )'''
    print('Getting a fresh copy from SQL database...')
    url = get_db_url('zillow')
    zillow_cluster_f = pd.read_sql(query, url)
    print('Copying to CSV...')
    zillow_cluster_f.to_csv(filename, index=False)
    return zillow_cluster_f


def zachs_zillow_pull():
    '''
    Returns a dataframe from a SQL query (written by Zach G.) of the Zillow data on 
    Codeup's MySQL server
    '''
    filename = 'zillow_clustering.csv'
    if os.path.exists(filename):
        print('Reading from CSV file...')
        return pd.read_csv(filename)
    query = '''
    SELECT
	prop.*,
    predictions_2017.logerror,
    predictions_2017.transactiondate,
    ac.airconditioningdesc,
    arch.architecturalstyledesc,
    build.buildingclassdesc,
    heat.heatingorsystemdesc,
    land.propertylandusedesc,
    story.storydesc,
    con.typeconstructiondesc
    FROM properties_2017 prop
    JOIN (
    SELECT parcelid, MAX(transactiondate) AS max_transactiondate
    FROM predictions_2017
    GROUP BY parcelid
    ) pred USING(parcelid)
    JOIN predictions_2017 ON pred.parcelid = predictions_2017.parcelid
                        AND pred.max_transactiondate = predictions_2017.transactiondate
    LEFT JOIN airconditioningtype ac USING (airconditioningtypeid)
    LEFT JOIN architecturalstyletype arch USING (architecturalstyletypeid)
    LEFT JOIN buildingclasstype build USING (buildingclasstypeid)
    LEFT JOIN heatingorsystemtype heat USING (heatingorsystemtypeid)
    LEFT JOIN propertylandusetype land USING (propertylandusetypeid)
    LEFT JOIN storytype story USING (storytypeid)
    LEFT JOIN typeconstructiontype con USING (typeconstructiontypeid)
    WHERE prop.latitude IS NOT NULL
    AND prop.longitude IS NOT NULL
    AND transactiondate <= '2017-12-31';
    '''
    print('Getting a fresh copy from SQL database...')
    url = get_db_url('zillow')
    zillow_clustering = pd.read_sql(query, url)
    print('Copying to CSV...')
    zillow_clustering.to_csv(filename, index=False)
    return zillow_clustering

def get_items_data():
    filename= 'items.csv'
    if os.path.exists(filename):
        print('Reading from CSV file...')
        return pd.read_csv(filename)

    domain = 'https://api.data.codeup.com'
    endpoint = '/api/v1/items'
    items= []

    #For each page --  until next page is None
    while endpoint is not None:
        url = domain + endpoint
        response = requests.get(url)
        data = response.json()

        print(f'\rGetting page {data["payload"]["page"]} of {data["payload"]["max_page"]}: {url}', end='')

        items.extend(data['payload']['items'])
        endpoint = data['payload']['next_page']
    items = pd.DataFrame(items)
    items.to_csv(filename, index=False)
    return items

def get_stores_data():
    filename= 'stores.csv'
    if os.path.exists(filename):
        print('Reading from CSV file...')
        return pd.read_csv(filename)
    
    domain = 'https://api.data.codeup.com'
    endpoint = '/api/v1/stores'
    url = domain + endpoint
    response = requests.get(url)
    data = response.json()
    stores = data['payload']['stores']
    stores = pd.DataFrame(stores)
    stores.to_csv(filename, index=False)
    return stores

def get_sales_data():
    filename= 'stores.csv'
    if os.path.exists(filename):
        print('Reading from CSV file...')
        return pd.read_csv(filename)
    
    domain = 'https://api.data.codeup.com'
    endpoint = '/api/v1/sales'
    sales = []

    url = domain + endpoint
    response = requests.get(url)
    data = response.json()
    while endpoint is not None:
        url = domain + endpoint
        response = requests.get(url)
        data = response.json()

        print(f'\rGetting page {data["payload"]["page"]} of {data["payload"]["max_page"]}: {url}', end='')

        sales.extend(data['payload']['sales'])
        endpoint = data['payload']['next_page']
    sales = pd.DataFrame(sales)
    sales.to_csv(filename, index=False)
    return sales

def get_sales_items_stores():
    filename = 'sales_items_stores.csv'
    if os.path.exists(filename):
        print('Reading from CSV file...')
        return pd.read_csv(filename)

    sales = pd.read_csv('sales.csv')
    sales = sales.rename(columns= {'item': 'item_id', 'store': 'store_id'})
    items = pd.read_csv('items.csv')
    stores = pd.read_csv('stores.csv')
    stores = stores.rename(columns= {'store': 'store_id'})
    
    sales_items_stores = pd.merge(sales, items, how='left', on='item_id')
    sales_items_stores = pd.merge(sales_items_stores, stores, how='left', on='store_id')
    sales_items_stores.to_csv(filename, index=False)
    return sales_items_stores

def get_opsd():
    filename = 'opsd.csv'
    if os.path.exists(filename):
        print('Reading from CSV file...')
        return pd.read_csv(filename)

    df = pd.read_csv('https://raw.githubusercontent.com/jenfly/opsd/master/opsd_germany_daily.csv')
    df.to_csv(filename)
    return df



    
