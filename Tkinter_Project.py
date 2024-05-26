import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os
global flag,countforforgotpass,noofcoordinates
flag,countforforgotpass=0,0
b=[]

def alert(title, message):
    show_method = getattr(tk.messagebox, 'show{}'.format('info'))
    show_method(title, message)

def getorigin(eventorigin):
    global x0,y0
    x0=eventorigin.x
    y0=eventorigin.y
    check(x0,y0)
#changing the coordinates when forgor password is clicked
def resetpoints(eventorigin):
    global x0,y0
    global coordinates
    x0=eventorigin.x
    y0=eventorigin.y
    coordinates.append([x0,y0])

def passwordchanged():
    global b,root1
    root1.destroy()
    b=coordinates[:len(coordinates)-1]
    writingfile("a.txt",b)
    alert('security', 'password has been changed')
def forgotpassword():
    global countforforgotpass,img
    if(countforforgotpass==0):    
        global coordinates,root1
        coordinates=[]
        root1 = tk.Toplevel()
        root1.title("setting password ")
        frame = tk.Frame(root1,width=100,height=100)
        frame.pack(fill=None,expand=False)
        panel = tk.Label(frame, image = img)
        panel.pack(side = "bottom", fill = "both", expand = "yes")
        button = tk.Button(root1, text="Done", fg="red",command=passwordchanged)
        button.pack(side=tk.BOTTOM)
        root1.bind("<Button 1>",resetpoints)
        countforforgotpass=countforforgotpass+1
    else:
        alert('security', 'you can only change the password once')

def setpassword():
    global countforforgotpass,img
    if(countforforgotpass==0):    
        global coordinates,root1
        coordinates=[]
        root1 = tk.Toplevel()
        root1.title("setting password ")
        frame = tk.Frame(root1,width=100,height=100)
        frame.pack(fill=None,expand=False)
        panel = tk.Label(frame, image = img)
        panel.pack(side = "bottom", fill = "both", expand = "yes")
        button = tk.Button(root1, text="Done", fg="red",command=passwordchanged)
        button.pack(side=tk.BOTTOM)
        root1.bind("<Button 1>",resetpoints)
        countforforgotpass=countforforgotpass+1
    else:
        alert('security', 'you can only change the password once')

    
def readingfile(filename):
    global noofcoordinates
    f=open(filename,"r")
    if (f.mode == 'r'):
        filecontents=f.read()
    f.close()
    filecontents=list((filecontents.strip()).split(" "))
    for i in range(0,len(filecontents),2): 
        b.append([int(filecontents[i]),int(filecontents[i+1])])
    noofcoordinates=len(b)


def writingfile(filename,temp):
    f=open(filename,"w+")
    t=[]
    for i in temp:
        t.append(i[0])
        t.append(i[1])
    for i in t:
        f.write("%d " %i)
    f.close()


#flag for sequencial access of the pattern
#consider the coordinates are like [[x,y],[x1,y1],[x2,y2]  ]
def check(x,y):
    global flag,b,noofcoordinates
    try:
        if(x<=(b[flag][0]+40) and x>=(b[flag][0]-40) and y<=(b[flag][1]+40) and y>=(b[flag][1]-40)):
            flag=flag+1
            if(flag==noofcoordinates):
                alert('security', 'password has been accepted')
                flag=0
        else:
            flag=0
    except:
        print()

def mainfun():
    global root,img
    root.destroy()
    readingfile("a.txt")
    root2 = tk.Tk()
    root2.title("enter password")
    frame = tk.Frame(root2,width=100,height=100)
    frame.pack(fill=None,expand=False)
    img = Image.open('download.jpg')
    img = img.resize((720,500), Image.ANTIALIAS)
    img = ImageTk.PhotoImage(img)
    panel = tk.Label(frame, image = img)
    panel.pack(side = "bottom", fill = "both", expand = "yes")
    button = tk.Button(root2, text="forgot password", fg="red",command=forgotpassword)
    button.pack(side=tk.BOTTOM)
    root2.bind("<Button 1>",getorigin)
    root2.mainloop()
    
root = tk.Tk()
root.title("Graphical security authentication application")
frame = tk.Frame(root,width=450,height=250)
global img
img = Image.open('download.jpg')
img = img.resize((720,500), Image.ANTIALIAS)
img = ImageTk.PhotoImage(img)
frame.pack(fill=None,expand=False)
button = tk.Button(root, text="              new user              ", fg="green",command=setpassword)
button1 = tk.Button(root, text="              existing user              ", fg="green",command=mainfun)
button.pack()
button1.pack()
frame1 = tk.Frame(root,width=450,height=250)
frame1.pack(fill=None,expand=False)