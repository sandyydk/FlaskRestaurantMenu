from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from database_setup import Restaurant, MenuItem, Base


def initializeDatabase():
    global engine, session
    engine = create_engine('sqlite:///restaurantmenu.db')
    Base.metadata.create_all(engine)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()


class webserverHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]

                myRestaurantQuery = session.query(Restaurant).filter_by(
                    id=restaurantIDPath).one()
                if myRestaurantQuery:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1>Are you sure you want to delete %s?" % myRestaurantQuery.name
                    output += "<form method='POST' enctype = 'multipart/form-data' action = '/restaurants/%s/delete'>" % restaurantIDPath
                    output += "<input type = 'submit' value = 'Delete'>"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)

            if self.path.endswith("/edit"):
                restaurantId = self.path.split("/")[2]

                restaurant = session.query(Restaurant).filter_by(id=restaurantId)

                if restaurant != []:
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>" 
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" %restaurantId
                    output += "<input type='text' name='restaurantnewname' >"
                    output += "<input type='submit' value='Rename' >"
                    output += "</form>"
                    output += "</body></html>"
                    self.wfile.write(output)

            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                output = ""
                output += "<html><body>" 
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'> <input type='text' name='restaurantname' >"
                output += "<input type='submit' value='Create' >"
                output += "</body></html>"
                self.wfile.write(output)

            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type','text/html')
                self.end_headers()
                output = ""
                restaurants = session.query(Restaurant).all()
                output += "<html><body>" 
                output += "<a href='/restaurants/new'><h2>Add New Restaurant</h2></a>"
                for restaurant in restaurants:
                    print restaurant.name
                    output += restaurant.name
                    output += " <a href='/restaurants/%s/edit'>edit</a> " %restaurant.id
                    output += " <a href='/restaurants/%s/delete'>delete</a> " %restaurant.id
                    output += "<br>"
                output += "</body></html>"
                self.wfile.write(output)

        except IOError:        
            self.send_error(404, "File Not Found %s" %self.path)


    def do_POST(self):
        try:
            if self.path.endswith("/delete"):
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(
                    id=restaurantIDPath).one()
                if myRestaurantQuery:
                    session.delete(myRestaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('restaurantnewname')
                    restaurantIDPath = self.path.split("/")[2]

                    myRestaurantQuery = session.query(Restaurant).filter_by(
                        id=restaurantIDPath).one()
                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = messagecontent[0]
                        session.add(myRestaurantQuery)
                        session.commit()
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()


            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile,pdict)
                messageContent = fields.get('restaurantname')

                newRestaurant = Restaurant(name=messageContent[0])
                session.add(newRestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Content-type','text/html')
                self.send_header('Location','/restaurants')
                self.end_headers()

        except:
            pass     

def main():
    try:
        initializeDatabase()
        port = 8080
        server = HTTPServer(('',port),webserverHandler)
        print "Web server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print "User terminated the server"
        server.socket.close()

if __name__ == '__main__':
    main()