import customtkinter as ctk
from tkinter import ttk, messagebox
import Backend

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")

# Una sola ventana, con dos frames: el login y el panel
app = ctk.CTk()
app.title("Adopt Me - Acceso")
app.geometry("350x350")

frame_login = ctk.CTkFrame(app, fg_color="transparent")
frame_panel = ctk.CTkFrame(app, fg_color="transparent")


def iniciar_sesion():
    usuario = Backend.validar_login(entry_user.get(), entry_pass.get())
    if usuario:
        frame_login.pack_forget()
        app.geometry("1000x720")
        app.title("Adopt Me - Panel Principal | Hola, " + usuario['USERNAME'])
        construir_panel(usuario)
        frame_panel.pack(fill="both", expand=True)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")


# Login
ctk.CTkLabel(frame_login, text="🐾 Adopt Me", font=("Arial", 24, "bold"), text_color="#245743").pack(pady=30)
entry_user = ctk.CTkEntry(frame_login, placeholder_text="Tu usuario", width=250)
entry_user.pack(pady=10)
entry_pass = ctk.CTkEntry(frame_login, show="*", placeholder_text="Tu contraseña", width=250)
entry_pass.pack(pady=10)
ctk.CTkButton(frame_login, text="Iniciar sesión →", command=iniciar_sesion, width=250).pack(pady=20)
frame_login.pack(fill="both", expand=True)


#Panel
def construir_panel(usuario):

    #Empleados 
    ctk.CTkLabel(frame_panel, text="🐾 Directorio de Empleados", font=("Arial", 20, "bold"), text_color="#245743").pack(pady=10)

    columnas = ("ID", "Usuario", "Nombre", "Correo", "Teléfono", "CURP", "Dirección")
    tabla_users = ttk.Treeview(frame_panel, columns=columnas, show="headings", height=5)
    for col in columnas:
        tabla_users.heading(col, text=col)
        tabla_users.column(col, width=120)
    tabla_users.pack(fill="x", padx=20, pady=5)

    def llenar_usuarios():
        for fila in tabla_users.get_children():
            tabla_users.delete(fila)
        for u in Backend.obtener_usuarios(usuario['ID_ROL']):
            tabla_users.insert("", "end", values=(u['ID_USUARIO'], u['USERNAME'], u['NOMBRE'], u['CORREO'], u['TELEFONO'], u['CURP'], u['DIRECCION']))

    llenar_usuarios()

    # Solo el administrador ve los botones
    if usuario['ID_ROL'] == 1:

        # Este formulario sirve para agregar (datos=None) y para editar (datos=el usuario)
        def formulario_usuario(datos=None):
            ventana = ctk.CTkToplevel(app)
            ventana.geometry("400x650")
            ventana.grab_set()
            if datos:
                ventana.title("Editar usuario")
            else:
                ventana.title("Agregar usuario")

            # nombre del campo : columna de la base de datos
            campos = {"Usuario": "USERNAME", "Contraseña": None, "Nombre": "NOMBRE", "Correo": "CORREO",
                      "Teléfono": "TELEFONO", "CURP": "CURP", "Dirección": "DIRECCION"}
            entradas = {}
            for campo, columna in campos.items():
                ctk.CTkLabel(ventana, text=campo).pack(pady=(8, 0))
                entrada = ctk.CTkEntry(ventana)
                entrada.pack(padx=30, fill="x")
                if campo == "Contraseña":
                    entrada.configure(show="*")
                if datos and columna:
                    entrada.insert(0, datos[columna] or "")
                entradas[campo] = entrada

            if datos:
                entradas["Usuario"].configure(state="disabled") # el usuario no se cambia
                ctk.CTkLabel(ventana, text="(Contraseña vacía = no se cambia)", text_color="gray").pack()

            ctk.CTkLabel(ventana, text="Rol").pack(pady=(8, 0))
            rol = ctk.CTkOptionMenu(ventana, values=["Empleado", "Administrador"])
            rol.pack()
            if datos and datos['ID_ROL'] == 1:
                rol.set("Administrador")

            def guardar():
                if entradas["Usuario"].get() == "" or entradas["Nombre"].get() == "":
                    return messagebox.showwarning("Aviso", "Llena al menos usuario y nombre.")
                if not datos and entradas["Contraseña"].get() == "":
                    return messagebox.showwarning("Aviso", "Escribe una contraseña.")

                if rol.get() == "Administrador":
                    id_rol = 1
                else:
                    id_rol = 2

                try:
                    if datos:
                        Backend.editar_usuario(datos['ID_USUARIO'], entradas["Nombre"].get(), entradas["Correo"].get(),
                                               entradas["Teléfono"].get(), entradas["CURP"].get(), entradas["Dirección"].get(),
                                               id_rol, entradas["Contraseña"].get())
                    else:
                        Backend.agregar_usuario(entradas["Usuario"].get(), entradas["Contraseña"].get(), entradas["Nombre"].get(),
                                                entradas["Correo"].get(), entradas["Teléfono"].get(), entradas["CURP"].get(),
                                                entradas["Dirección"].get(), id_rol)
                    messagebox.showinfo("Éxito", "Usuario guardado.")
                    ventana.destroy()
                    llenar_usuarios()
                except Exception as error:
                    messagebox.showerror("Error", str(error))

            ctk.CTkButton(ventana, text="Guardar", command=guardar).pack(pady=20)

        def btn_editar():
            seleccion = tabla_users.selection()
            if not seleccion:
                return messagebox.showwarning("Aviso", "Selecciona un usuario de la tabla.")
            id_usr = tabla_users.item(seleccion)['values'][0]
            # Buscamos al usuario completo para llenar el formulario
            for u in Backend.obtener_usuarios(1):
                if u['ID_USUARIO'] == id_usr:
                    formulario_usuario(u)

        def btn_eliminar():
            seleccion = tabla_users.selection()
            if not seleccion:
                return messagebox.showwarning("Aviso", "Selecciona un usuario de la tabla.")
            id_usr = tabla_users.item(seleccion)['values'][0]
            if id_usr == usuario['ID_USUARIO']:
                return messagebox.showwarning("Aviso", "No puedes eliminarte a ti mismo.")
            if messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminarlo?"):
                if Backend.eliminar_usuario(id_usr):
                    llenar_usuarios()
                else:
                    messagebox.showerror("Error", "No se puede eliminar: tiene animales publicados.")

        frame_botones = ctk.CTkFrame(frame_panel, fg_color="transparent")
        frame_botones.pack(pady=5)
        ctk.CTkButton(frame_botones, text="＋ Agregar", command=formulario_usuario).pack(side="left", padx=10)
        ctk.CTkButton(frame_botones, text="✎ Editar", command=btn_editar, fg_color="#36785c").pack(side="left", padx=10)
        ctk.CTkButton(frame_botones, text="🗑 Eliminar", command=btn_eliminar, fg_color="#c84b48").pack(side="left", padx=10)

    #Animales
    ctk.CTkLabel(frame_panel, text="🐶 Animales del Refugio", font=("Arial", 20, "bold"), text_color="#245743").pack(pady=10)

    col_anim = ("ID", "Nombre", "Especie", "Sexo", "Edad (meses)", "Tamaño", "Estado", "Descripción")
    tabla_animales = ttk.Treeview(frame_panel, columns=col_anim, show="headings", height=6)
    for col in col_anim:
        tabla_animales.heading(col, text=col)
        tabla_animales.column(col, width=100)
    tabla_animales.column("Descripción", width=250)
    tabla_animales.pack(fill="x", padx=20, pady=5)

    def llenar_animales():
        for fila in tabla_animales.get_children():
            tabla_animales.delete(fila)
        for a in Backend.obtener_animales():
            tabla_animales.insert("", "end", values=(a['ID_ANIMAL'], a['NOMBRE'], a['ESPECIE'], a['SEXO'],
                                                     a['EDAD_MESES'], a['TAMANO'], a['ESTADO'], a['DESCRIPCION']))

    llenar_animales()

    def formulario_animal():
        ventana = ctk.CTkToplevel(app)
        ventana.title("Publicar animal")
        ventana.geometry("400x520")
        ventana.grab_set()

        nombre = ctk.CTkEntry(ventana, placeholder_text="Nombre")
        nombre.pack(pady=8, padx=30, fill="x")
        edad = ctk.CTkEntry(ventana, placeholder_text="Edad en meses")
        edad.pack(pady=8, padx=30, fill="x")
        especie = ctk.CTkOptionMenu(ventana, values=["PERRO", "GATO"])
        especie.pack(pady=8)
        sexo = ctk.CTkOptionMenu(ventana, values=["MACHO", "HEMBRA"])
        sexo.pack(pady=8)
        tamano = ctk.CTkOptionMenu(ventana, values=["PEQUENO", "MEDIANO"])
        tamano.pack(pady=8)
        estado = ctk.CTkOptionMenu(ventana, values=["DISPONIBLE", "ADOPTADO"])
        estado.pack(pady=8)
        descripcion = ctk.CTkEntry(ventana, placeholder_text="Descripción")
        descripcion.pack(pady=8, padx=30, fill="x")

        def guardar():
            if nombre.get() == "" or not edad.get().isdigit():
                return messagebox.showwarning("Aviso", "Escribe el nombre y la edad (solo número).")
            texto = descripcion.get()
            if texto == "":
                texto = "Sin descripción"
            try:
                Backend.agregar_animal(nombre.get(), especie.get(), edad.get(), sexo.get(),
                                       tamano.get(), texto, estado.get(), usuario['ID_USUARIO'])
                messagebox.showinfo("Éxito", "Animal publicado.")
                ventana.destroy()
                llenar_animales()
            except Exception as error:
                messagebox.showerror("Error", str(error))

        ctk.CTkButton(ventana, text="Publicar", command=guardar).pack(pady=20)

    ctk.CTkButton(frame_panel, text="＋ Publicar animal", command=formulario_animal, fg_color="#36785c").pack(pady=10)


app.mainloop()
