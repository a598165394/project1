#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import random
import os
import time
import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
#
DATABASEURI = "postgresql://hd2337:YZFLPN@w4111db.eastus.cloudapp.azure.com/hd2337"
#DATABASEURI = "sqlite:///test.db"

#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
#engine.execute("""DROP TABLE IF EXISTS test;""")
#engine.execute("""SELECT * FROM Airport;""")
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
# id serial,
# name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
#engine.tables
#engine.schema

#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
#define a function for time formatting
def time_formating(int_value):
	#to format time into 24 hour hh:mm format
	value = int(int_value)
	hour = value / 60
        if hour < 10:
        	hour_str = "0"+str(hour)
        else:
                hour_str = str(hour)
        min = value % 60
        if min < 10:
                min_str = "0"+str(min)
        else:
                min_str = str(min)
        return hour_str + ":"+ min_str


#Reverse transform the input into proper time format for database
def reverse_time(hour, min):
    if hour[0] == "0":
        hour = hour[1:]
    if min[0] == "0":
        min = min[1:]
    return int(hour)*60 + int(min)

login_id =0;

@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print request.args


  #
  # example of a database query
  #
  
  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")


#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/comments')
def comments():
    cursor = g.conn.execute("SELECT user_id, post_date, post_time, content FROM Post_Comments")
    records = []
    for line in cursor:
        records.append(line)
    cursor.close()
    content = dict(data = records)
    return render_template("comments.html", **content)


#For Admin to manage_comments
@app.route('/manage_comments')
def manage_comments():
    cursor = g.conn.execute("SELECT user_id, post_date, post_time, content FROM Post_Comments;")
    records = []
    for line in cursor:
        records.append(line)
    cursor.close()
    content = dict(data = records)
    return render_template("manage_comments.html", **content)

#For Admin to delete comments
@app.route('/delete_comments', methods = ['POST'])
def delete_comments():
    content = request.form['content']
    q = "DELETE FROM Post_Comments WHERE content =%s"
   
    try:
        g.conn.execute(q, (content))
    except Exception:
        return render_template("exception.html")
    else:
        return redirect('/manage_comments')
      


@app.route('/list_flights_delay')
def list_flights_delay():
    cursor = g.conn.execute("SELECT time_cost,cause,flight_number,flight_date FROM Hasdelay")
    records = []
    for line in cursor:
        records.append(line)
    cursor.close()
    content = dict(data = records)
    return render_template("list_flights_delay.html",**content)


#list records from Flies table
@app.route('/list_flies')
def list_flies():
    cursor = g.conn.execute("SELECT * FROM Flies")
    names = []
    for record in cursor:
        names.append(record)  # can also be accessed using result[0]
    cursor.close()
    context = dict(data = names)
    return render_template("list_flies.html", **context)

#Add flights infor to Flies table
@app.route('/add_flies', methods = ['POST'])
def add_flies():
    flight_number = request.form['flight_number']
    airplane = request.form['model']
    flight_date = request.form['dep_date']
    args = (airplane, flight_number, flight_date)
    q = "INSERT INTO Flies VALUES (%s, %s, %s)"

    try:
        g.conn.execute(q, args)
    except Exception:
        return render_template("exception.html")
    else:
        return redirect('/list_flies')    



#Delete flights infor to Flies table #Default: ON DELETE NO ACTION
@app.route('/delete_flies', methods = ['POST'])
def delete_flies():
    flight_number = request.form['flight_number']
    airplane = request.form['model']
    flight_date = request.form['dep_date']
    args = (airplane, flight_number, flight_date)
    q = "DELETE FROM Flies WHERE model =%s AND flight_number =%s AND flight_date =%s"
    print q

    try:
        g.conn.execute(q, args)
    except Exception:
        return render_template("exception.html")
    else:
        return redirect('/list_flies')
    


@app.route('/list_airports')
def list_airports():
  cursor = g.conn.execute("SELECT airport_name FROM Airport")
  names = []
  for result in cursor:
    names.append(result['airport_name'])  # can also be accessed using result[0]
  cursor.close()
  context = dict(data = names)
  return render_template("list_airports.html", **context)


#Back to main menu
@app.route('/back_to_main')
def back_to_main():
    return render_template("main_menu.html")


#Back to admin menu
@app.route('/back_to_admin')
def back_to_admin():
    return render_template("admin_menu.html")


# Example of adding new data to the database
@app.route('/add_airport', methods=['POST'])
def add_airport():
  airport_name = request.form['airport_name']
  q = "INSERT INTO Airport VALUES (%s)"
  
  try:
      g.conn.execute(q, (airport_name))
  except Exception:
      return render_template("exception.html")
  else:
      return redirect('/list_airports')
  
  


# Example of adding new user - agency relationship
@app.route('/add_choose_relationship', methods=['POST'])
def add_choose_relationship():
  global login_id
  user_id = login_id
  agency = request.form['agency_name']
  q = "SELECT * FROM Agency WHERE agency_name =%s"
  cursor = g.conn.execute(q, (agency))
  #if it is a new agency, add into the new name into the agency table
  if cursor.rowcount == 0:
      g.conn.execute("INSERT INTO Agency VALUES (%s)",(agency))
  cursor.close()
  #without if statement above, the foreign key constraint may be violated
  args = (user_id, agency)
  q = "INSERT INTO Choose (user_id,agency_name) VALUES (%s, %s)"
  g.conn.execute(q, args)
  return render_template("thank_you.html")
  

#Admin function only
@app.route('/list_search_history')
def list_search_history():
    cursor = g.conn.execute("SELECT user_id,content FROM Search;")
    records = []
    for line in cursor:
        records.append(line)
    cursor.close()
    content = dict(data = records)
    return render_template("list_search_history.html",**content)



# add new flight delay information
@app.route('/add_flights_delay', methods=['POST'])
def add_flights_delay():
    #   print "line 263"
    try:
        time_cost = request.form['time_cost']
        cause = request.form['cause']
        flight_number = request.form['flight_number']
        flight_date = request.form['flight_date']
        args = (int(time_cost),cause,flight_number,flight_date)
        q = "INSERT INTO Hasdelay (time_cost,cause,flight_number,flight_date) VALUES(%s, %s, %s, %s);"
        g.conn.execute(q, args)
    except Exception:
        return render_template("exception.html")
    else:
        return redirect('/list_flights_delay')


    


#Adding new comments
@app.route('/add_comment', methods=['POST'])
def add_comment():
    global login_id
    user_id = login_id
    #LEFT OUT JOIN ACCOUNT AND POST_COMMENTS TABLE, IF USER HAVEN'T POST ANY COMMENTS, THEN COUNT = 0
    q = "SELECT A.user_id, max(P.comment_id) FROM Account A LEFT OUTER JOIN Post_Comments P ON A.user_id = P.user_id WHERE A.user_id =%s GROUP BY A.user_id"
    cursor = g.conn.execute(q,(user_id))
    for ids_with_counts in cursor:
        if(ids_with_counts[1]==None):
            print "line 579"
            count =0
        else:
            count = int(ids_with_counts[1])
#     print type(count)
        print "The count is %d\n" % count
        content = request.form['content']
        args = (user_id, count+1, repr(time.strftime("%Y/%m/%d")),repr(time.strftime("%H:%M:%S")), content)
        q = "INSERT INTO Post_Comments (user_id, comment_id, post_date, post_time, content) VALUES (%s, %s, %s, %s, %s)"
#     print q
        g.conn.execute(q, args)
        cursor.close()
        return redirect('/comments')
    #if nothing returned, means the user_id does not exist, return error
    cursor.close()
    return render_template("error.html")


# Search in the database
@app.route('/search')
def search():
    return render_template("search.html")

#Search by the Admin
@app.route('/manage_search')
def manage_search():
    return render_template("manage_search.html")
#login request
@app.route('/login', methods=['POST'])
def login():#Following is another way to check whether a user_id exists or not
   global login_id
   
   login_id = request.form['user_id']
   count = 0
   list_ids = g.conn.execute("SELECT user_id FROM Account;")
   for ids in list_ids:
	if int(login_id) == ids[0]:
	   list_ids.close()
   	   return render_template("main_menu.html")
   list_ids.close()
   return render_template("error.html")
#abort(401)
#this_is_never_executed()


#Logout from the system
@app.route('/logout')
def logout():
    global login_id
    login_id = 0
    return redirect('/')

#admin request
@app.route('/admin', methods=['POST'])
def admin():
    global login_id
    login_id = request.form['admin_id']
    q = "SELECT admin_id FROM Admin_ids WHERE admin_id =%s"
    cursor = g.conn.execute(q, (login_id))
    if cursor.rowcount == 0:
        return render_template("no_admin_right.html")
    else:
        return render_template("admin_menu.html")


#register request
@app.route('/register')
def register():
    list_ids = g.conn.execute("SELECT user_id FROM Account;")
    while True:
	count = 0
        #generating new id for first time user
        new_id = random.randint(100000, 99999999)
        for ids in list_ids: #check unique of new_id
            if new_id == ids[0]:
                count +=1
		break
        if count == 0:
	    break
    list_ids.close()    
    #insert new id into Account table
    g.conn.execute("INSERT INTO Account VALUES(%s)", new_id)
    #print new id to website
    ids = []
    ids.append(new_id) 
    print ids
    context = dict(data = ids)
    print context
    return render_template("register.html", **context)

#list_user_ids from Account table
@app.route('/list_ids')
def list_ids():
    cursor = g.conn.execute("SELECT user_id FROM Account")
    ids = []
    for result in cursor:
        ids.append(result['user_id'])  # can also be accessed using result[0]
    cursor.close()
    context = dict(data = ids)
    return render_template("list_ids.html", **context)

#list agencies from Agency table
@app.route('/list_agencies')
def list_agencies():
    cursor = g.conn.execute("SELECT agency_name FROM Agency;")
    names = []
    for result in cursor:
        names.append(result['agency_name'])  # can also be accessed using result[0]
    cursor.close()
    context = dict(data = names)
    return render_template("list_agencies.html", **context)


#list choose option between user and agency
@app.route('/list_user_choose')
def list_user_choose():
    cursor = g.conn.execute("SELECT * FROM Choose")
    names = []
    for record in cursor:
        names.append(record)
    cursor.close()
    context = dict(data = names)
    return render_template("list_user_choose.html",**context)


#list top 5 agency choosed by user 
@app.route('/list_popular_agency')
def list_popular_agency():
    cursor = g.conn.execute("SELECT C.agency_name, count(*) AS Chosen_times FROM Choose C GROUP BY C.agency_name ORDER BY Chosen_times DESC LIMIT 5;")
    names = []
    for record in cursor:
        names.append(record)
    cursor.close()
    context = dict(data = names)
    print "pass line 388"
    return render_template("list_popular_agency.html",**context)

#list top 5 agency choosed by user (for Admin)
@app.route('/manage_list_popular_agency')
def manage_list_popular_agency():
    cursor = g.conn.execute("SELECT C.agency_name, count(*) AS Chosen_times FROM Choose C GROUP BY C.agency_name ORDER BY Chosen_times DESC LIMIT 5;")
    names = []
    for record in cursor:
        names.append(record)
    cursor.close()
    context = dict(data = names)
    return render_template("manage_list_popular_agency.html",**context)
    
#add new agency into Agency table
@app.route('/add_agency', methods=['POST'])
def add_agency():
    try:
        agency_name = request.form['agency_name']
        g.conn.execute("INSERT INTO Agency VALUES (%s)", agency_name)    
    except Exception:
        return render_template("exception.html")
    else:
        return redirect('/list_agencies')
   
#Delete agency from Agency table
@app.route('/delete_agency', methods=['POST'])
def delete_agency():
    try:
        agency_name = request.form['agency_name']
        g.conn.execute("DELETE FROM Agency WHERE agency_name =%s", (agency_name))
    except Exception:
        return render_template("exception.html")
    else:
        return redirect('/list_agencies')

    

#list airplane type from AirplaneInfo table
@app.route('/list_airplanes')
def list_airplanes():
    cursor = g.conn.execute("SELECT * FROM AirplaneInfo")
    names = []
    for record in cursor:
        names.append(record)  # can also be accessed using result[0]
    cursor.close()
    context = dict(data = names)
    return render_template("list_airplanes.html", **context)

#add new AirplaneInfo into AirplaneInfo table
#
#Forbid add into AirplaneInfo Table due to check constraint
#
#
#@app.route('/add_airplane', methods=['POST'])
#def add_airplane():
#    manu = request.form['manufacturer']
#    model = request.form['model']
#    args = (repr(str(manu)), repr(str(model)))
    
#    g.conn.execute("INSERT INTO AirplaneInfo (manufacturer, model) VALUES (%s, %s);" % args)
#    return redirect('/list_airplanes')

#list FlightInfo from FlightInfo table
@app.route('/list_flights')
def list_flights():
    cursor = g.conn.execute("SELECT * FROM FlightInfo;")
    records = []
    for row in cursor:
        temp = []
        for value in row:
            if value != row[3] and value != row[4]:
                temp.append(value)
            else:
                temp.append(time_formating(value))   
        records.append(temp)
    cursor.close()
    content = dict(data = records)
    return render_template("flights_info.html", **content)

#Add flights to FlightInfo table
@app.route('/add_flights', methods = ['POST'])
def add_flights():
    try:
        flight_number = request.form['flight_number']
        airplane = request.form['airplane']
        flight_date = request.form['dep_date']
        dep_airport = request.form['dep_airport']
        dep_hour = request.form['dep_hour']
        dep_min = request.form['dep_min']
        dep_time = reverse_time(dep_hour, dep_min)
        arr_airport = request.form['arr_airport']
        arr_hour = request.form['arr_hour']
        arr_min = request.form['arr_min']
        arr_time = reverse_time(arr_hour, arr_min)
        args = (airplane, flight_number, flight_date, int(str(dep_time)), int(str(arr_time)), dep_airport, arr_airport)
        q = "INSERT INTO FlightInfo (airplane,flight_number,flight_date,dep_time,arr_time,dep_airport,arr_airport) VALUES (%s, %s, %s, %s, %s, %s, %s);"
        g.conn.execute(q,args)  
    except Exception:
        return render_template("exception.html")
    else:
        return redirect('/list_flights')
    


#User: search by date
@app.route('/search_date')
def search_date():
    return render_template("search_date.html")

@app.route('/search_by_link_to')
def search_by_link_to():
    
    q = "SELECT * FROM Link_to;"
    cursor = g.conn.execute(q)
    names = []
    for record in cursor:
        names.append(record)
    cursor.close()

    context = dict(data = names)
    print "608"
    return render_template("search_by_link_to.html",**context)


#Add flights infor to Flies table
@app.route('/add_link_to', methods = ['POST'])
def add_link_to():
    control = request.form['control']
    if control=='departure':
        control = 'out'
    elif control =='arrival':
        control = 'in'
    else:
        return render_template("exception.html")
    flight_date = request.form['flight_date']
    flight_number = request.form['flight_number']
    airport_name = request.form['airport_id']
    args = (control, flight_number, flight_date,airport_name)
    q = "INSERT INTO Link_to VALUES (%s, %s, %s, %s)"
    try:
        g.conn.execute(q,args)  
    except Exception:
        return render_template("exception.html")
    else:
        return redirect('/search_by_link_to')
    


#Delete flights infor to Flies table #Default: ON DELETE NO ACTION
@app.route('/delete_link_to', methods = ['POST'])
def delete_link_to():
    control = request.form['control']
    if control=='departure':
        control = 'out'
    elif control =='arrival':
        control = 'in'
    else:
        return render_template("exception.html")
    flight_date = request.form['flight_date']
    flight_number = request.form['flight_number']
    airport_name = request.form['airport_id']
    args = (control, flight_number, flight_date,airport_name)
    q = "DELETE FROM Link_to WHERE in_or_out =%s AND flight_number =%s AND flight_date =%s AND airport_name =%s"
    print q
    try:
        g.conn.execute(q,args)  
    except Exception:
        return render_template("exception.html")
    else:
        return redirect('/search_by_link_to')
    

#user: search by flight date
@app.route('/search_flight_date', methods = ['POST'])
def search_flight_date():
    global login_id
    user_id = login_id
    flight_date = request.form['flight_date']
    dep_airport = request.form['dep_airport']
    arr_airport = request.form['arr_airport']
    args = (dep_airport, arr_airport)
    count = 0
    q = "SELECT A.user_id, max(S.count) FROM Account A LEFT OUTER JOIN Search S ON A.user_id = S.user_id WHERE A.user_id =%s GROUP BY A.user_id"
    print "571"
    cursor = g.conn.execute(q,(user_id))
    print "573"
    for ids_with_counts in cursor:
        print "575"
        print count
        print ids_with_counts
        if(ids_with_counts[1]==None):
            print "line 579"
            count =0
        else:
            count = int(ids_with_counts[1])
        
        print "577"
    word =""
    cursor.close()
    print "574"
    #  print args
    q = "SELECT Hd.flight_number, AVG(Hd.time_cost) AS average_delay_time FROM Hasdelay Hd, FlightInfo F WHERE F.dep_airport = %s AND F.arr_airport = %s AND F.flight_number = Hd.flight_number GROUP BY Hd.flight_number ORDER BY AVG(Hd.time_cost);"
    
    try:
        cursor = g.conn.execute(q,args)
    except Exception:
          return render_template("exception_user.html")
    else:
        names = []
        for record in cursor:
            print "532"
            word+=str(record[0])
            print word
            word+=str(int(record[1]))
        #print "534"
            temp = [record[0]]
            temp.append(int(record[1])) #change average time cost as int
            names.append(temp)
        cursor.close()

        if names == []:
          return render_template("not_found.html")
        context = dict(data = names)
        print "538"
        print login_id
        search = (login_id, repr(word),count+1)
        q = "INSERT INTO Search VALUES (%s, %s,%s);"
        try:
            g.conn.execute(q, search)        
        except Exception:
            return render_template("exception_user.html")
        else:
            return render_template("search_date_result.html",**context)




#User: Search flight number for average delay time
@app.route('/search_flight')
def search_flight():
    return render_template('search_flight.html')



#Search in the database and display the search result of search_flight
@app.route('/search_flight_result', methods = ['POST'])
def search_flight_result():
    flight_number = request.form['flight_number']
    q = "SELECT H.flight_number, avg(H.time_cost) AS avg_cost,((COUNT(*) *100)/(SELECT COUNT(*) FROM Hasdelay hd2 WHERE hd2.flight_number = %s )) as percetnage FROM Hasdelay H WHERE H.flight_number = %s AND H.time_cost > 0 GROUP BY H.flight_number;"
    args = (flight_number,flight_number)
    cursor = g.conn.execute(q,args)
    names = []
    for record in cursor:
        temp = [record[0]]
        temp.append(int(record[1])) #change average time cost as int
        temp.append(record[2])
        names.append(temp)
    cursor.close();
    values = []
    if names == []:
        noLaterQ = "SELECT H.flight_number, AVG(H.time_cost) AS avg_cost FROM Hasdelay H WHERE H.flight_number = %s GROUP BY H.flight_number;"
        secCursor = g.conn.execute(noLaterQ,flight_number);
        for word in secCursor:
            temp = [word[0]]
            temp.append(int(word[1]))
            temp.append(int(0)) #change average time cost as int
            values.append(temp)
        secCursor.close()
        if(values==[]):
            return render_template("not_found.html")
        context = dict(data = values)
        return render_template("search_flight_result.html",**context)
    else:
        context = dict(data = names)
        return render_template("search_flight_result.html",**context)


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using

        python server.py

    Show the help text using

        python server.py --help

    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
