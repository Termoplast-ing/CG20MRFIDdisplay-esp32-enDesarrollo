import tkinter as tk
from util.util_imagenes import leer_imagen
class TecladoWindow(tk.Toplevel):
    def __init__(self, master, target_entry=None):
        super().__init__(master)
        self.overrideredirect(True)
        self.target_entry = target_entry
        self.texto = tk.StringVar()
        self.texto.set(target_entry.get() if target_entry else "")
        self.withdraw()
        self.mayusculas = False 
        self.geometry("480x480")
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 480) // 2
        y = self.winfo_screenheight() - 400 - 50  # 50 píxeles desde abajo
        self.geometry(f"+{x}+{y}")
        self.deiconify()
        self.resizable(0, 0)
        self.configure(bg="black",highlightthickness=4,highlightbackground="black",highlightcolor="black")
        
        self.grab_set()

        # Frame principal con borde
        main_frame = tk.Frame(self, bg="#EF9480", bd=7, relief=tk.FLAT)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Carga las imágenes con rutas relativas correctas
        self.borrarIMG = tk.PhotoImage(file="imagenes/borrar.png")
        self.enterIMG = tk.PhotoImage(file="imagenes/enter.png")
        self.shiftIMG = tk.PhotoImage(file="imagenes/shift.png")
        self.espacioIMG = tk.PhotoImage(file="imagenes/espacio.png")
        self.cancelarIMG = leer_imagen('./imagenes/cancelar1.png', (100, 100))

        lineaTexto=tk.Frame(main_frame)
        linea1=tk.Frame(main_frame)
        linea2=tk.Frame(main_frame)
        linea3=tk.Frame(main_frame)
        linea4=tk.Frame(main_frame)
        linea5=tk.Frame(main_frame)
        linea6=tk.Frame(main_frame)
        linea7=tk.Frame(main_frame, bg="#EF9480")
        lineaTexto.pack(pady=10)
        linea1.pack()
        linea2.pack()
        linea3.pack()
        linea4.pack()
        linea5.pack()
        linea6.pack()
        linea7.pack(pady=5)
###
        def a1():          
            textoAux=self.texto.get()
            if self.mayusculas:
                self.texto.set(textoAux+"!")
            else:
                self.texto.set(textoAux+"1")
        def a2():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"@")
            else:
                self.texto.set(textoAux+"2")
        def a3():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"#")
            else:
                self.texto.set(textoAux+"3")
        def a4():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"$")
            else:
                self.texto.set(textoAux+"4")
        def a5():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"%")
            else:
                self.texto.set(textoAux+"5")
        def a6():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"^")
            else:
                self.texto.set(textoAux+"6")
        def a7():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"&")
            else:
                self.texto.set(textoAux+"7")
        def a8():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"*")
            else:
                self.texto.set(textoAux+"8")
        def a9():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"(")
            else:
                self.texto.set(textoAux+"9")
        def a0():            
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+")")
            else:
                self.texto.set(textoAux+"0")
        def q():           
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"Q")
            else:
                self.texto.set(textoAux+"q")
        def w():            
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"W")
            else:
                self.texto.set(textoAux+"w")
        def e():           
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"E")
            else:
                self.texto.set(textoAux+"e")
        def r():            
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"R")
            else:
                self.texto.set(textoAux+"r")
        def t():           
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"T")
            else:
                self.texto.set(textoAux+"t")
        def y():         
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"Y")
            else:
                self.texto.set(textoAux+"y")
        def u():           
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"U")
            else:
                self.texto.set(textoAux+"u")
        def i():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"I")
            else:
                self.texto.set(textoAux+"i")
        def o():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"O")
            else:
                self.texto.set(textoAux+"o")
        def p():            
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"P")
            else:
                self.texto.set(textoAux+"p")
        def a():            
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"A")
            else:
                self.texto.set(textoAux+"a")
        def s():           
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"S")
            else:
                self.texto.set(textoAux+"s")
        def d():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"D")
            else:
                self.texto.set(textoAux+"d")
        def f():
            textoAux=self.texto.get()           
            if(self.mayusculas):
                self.texto.set(textoAux+"F")
            else:
                self.texto.set(textoAux+"f")
        def g():    
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"G")
            else:
                self.texto.set(textoAux+"g")
        def h():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"H")
            else:
                self.texto.set(textoAux+"h")
        def j():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"J")
            else:
                self.texto.set(textoAux+"j")
        def k():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"K")
            else:
                self.texto.set(textoAux+"k")
        def l():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"L")
            else:
                self.texto.set(textoAux+"l")        
        def guion():                        
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"_")
            else:
                self.texto.set(textoAux+"-")
        def z():           
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"Z")
            else:
                self.texto.set(textoAux+"z")
        def x():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"X")
            else:
                self.texto.set(textoAux+"x")
        def c():           
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"C")
            else:
                self.texto.set(textoAux+"c")
        def v():           
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"V")
            else:
                self.texto.set(textoAux+"v")
        def b():       
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"B")
            else:
                self.texto.set(textoAux+"b")
        def n():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"N")
            else:
                self.texto.set(textoAux+"n")
        def m():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"M")
            else:
                self.texto.set(textoAux+"m")          
        def delete():            
            textoAux=self.texto.get()
            if(len(textoAux)>0):
                self.texto.set(textoAux[:-1])
        def espacio():
            textoAux=self.texto.get()
            self.texto.set(textoAux+" ")
        def enter():
            if self.target_entry:
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, self.texto.get())
            self.destroy()
            
        def menor():           
            textoAux=self.texto.get()
            self.texto.set(textoAux+"<")
        def mayor():           
            textoAux=self.texto.get()
            self.texto.set(textoAux+">")
        def corchete1():            
            textoAux=self.texto.get()
            self.texto.set(textoAux+"[")
        def corchete2():          
            textoAux=self.texto.get()
            self.texto.set(textoAux+"]")
        def llave1():         
            textoAux=self.texto.get()
            self.texto.set(textoAux+"{")
        def llave2():        
            textoAux=self.texto.get()
            self.texto.set(textoAux+"}")
        def barra1():         
            textoAux=self.texto.get()
            self.texto.set(textoAux+"\\")
        def virgulilla():          
            textoAux=self.texto.get()
            self.texto.set(textoAux+"~")
        def acento():      
            textoAux=self.texto.get()
            self.texto.set(textoAux+"`")
        def barra():           
            textoAux=self.texto.get()
            self.texto.set(textoAux+"/")
        def comillasIgual():         
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"=")
            else:
                self.texto.set(textoAux+'"')
        def apostrofrePregunta():           
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"?")
            else:
                self.texto.set(textoAux+"'")
        def masRecta():           
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+"|")
            else:
                self.texto.set(textoAux+"+")
        def comaPunto():           
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+",")
            else:
                self.texto.set(textoAux+".")
        def dospuntosPuntocoma():
            textoAux=self.texto.get()
            if(self.mayusculas):
                self.texto.set(textoAux+";")
            else:
                self.texto.set(textoAux+":")  
        ###
        def shift():
            self.mayusculas=not self.mayusculas
            if(self.mayusculas):
                btn_1.config(text="!")
                btn_2.config(text="@")
                btn_3.config(text="#")
                btn_4.config(text="$")
                btn_5.config(text="%")
                btn_6.config(text="^")
                btn_7.config(text="&")
                btn_8.config(text="*")
                btn_9.config(text="(")
                btn_0.config(text=")")
                btn_q.config(text="Q")
                btn_w.config(text="W")
                btn_e.config(text="E")
                btn_r.config(text="R")
                btn_t.config(text="T")
                btn_y.config(text="Y")
                btn_u.config(text="U")
                btn_i.config(text="I")
                btn_o.config(text="O")
                btn_p.config(text="P")
                btn_a.config(text="A")
                btn_s.config(text="S")
                btn_d.config(text="D")
                btn_f.config(text="F")
                btn_g.config(text="G")
                btn_h.config(text="H")
                btn_j.config(text="J")
                btn_k.config(text="K")
                btn_l.config(text="L")
                btn_guion.config(text="_")
                btn_z.config(text="Z")
                btn_x.config(text="X")
                btn_c.config(text="C")
                btn_v.config(text="V")
                btn_b.config(text="B")
                btn_n.config(text="N")
                btn_m.config(text="M")
                btn_apostrofrePregunta.config(text="?")
                btn_comillasIgual.config(text='=')
                btn_masRecta.config(text="|")
                btn_comaPunto.config(text=",")
                btn_dospuntosPuntocoma.config(text=";")
            else:
                btn_1.config(text="1")
                btn_2.config(text="2")
                btn_3.config(text="3")
                btn_4.config(text="4")
                btn_5.config(text="5")
                btn_6.config(text="6")
                btn_7.config(text="7")
                btn_8.config(text="8")
                btn_9.config(text="9")
                btn_0.config(text="0")
                btn_q.config(text="q")
                btn_w.config(text="w")
                btn_e.config(text="e")
                btn_r.config(text="r")
                btn_t.config(text="t")
                btn_y.config(text="y")
                btn_u.config(text="u")
                btn_i.config(text="i")
                btn_o.config(text="o")
                btn_p.config(text="p")
                btn_a.config(text="a")
                btn_s.config(text="s")
                btn_d.config(text="d")
                btn_f.config(text="f")
                btn_g.config(text="g")
                btn_h.config(text="h")
                btn_j.config(text="j")
                btn_k.config(text="k")
                btn_l.config(text="l")
                btn_guion.config(text="-")
                btn_z.config(text="z")
                btn_x.config(text="x")
                btn_c.config(text="c")
                btn_v.config(text="v")
                btn_b.config(text="b")
                btn_n.config(text="n")
                btn_m.config(text="m")
                btn_apostrofrePregunta.config(text="'")
                btn_comillasIgual.config(text='"')
                btn_masRecta.config(text="+")
                btn_comaPunto.config(text=".")
                btn_dospuntosPuntocoma.config(text=":")

        if(not self.mayusculas):
            label = tk.Label(lineaTexto, textvariable=self.texto, font=("Helvetica", 16, "bold"),  bg="#EF9480",fg="black",padx=10,pady=5,relief=tk.FLAT,highlightthickness=0)
            label.pack()
            btn_1 = tk.Button(linea1, text="1", command=a1,width=2,padx=8, pady=5, bg="lightblue")
            btn_2 = tk.Button(linea1, text="2", command=a2,width=2,padx=8, pady=5, bg="lightblue")
            btn_3 = tk.Button(linea1, text="3", command=a3,width=2,padx=8, pady=5, bg="lightblue")
            btn_4 = tk.Button(linea1, text="4", command=a4,width=2,padx=8, pady=5, bg="lightblue")
            btn_5 = tk.Button(linea1, text="5", command=a5,width=2,padx=8, pady=5, bg="lightblue")
            btn_6 = tk.Button(linea1, text="6", command=a6,width=2,padx=8, pady=5, bg="lightblue")
            btn_7 = tk.Button(linea1, text="7", command=a7,width=2,padx=8, pady=5, bg="lightblue")
            btn_8 = tk.Button(linea1, text="8", command=a8,width=2,padx=8, pady=5, bg="lightblue")
            btn_9 = tk.Button(linea1, text="9", command=a9,width=2,padx=8, pady=5, bg="lightblue")
            btn_0 = tk.Button(linea1, text="0", command=a0,width=2,padx=8, pady=5, bg="lightblue")
            ###
            btn_q = tk.Button(linea2, text="q", command=q,width=2,padx=8, pady=5, bg="lightblue")
            btn_w = tk.Button(linea2, text="w", command=w,width=2,padx=8, pady=5, bg="lightblue")
            btn_e = tk.Button(linea2, text="e", command=e,width=2,padx=8, pady=5, bg="lightblue")
            btn_r = tk.Button(linea2, text="r", command=r,width=2,padx=8, pady=5, bg="lightblue")
            btn_t = tk.Button(linea2, text="t", command=t,width=2,padx=8, pady=5, bg="lightblue")
            btn_y = tk.Button(linea2, text="y", command=y,width=2,padx=8, pady=5, bg="lightblue")
            btn_u = tk.Button(linea2, text="u", command=u,width=2,padx=8, pady=5, bg="lightblue")
            btn_i = tk.Button(linea2, text="i", command=i,width=2,padx=8, pady=5, bg="lightblue")
            btn_o = tk.Button(linea2, text="o", command=o,width=2,padx=8, pady=5, bg="lightblue")
            btn_p = tk.Button(linea2, text="p", command=p,width=2,padx=8, pady=5, bg="lightblue")
            ###
            btn_a = tk.Button(linea3, text="a", command=a,width=2,padx=8, pady=5, bg="lightblue")
            btn_s = tk.Button(linea3, text="s", command=s,width=2,padx=8, pady=5, bg="lightblue")
            btn_d = tk.Button(linea3, text="d", command=d,width=2,padx=8, pady=5, bg="lightblue")
            btn_f = tk.Button(linea3, text="f", command=f,width=2,padx=8, pady=5, bg="lightblue")
            btn_g = tk.Button(linea3, text="g", command=g,width=2,padx=8, pady=5, bg="lightblue")
            btn_h = tk.Button(linea3, text="h", command=h,width=2,padx=8, pady=5, bg="lightblue")
            btn_j = tk.Button(linea3, text="j", command=j,width=2,padx=8, pady=5, bg="lightblue")
            btn_k = tk.Button(linea3, text="k", command=k,width=2,padx=8, pady=5, bg="lightblue")
            btn_l = tk.Button(linea3, text="l", command=l,width=2,padx=8, pady=5, bg="lightblue")
            btn_guion = tk.Button(linea3, text="-", command=guion,width=2,padx=8, pady=5, bg="lightblue")
            ###
            btn_shift = tk.Button(linea4, image=self.shiftIMG, width=40,height=28, command=shift,padx=10, pady=5, bg="lightblue")
            btn_z = tk.Button(linea4, text="z", command=z,width=2,padx=10, pady=5, bg="lightblue")
            btn_x = tk.Button(linea4, text="x", command=x,width=2,padx=10, pady=5, bg="lightblue")
            btn_c = tk.Button(linea4, text="c", command=c,width=2,padx=10, pady=5, bg="lightblue")
            btn_v = tk.Button(linea4, text="v", command=v,width=2,padx=10, pady=5, bg="lightblue")
            btn_b = tk.Button(linea4, text="b", command=b,width=2,padx=10, pady=5, bg="lightblue")
            btn_n = tk.Button(linea4, text="n", command=n,width=2,padx=10, pady=5, bg="lightblue")
            btn_m = tk.Button(linea4, text="m", command=m,width=2,padx=10, pady=5, bg="lightblue")
            btn_delete = tk.Button(linea4, image=self.borrarIMG, width=40,height=28,command=delete,padx=11, pady=5, bg="grey")
            ###
            btn_menor = tk.Button(linea5, text="<", command=menor,width=2,padx=11, pady=5, bg="lightblue")
            btn_mayor = tk.Button(linea5, text=">", command=mayor,width=2,padx=10, pady=5, bg="lightblue")
            btn_corchete1 = tk.Button(linea5, text="[", command=corchete1,width=2,padx=10, pady=5, bg="lightblue")
            btn_corchete2 = tk.Button(linea5, text="]", command=corchete2,width=2,padx=10, pady=5, bg="lightblue")
            btn_llave1 = tk.Button(linea5, text="{", command=llave1,width=2,padx=10, pady=5, bg="lightblue")
            btn_llave2 = tk.Button(linea5, text="}", command=llave2,width=2,padx=10, pady=5, bg="lightblue")
            btn_barra1 = tk.Button(linea5, text="\\", command=barra1,width=2,padx=10, pady=5, bg="lightblue")
            btn_virgulilla = tk.Button(linea5, text="~", command=virgulilla,width=2,padx=10, pady=5, bg="lightblue")
            btn_acento = tk.Button(linea5, text="`", command=acento,width=2,padx=11, pady=5, bg="lightblue")
            ###
            btn_comillasIgual = tk.Button(linea6, text='"', command=comillasIgual,width=3,padx=9, pady=5, bg="lightblue")
            btn_apostrofrePregunta = tk.Button(linea6, text="'", command=apostrofrePregunta,width=2,padx=10, pady=5, bg="lightblue")
            btn_masRecta = tk.Button(linea6, text="+", command=masRecta,width=2,padx=10, pady=5, bg="lightblue")
            btn_espacio = tk.Button(linea6, image=self.espacioIMG, width=78,height=28, command=espacio,padx=10, pady=5, bg="lightblue")
            btn_comaPunto = tk.Button(linea6, text=".", command=comaPunto,width=2,padx=10, pady=5, bg="lightblue")
            btn_barra = tk.Button(linea6, text="/", command=barra,width=2,padx=10, pady=5, bg="lightblue")
            btn_dospuntosPuntocoma = tk.Button(linea6, text=":", command=dospuntosPuntocoma,width=2,padx=10, pady=5, bg="lightblue")
            btn_enter = tk.Button(linea6, image=self.enterIMG, width=39,height=28,command=enter,padx=10, pady=5, bg="grey")
            ###
            btn_1.pack(side="left", pady=0)
            btn_2.pack(side="left", pady=0)
            btn_3.pack(side="left", pady=0)
            btn_4.pack(side="left", pady=0)
            btn_5.pack(side="left", pady=0)
            btn_6.pack(side="left", pady=0)
            btn_7.pack(side="left", pady=0)
            btn_8.pack(side="left", pady=0)
            btn_9.pack(side="left", pady=0)
            btn_0.pack(side="left", pady=0)
            ###
            btn_q.pack(side="left", pady=0)
            btn_w.pack(side="left", pady=0)
            btn_e.pack(side="left", pady=0)
            btn_r.pack(side="left", pady=0)
            btn_t.pack(side="left", pady=0)
            btn_y.pack(side="left", pady=0)
            btn_u.pack(side="left", pady=0)
            btn_i.pack(side="left", pady=0)
            btn_o.pack(side="left", pady=0)
            btn_p.pack(side="left", pady=0)
            ###
            btn_a.pack(side="left", pady=0)
            btn_s.pack(side="left", pady=0)
            btn_d.pack(side="left", pady=0)
            btn_f.pack(side="left", pady=0)
            btn_g.pack(side="left", pady=0)
            btn_h.pack(side="left", pady=0)
            btn_j.pack(side="left", pady=0)
            btn_k.pack(side="left", pady=0)
            btn_l.pack(side="left", pady=0)
            btn_guion.pack(side="left", pady=0)
            ###
            btn_shift.pack(side="left", pady=0)
            btn_z.pack(side="left", pady=0)
            btn_x.pack(side="left", pady=0)
            btn_c.pack(side="left", pady=0)
            btn_v.pack(side="left", pady=0)
            btn_b.pack(side="left", pady=0)
            btn_n.pack(side="left", pady=0)
            btn_m.pack(side="left", pady=0)
            btn_delete.pack(side="left", pady=0)
            ###
            btn_menor.pack(side="left", pady=0)
            btn_mayor.pack(side="left", pady=0)
            btn_corchete1.pack(side="left", pady=0)
            btn_corchete2.pack(side="left", pady=0)
            btn_llave1.pack(side="left", pady=0)
            btn_llave2.pack(side="left", pady=0)
            btn_barra1.pack(side="left", pady=0)
            btn_virgulilla.pack(side="left", pady=0)
            btn_acento.pack(side="left", pady=0)
            ###
            btn_comillasIgual.pack(side="left", pady=0)
            btn_apostrofrePregunta.pack(side="left", pady=0)
            btn_masRecta.pack(side="left", pady=0)
            btn_espacio.pack(side="left", pady=0)
            btn_comaPunto.pack(side="left", pady=0)
            btn_barra.pack(side="left", pady=0)
            btn_dospuntosPuntocoma.pack(side="left", pady=0)
            btn_enter.pack(side="left", pady=0)
                    # Función para cancelar (cierra la ventana sin guardar cambios)
        def cancelar():
            self.destroy()

        # Botón de cancelar con mismo estilo que el botón de menú
        btn_cancelar = tk.Button(
            linea7,
            text="Cancelar",  # Texto del botón
            font=("Helvetica", 20),  # Misma fuente y tamaño
            command=cancelar,
            bg="red",  # Mismo color de fondo
            fg="#ffffff",  # Texto blanco
            activebackground="#FF6347",  # Color al presionar
            highlightbackground="#EF9480",  # Color del resaltado
            highlightcolor="#FF6347",  # Color del borde de enfoque
            bd=9,  # Grosor del borde (igual que el botón menú)
            relief="raised"  # Estilo del relieve
        )

        # Configuración de eventos hover (igual que el menú)
        def on_enter_cancelar(event):
            event.widget.config(bg="red")  # Mantener rojo al pasar el mouse

        def on_leave_cancelar(event):
            event.widget.config(bg="red")  # Mantener rojo al salir el mouse

        btn_cancelar.bind("<Enter>", on_enter_cancelar)
        btn_cancelar.bind("<Leave>", on_leave_cancelar)

        # Posicionamiento (ajustado a tu layout)
        btn_cancelar.pack(side="top", pady=20)
