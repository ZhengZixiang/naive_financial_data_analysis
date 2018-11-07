# -*- coding: utf-8 -*-
import MySQLdb as mdb
import pandas as pd

if __name__ == '__main__':
    # Connect to the MySQL instance
    db_host = 'localhost'
    db_user = 'root'
    db_pass = 'root'
    db_name = 'quant'
    con = mdb.connect(db_host, db_user, db_pass, db_name)

    # Select all of the historic Google adjusted close data
    sql = "SELECT dp.price_date, dp.adj_close_price FROM symbol AS sym " \
          "INNER JOIN daily_price AS dp ON dp.symbol_id = sym.id " \
          "WHERE sym.ticker = 'GOOG' ORDER BY dp.price_date ASC;"

    # Create a pandas dataframe from the SQL query
    google = pd.read_sql_query(sql, con=con, index_col='price_date')

    # Output the dataframe tial
    print(google.tail)
