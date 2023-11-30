import sqlite3

global cursor

def connectDB():
    try:
        global cursor
        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect('sql.db')
        cursor = sqliteConnection.cursor()
        print('DB Init')
     
        # Write a query and execute it with cursor
        query = 'select sqlite_version();'
        cursor.execute(query)
     
        # Fetch and output result
        result = cursor.fetchall()
        print('SQLite Version is {}'.format(result))
     
        # Close the cursor
        
    except sqlite3.Error as error:
        print('Error occurred - ', error)
 
        
def getUser(tagnumber):
    
    global cursor
    # Connect to DB and create a cursor

    # Write a query and execute it with cursor
    query = 'select * from users where rfid_tag = ' + tagnumber
    cursor.execute(query)

    # Fetch and output result
    result = cursor.fetchall()

    return result
    print('User is {}'.format(result))

        # Close the cursor
            
         
          
