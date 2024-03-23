import tkinter as tk
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
from face_processing import *
from datetime import datetime
from bdd import DatabaseHandler

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'biometrie',
}
# try:
conn = DatabaseHandler("localhost", "root", "", "biometrie")
cursor = conn.get_cursor()

query = """
    CREATE TABLE IF NOT EXISTS membres (
        id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        nom VARCHAR(255),
        prenom VARCHAR(255),
        email VARCHAR(255),
        FacialData LONGBLOB,
        lastAccess date
    )
"""
conn.execute_query(query)

print("Table créée avec succès et données insérées.")

# finally:
#     if 'conn' in locals():
#         conn.close()
#         print("Connexion à la base de données fermée.")


def getPath(imfile, ipath="images"):
    # Get the current directory of the script
    current_directory = os.path.dirname(os.path.realpath(__file__))
    # Get the parent directory (one level up)
    project_directory = os.path.dirname(current_directory)
    # Now you can use this to construct relative paths
    image_path = os.path.join(project_directory, ipath, imfile)
    return image_path

# Function to center a tkinter window
def center(win):
    # Centers a tkinter window
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()


# Main Application
class BiometryApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        # Initialisation bdd
        # DatabaseHandler("localhost", "user", "password", "mydatabase")        

        # Initializes the main application window
        tk.Tk.__init__(self, *args, **kwargs)

        global container
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}  # Dictionary to hold different frames
        self.title("Biometric Data Processing")
        self.geometry("800x600")
        center(self)
        self.resizable(False, False)

        # Create instances of different frames
        for F in (StartPage, Enroll, Auth, Enroll_Means, Auth_Means, Temporary):
            if F == Enroll_Means:
                image_path = getPath("face.jpg")
                frame = F(container, self, means=fr"{image_path}")
            else:
                frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_full_image(self, event, image, canva):
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        # image = self.image_original.size
        image_width, image_height = image.size #self.image_original.size

        # Calculate the scaling factor for both width and height
        scale_x = canvas_width / image_width
        scale_y = canvas_height / image_height

        # Choose the minimum scaling factor to ensure the entire image is visible
        scale_factor = min(scale_x, scale_y)

        # Calculate the new dimensions of the image
        new_width = int(image_width * scale_factor)
        new_height = int(image_height * scale_factor)

        # Resize the original image
        resized_image = image.resize((new_width, new_height))

        # Create a new PhotoImage object from the resized image
        resized_tk = ImageTk.PhotoImage(resized_image)

        # Configure the canvas to match the window size
        canva.config(width=canvas_width, height=canvas_height)

        # Delete previous image from the canvas (if any)
        canva.delete('all')

        # Display the resized image on the canvas
        canva.create_image(canvas_width // 2, canvas_height // 2, anchor='center', image=resized_tk)

        # Save a reference to avoid garbage collection
        canva.image = resized_tk

    def show_frame(self, cont):
        # Display the requested frame
        frame = self.frames[cont]
        frame.tkraise()

    def show_auth_frame(self):
        # Switch to the authentication frame
        frame = self.frames[Auth]
        frame.tkraise()

    def show_enroll_frame(self):
        # Switch to the enrollment frame
        frame = self.frames[Enroll]
        frame.tkraise()
    
    def show_enroll_means_frame(self, means):
        # Switch to the enrollment means frame and update means
        frame = self.frames[Enroll_Means]
        frame.update_means(means)
        frame.tkraise()

    def show_auth_means_frame(self, means):
        # Switch to the authentification means frame and update means
        frame = self.frames[Auth_Means]
        frame.update_means(means)
        frame.tkraise()


# Start Page Frame
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        # Start Page frame with options to enroll and authenticate
        tk.Frame.__init__(self, parent)
        # Get the current directory o
        # Relative path
        image_path = getPath("start_page.jpg")
        # Load the image and get its size
        self.image_original = Image.open(fr"{image_path}")

        image_width, image_height = self.image_original.size

        # Create a PhotoImage object from the image
        self.image_tk = ImageTk.PhotoImage(self.image_original)

        # Create a canvas and display the image
        self.canvas = tk.Canvas(self, width=image_width, height=image_height, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.grid(sticky='nsew')
        # self.canvas.grid(row=0, column=1, rowspan=3, sticky='nsew')
        self.canvas.create_image(0, 0, anchor='nw', image=self.image_tk)
        self.bind('<Configure>', lambda event, image = self.image_original, canva = self.canvas: controller.show_full_image(event, image, canva))

        # Add "Enroll_button" image
        enroll_image_path = fr'{getPath("enroll_page_button.jpg")}'  # Replace with the path to your "Enroll_button" image
        enroll_image = ImageTk.PhotoImage(file=enroll_image_path)
        enroll_label = tk.Label(self, image=enroll_image,  cursor="hand2")
        enroll_label.image = enroll_image  # Keep a reference to avoid garbage collection
        enroll_label.place(relx=0.15, rely=0.49)
        enroll_label.bind("<Button-1>", lambda event: controller.show_enroll_frame())

        # Add "Authentification_button" image
        auth_image_path = fr'{getPath("auth_page_button.jpg")}'  # Replace with the path to your "authious" image
        auth_image = ImageTk.PhotoImage(file=auth_image_path)
        auth_label = tk.Label(self, image=auth_image,  cursor="hand2")
        auth_label.image = auth_image  # Keep a reference to avoid garbage collection
        auth_label.place(relx=0.51, rely=0.49)
        auth_label.bind("<Button-1>", lambda event: controller.show_auth_frame())

# Second Window Frame (Page 1) - Enrollment Frame
class Enroll(tk.Frame):
    def __init__(self, parent, controller):
        # Enrollment frame with options for different biometric means
        tk.Frame.__init__(self, parent)
        image_path = getPath("enroll_page.jpg")
        # Load the image and get its size
        self.image_original = Image.open(fr"{image_path}")

        image_width, image_height = self.image_original.size

        # Create a PhotoImage object from the image
        self.image_tk = ImageTk.PhotoImage(self.image_original)

        # Create a canvas and display the image
        self.canvas = tk.Canvas(self, width=image_width, height=image_height, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.grid(sticky='nsew')
        self.canvas.create_image(0, 0, anchor='nw', image=self.image_tk)
        self.bind('<Configure>', lambda event, image = self.image_original, canva = self.canvas: controller.show_full_image(event, image, canva))

        # Add enrollment images for different means
        image_path = getPath("face.jpg")
        enroll_image_face = fr"{image_path}"
        enroll_face = ImageTk.PhotoImage(file=enroll_image_face)
        face_label = tk.Label(self, image=enroll_face, cursor="hand2")
        face_label.image = enroll_face
        face_label.place(relx=0.5, rely=0.6, anchor='center')
        face_label.bind("<Button-1>", lambda event: controller.show_enroll_means_frame(enroll_image_face))

        # Submit button, centered horizontally
        button = Button(self, text="Return", command=lambda: controller.show_frame(StartPage), bg="red", font=("Helvetica", 14, "bold"))
        button.place(relx=0.5, rely=0.8, anchor='center')


# Third Window Frame (Page 2) - Authentication Frame
class Auth(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        image_path = getPath("auth_page.jpg")
        # Load the image and get its size
        self.image_original = Image.open(fr"{image_path}")

        image_width, image_height = self.image_original.size

        # Create a PhotoImage object from the image
        self.image_tk = ImageTk.PhotoImage(self.image_original)

        # Create a canvas and display the image
        self.canvas = tk.Canvas(self, width=image_width, height=image_height, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.grid(sticky='nsew')
        self.canvas.create_image(0, 0, anchor='nw', image=self.image_tk)
        self.bind('<Configure>', lambda event, image = self.image_original, canva = self.canvas: controller.show_full_image(event, image, canva))

        # Add enrollment images for different means
        enroll_image_face = fr"{getPath('face.jpg')}"
        enroll_face = ImageTk.PhotoImage(file=enroll_image_face)
        face_label = tk.Label(self, image=enroll_face, cursor="hand2")
        face_label.image = enroll_face
        face_label.place(relx=0.5, rely=0.6, anchor='center')
        face_label.bind("<Button-1>", lambda event: controller.show_auth_means_frame(fr"{getPath('face.jpg')}"))

        # Submit button, centered horizontally
        button = Button(self, text="Return", command=lambda: controller.show_frame(StartPage), bg="red", font=("Helvetica", 14, "bold"))
        button.place(relx=0.5, rely=0.8, anchor='center')

    
# Frame for enrolling with specific means (e.g., face, fingerprint, iris)
class Enroll_Means(tk.Frame):
    mean = ""
    complete_name = "okay"
    def __init__(self, parent, controller, means):
        tk.Frame.__init__(self, parent)

        # Load the background image for the frame
        self.image_original = Image.open(fr"{getPath('enroll_means.jpg')}")

        # Get the size of the original image
        image_width, image_height = self.image_original.size

        # Create a PhotoImage object from the original image
        self.image_tk = ImageTk.PhotoImage(self.image_original)

        # Create a canvas to display the image
        self.canvas = tk.Canvas(self, width=image_width, height=image_height, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.grid(sticky='nsew')
        self.canvas.create_image(0, 0, anchor='nw', image=self.image_tk)

        # Bind the show_full_image method to the <Configure> event, so the image is resized on window resize
        self.bind('<Configure>', lambda event, image = self.image_original, canva = self.canvas: controller.show_full_image(event, image, canva))

        # Variables for user input
        self.Text_Area1 = StringVar()
        self.Text_Area2 = StringVar()
        self.Text_Area3 = StringVar()
    
        # Drawing text on the image
        draw = ImageDraw.Draw(self.image_original)
        point0 = 118,53
        point1 = 430,200
        point2 = 430,300
        point3 = 430,400
        color0 = "lightblue"
        color="cyan"

        draw.text(point0, "Enrolling you", color, font=ImageFont.load_default(20))

        # Entry widget for name
        draw.text(point1, "Enter your last name", color0, font=ImageFont.load_default(20))

        Input1 = Entry(self, textvariable=self.Text_Area1, font=("Helvetica", 12), width=30)
        Input1.place(relx=0.5, rely=0.4, anchor='center')

        # Entry widget for first name
        draw.text(point2, "Enter your first name", color0, font=ImageFont.load_default(20))

        Input2 = Entry(self, textvariable=self.Text_Area2, font=("Helvetica", 12), width=30)
        Input2.place(relx=0.5, rely=0.5, anchor='center')

        # Entry widget for email
        draw.text(point3, "Enter your email", color0, font=ImageFont.load_default(20))

        Input3 = Entry(self, textvariable=self.Text_Area3, font=("Helvetica", 12), width=30)
        Input3.place(relx=0.5, rely=0.6, anchor='center')

        # Label for displaying error message
        self.error_label = Label(self, fg="red", font=("Helvetica", 12, "italic"), bg="black")
        self.error_label.place(relx=0.5, rely=0.7, anchor='center')

        # Submit button
        button = Button(self, text="Submit", command= lambda: self.enroll_biometry(controller), bg="green", font=("Helvetica", 14, "bold"),)
        button.place(relx=0.55, rely=0.8, anchor='center')

        # Cancel button, centered horizontally
        button = Button(self, text="Return", command=lambda: controller.show_enroll_frame(), bg="red", font=("Helvetica", 14, "bold"),)
        button.place(relx=0.45, rely=0.8, anchor='center')

    def update_means(self, means):
        # Update the "Top" image based on the selected means
        enroll_image_path = means  # Replace with the path to your "Enroll_button" image
        enroll_image = ImageTk.PhotoImage(file=enroll_image_path)
        self.enroll_label = tk.Label(self, image=enroll_image)
        self.enroll_label.image = enroll_image  # Keep a reference to avoid garbage collection
        self.enroll_label.place(relx=0.1, rely=0.22)
        self.mean = means


    def enroll_biometry(self, controller):
        # recup des données
        nom = self.Text_Area1.get()
        prenom = self.Text_Area2.get()
        email = self.Text_Area3.get()

        # Check if both fields are filled
        if not nom or not prenom or not email:
            # Display an error message (you can customize this part)
            self.error_label.config(text="Please fill in all fields", fg="red", font=("Helvetica", 12, "bold"))
        else:
            # If both fields are filled, proceed with creating the new window
            self.error_label.config(text="")  # Clear the error message
            name = (nom.replace(' ', '') + "_" + prenom.replace(' ', '')) + ".jpg"
            filename = name.lower()

            if "face.jpg" in self.mean:
                face_en = FaceRecognition()
                face_en.enroll_face(filename)
                image_path = fr"{getPath('faces','biometries_data')}\{filename}"
                # Read the image file
                with open(image_path, 'rb') as image_file:
                    image_data = image_file.read()
                # Get the current date and time
                current_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(current_timestamp)
                conn.addUser(nom, prenom, email, image_data, current_timestamp) 
              


# Frame for authentication with specific means (e.g., face)
class Auth_Means(tk.Frame):
    mean = ""
    def __init__(self, parent, controller, means=fr"{getPath('iris.jpg')}"):
       
        tk.Frame.__init__(self, parent)

        # Load the background image for the frame
        self.image_original = Image.open(fr"{getPath('auth_means.jpg')}")

        # Get the size of the original image
        image_width, image_height = self.image_original.size

        # Create a PhotoImage object from the original image
        self.image_tk = ImageTk.PhotoImage(self.image_original)

        # Create a canvas to display the image
        self.canvas = tk.Canvas(self, width=image_width, height=image_height, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.grid(sticky='nsew')
        self.canvas.create_image(0, 0, anchor='nw', image=self.image_tk)
        self.bind('<Configure>', lambda event, image = self.image_original, canva = self.canvas: controller.show_full_image(event, image, canva))

        # Variables for user input
        # global Text_Area1, Text_Area2, error_label 
        self.Text_Area1 = StringVar()
        self.Text_Area2 = StringVar()
        self.Text_Area3 = StringVar()

        # Drawing text on the image
        draw = ImageDraw.Draw(self.image_original)
        point0 = 118,53
        point1 = 430,200
        point2 = 430,300
        point3 = 430,400
        color0 = "lightblue"
        color="cyan"

        draw.text(point0, "Enrolling you", color, font=ImageFont.load_default(20))


        # Entry widget for name
        draw.text(point1, "Enter your last name", color0, font=ImageFont.load_default(20))

        Input1 = Entry(self, textvariable=self.Text_Area1, font=("Helvetica", 12), width=30)
        Input1.place(relx=0.5, rely=0.4, anchor='center')

        # Entry widget for first name
        draw.text(point2, "Enter your first name", color0, font=ImageFont.load_default(20))

        Input2 = Entry(self, textvariable=self.Text_Area2, font=("Helvetica", 12), width=30)
        Input2.place(relx=0.5, rely=0.5, anchor='center')

        # Entry widget for email
        draw.text(point3, "Enter your email", color0, font=ImageFont.load_default(20))

        Input3 = Entry(self, textvariable=self.Text_Area3, font=("Helvetica", 12), width=30)
        Input3.place(relx=0.5, rely=0.6, anchor='center')

        # Messages d'erreur
        self.error_label = Label(self, fg="red", font=("Helvetica", 12, "italic"), bg="black")
        self.error_label.place(relx=0.5, rely=0.7, anchor='center')

        # Submit button
        button = Button(self, text="Submit", command=lambda: self.compare_biometry(controller), bg="green", font=("Helvetica", 14, "bold"),)
        button.place(relx=0.55, rely=0.8, anchor='center')

        # Cancel button
        button = Button(self, text="Return", command=lambda: controller.show_auth_frame(), bg="red", font=("Helvetica", 14, "bold"),)
        button.place(relx=0.45, rely=0.8, anchor='center')

    def update_means(self, means):
        # Update the "Top" image based on the selected means
        enroll_image_path = means  # Replace with the path to your "Enroll_button" image
        enroll_image = ImageTk.PhotoImage(file=enroll_image_path)
        enroll_label = tk.Label(self, image=enroll_image)
        enroll_label.image = enroll_image  # Keep a reference to avoid garbage collection
        enroll_label.place(relx=0.1, rely=0.22)
        self.mean = means

    def compare_biometry(self, controller):
        print('means_compare', self.mean)
        face_comp = FaceRecognition()
        face_comp.run_recognition()


# Frame for undone functionalities
class Temporary(tk.Frame):
    def __init__(self, parent, controller, means=fr"{getPath('maintenance.jpg')}"):
       
        tk.Frame.__init__(self, parent)

        # Load the background image for the frame
        self.image_original = Image.open(fr"{getPath('maintenance.jpg')}")

        # Get the size of the original image
        image_width, image_height = self.image_original.size

        # Create a PhotoImage object from the original image
        self.image_tk = ImageTk.PhotoImage(self.image_original)

        # Create a canvas to display the image
        self.canvas = tk.Canvas(self, width=image_width, height=image_height, bd=0, highlightthickness=0, relief='ridge')
        self.canvas.grid(sticky='nsew')
        self.canvas.create_image(0, 0, anchor='nw', image=self.image_tk)
        self.bind('<Configure>', lambda event, image = self.image_original, canva = self.canvas: controller.show_full_image(event, image, canva))

        # Drawing text on the image
        draw = ImageDraw.Draw(self.image_original)
        point0 = 10,40
        color="black"

        draw.text(point0, "Sorry, we're still working on this !", color, font=ImageFont.load_default(20))
        
        # Submit button, centered horizontally
        button = Button(self, text="Return", command=lambda: controller.show_frame(StartPage), bg="white", font=("Helvetica", 14, "bold"),)
        button.place(relx=0.5, rely=0.9, anchor='center')

# Driver Code
if __name__ == '__main__':
    app = BiometryApp()
    app.mainloop()

