# DB
import sqlite3
conn = sqlite3.connect('usersdata.db', check_same_thread=False)
c = conn.cursor()

# Functions

def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT, email TEXT, preferences TEXT)')


def add_userdata(username,password, email, preferences):
	c.execute('INSERT INTO userstable(username,password, email, preferences) VALUES (?,?,?,?)',(username, password, email, preferences))
	conn.commit()

def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data

def user_preference(username,password):
	c.execute('SELECT preferences FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data

def update_user_preference(username,password,preferences):
    c.execute('Update userstable set preferences = ? WHERE username =? AND password = ?',(preferences,username,password))
    conn.commit()

def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data
