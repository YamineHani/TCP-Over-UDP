import mysql.connector

# Put your own information
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="letmein"
)

# Creating a cursor object using the cursor() method
cursor = mydb.cursor()
# Creating the student database
cursor.execute("CREATE DATABASE IF NOT EXISTS student")
cursor.execute("USE student")
cursor.execute("CREATE TABLE IF NOT EXISTS students (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255))")
#print("Database and table created successfully.")

#cursor.execute("INSERT INTO students (NAME) VALUES (%s)", ("Joe",))
#mydb.commit()

#cursor.execute("SELECT * FROM students")

#for x in cursor:
#    print(x)


# Function to handle HTTP GET requests
def handle_get_request(request):
    try:
        id = request.split(b'/')[-2].decode()
        cursor.execute("SELECT name FROM students WHERE id = %s", (id,))
        student = cursor.fetchone()
        if student:
            # Adjusting HTTP version and removing Connection header
            return b"HTTP/1.0 200 OK\r\n\r\nName: " + student[0].encode()
        else:
            # Adjusting HTTP version and removing Connection header
            return b"HTTP/1.0 404 Not Found\r\n\r\nStudent not found"
    except mysql.connector.Error as err:
        # Adjusting HTTP version and removing Connection header
        return b"HTTP/1.0 500 Internal Server Error\r\n\r\nDatabase error: {}".format(err)


# Function to handle HTTP POST requests
def handle_post_request(request):
    try:
        payload = request.split(b"\r\n\r\n")[-1]
        name = payload.decode()
        cursor.execute("INSERT INTO students (name) VALUES (%s)", (name,))
        mydb.commit()
        # Adjusting HTTP version and removing Connection header
        return b"HTTP/1.0 201 Created\r\n\r\nStudent added successfully"
    except mysql.connector.Error as err:
        # Adjusting HTTP version and removing Connection header
        return b"HTTP/1.0 500 Internal Server Error\r\n\r\nDatabase error: {}".format(err)

