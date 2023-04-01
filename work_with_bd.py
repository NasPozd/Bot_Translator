import mysql.connector
from mysql.connector import Error
from config import db_config 

def create_connection_mysql_db(db_host, user_name, user_password, db_name = None):
        connection_db = None
        try:
            connection_db = mysql.connector.connect(
                host = db_host,
                user = user_name,
                passwd = user_password,
                database = db_name
                )
                
        except Error as db_connection_error: print("Возникла ошибка: ", db_connection_error)
        return connection_db

def SELECT(select_name, table, where_status=False, where_column=None, where_data=None):
    """
    
    Parameters
    ----------
    select_name : Name selected column.
    table : Table name BD.
    where_status : Set where_status = True/False.
        if False : "SELECT select_name FROM table" 
        elif True : "SELECT select_name FROM table WHERE where_column='where_data'"
    where_column : always if True status.
    where_data : always if True status.

    Returns
    -------
    Data.

    """
    conn = create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"], db_config["mysql"]["pass"], db_config["mysql"]["database"])
    try:
        cursor = conn.cursor() 
        if where_status:
            unit = ("SELECT "+select_name+" FROM "+table+" WHERE "+str(where_column)+"='"+str(where_data)+"'")
            cursor.execute(unit)
            return cursor.fetchall() 
        
        else:
            unit = ("SELECT "+select_name+" FROM "+table)
            cursor.execute(unit)
            return cursor.fetchall()
        
    except Exception as error: print(error)
    finally:
        cursor.close()
        conn.close()

def UPDATE(table, **kwargs):
    """
    
    Parameters
    ----------
    table : Table name BD.
    **kwargs : Set where_status = True/False, 
        where_column = always if True status, 
        where_data = always if True status,
        column = data,
        name_column, data_column = key, data.
        
    Returns
    -------
    None.

    """
    conn = create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"], db_config["mysql"]["pass"], db_config["mysql"]["database"])
    try:
        cursor, data_str, count, name_column, data_column = conn.cursor(), "", 0, kwargs.get('name_column'), kwargs.get('data_column')
        if kwargs.get('where_status'):
            where_column, where_data = kwargs.pop('where_column'), kwargs.pop('where_data')
            kwargs.pop('where_status')
            if name_column != None and data_column != None: data_str = data_str+" "+str(name_column)+"='"+str(data_column)+"'"
            else:
                for set_name, set_data in kwargs.items():
                    if count == len(kwargs.items())-1: data_str = ("""%s %s="%s" """ % (data_str, str(set_name), str(set_data)))
                    else: data_str, count = ("""%s %s="%s",""" % (data_str, str(set_name), str(set_data))), count + 1
            unit = ("""UPDATE %s SET %s WHERE %s='%s'""" % (str(table), data_str, str(where_column), str(where_data)))
            cursor.execute(unit)
            conn.commit()    
        
        else:
            if name_column != None and data_column != None: data_str = data_str+" "+str(name_column)+"='"+str(data_column)+"'"
            else:
               for set_name, set_data in kwargs.items():
                   if count == len(kwargs.items())-1: data_str = data_str+" "+str(set_name)+"='"+str(set_data)+"'"
                   else: data_str, count = data_str+" "+str(set_name)+"='"+str(set_data)+"',", count + 1
            unit = ("UPDATE "+table+" SET"+data_str)
            cursor.execute(unit)
            conn.commit() 
    
    except Exception as error: print("update" ,error)
    finally:
        cursor.close()
        conn.close()

def INSERT(table, **kwargs):
    """

    Parameters
    ----------
    table : Table name BD.
    **kwargs : Columns = values

    Returns
    -------
    None.

    """
    conn = create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"], db_config["mysql"]["pass"], db_config["mysql"]["database"])
    try:
        cursor, columns, values, count = conn.cursor(), "", "", 0
        for column_name, column_value in kwargs.items():
            if count == len(kwargs.items())-1: columns, values = columns+str(column_name), values+"'"+str(column_value)+"'"
            else: columns, values, count = columns+str(column_name)+", ", values+"'"+str(column_value)+"', ", count + 1
        
        unit = ("INSERT INTO %s (%s) VALUES (%s)" % (str(table), str(columns), str(values)))
        cursor.execute(unit)
        conn.commit()
    
    except Exception as error: print(error)
    finally:
        cursor.close()
        conn.close()

def DELETE(table, **kwargs):
    """

    Parameters
    ----------
    table : Table name BD.
    **kwargs : Where_column = where_data

    Returns
    -------
    None.

    """
    conn = create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"], db_config["mysql"]["pass"], db_config["mysql"]["database"])
    try:
        cursor, data_str = conn.cursor(), ""
        for where_column, where_data in kwargs.items(): data_str = str(where_column)+"="+str(where_data)
        unit = ("DELETE FROM "+str(table)+" WHERE "+data_str)
        cursor.execute(unit)
        conn.commit()
    
    except Exception as error: print(error)
    finally:
        cursor.close()
        conn.close()

def SELECTS(table, **kwargs):
    """"
    
    Parameters
    ----------
    table : Table name BD.
    **kwargs : Set where_status = True/False, 
        where_column = always if True status, 
        where_data = always if True status,
        column = data
        
    Returns
    -------
    Data.

    """
    conn = create_connection_mysql_db(db_config["mysql"]["host"], db_config["mysql"]["user"], db_config["mysql"]["pass"], db_config["mysql"]["database"])
    try:
        cursor, data_str, count = conn.cursor(), "", 0
        if kwargs.get('where_status'):
            where_column, where_data = kwargs.pop('where_column'), kwargs.pop('where_data')
            for set_name in kwargs.items():
                if str(list(set_name)[0]) != "where_status":
                       if count == len(kwargs.items())-2: data_str = ("%s %s"  % (data_str, str(list(set_name)[0])))
                       else: data_str, count = ("%s %s," % (data_str, str(list(set_name)[0]))), count + 1
            unit = ("SELECT"+data_str+" FROM "+table+" WHERE "+str(where_column)+"='"+str(where_data)+"'")
            cursor.execute(unit)
            return cursor.fetchall() 
        
        else:
            for set_name in kwargs.items():
                if count == len(kwargs.items())-1: data_str = ("%s %s" % (data_str, str(list(set_name)[0])))
                else: data_str, count = ("%s %s," % (data_str, str(list(set_name)[0]))), count + 1
            unit = ("SELECT "+data_str+" FROM "+table)
            cursor.execute(unit)
            return cursor.fetchall()
        
    except Exception as error: print("selects", error)
    finally:
        cursor.close()
        conn.close()