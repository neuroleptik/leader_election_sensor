#fichier de test projet 903
import threading
import socket
import time
import random


# Fonction d'un thread qui représente un capteur
def thread_function(identifiant,groupe):
    capteur1 = Capteur(groupe,identifiant)
    capteur1.display()
    capteur1.connect()
    # on regarde si c'est a nous d'envoyer le nombre sinon on ecoute
    while(capteur1.finex != True):
        if (capteur1.mon_tour):
            time.sleep(1) # on attend une seconde que tout le monde écoute
            capteur1.envoyer_aleatoire()
        else:
            # tant que c'est pas notre tour d'envoyer on ecoute pour l"election
      
            capteur1.recevoir_aleatoire()
       
    print("Phase d'éléction terminé pour le groupe "+str(groupe))
    time.sleep(3)
    while(1):
        if(capteur1.id_leader == capteur1.port):
            print("je suis le leader")
            print(capteur1.id_leader)
            print(capteur1.port)
            capteur1.recevoir_des_esclaves()
        else:
      
            capteur1.envoyer_au_leader()



#création de class d'un capteur (simulation)
class Capteur:
    def __init__(self,group,identifiant):
        self.group = group
        self.identifiant = identifiant
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = plage_port+(self.group*nb_capteurs_par_groupe)+self.identifiant
        self.id_leader = self.port
        self.nombre_election = random.randint(0,1000000)
        self.nombre_temp = self.nombre_election
        self.finex = False
        if (((self.group*nb_capteurs_par_groupe) - (self.group*nb_capteurs_par_groupe+self.identifiant)) == 0):
            self.mon_tour = True # a mon tour d'envoyer le nombre sinon j'ecoute le nombre
        else:
            self.mon_tour = False
    # fonction d'affichage d'un capteur
    def display(self):
        print("Capteur numéro : "+str(self.identifiant)+", Groupe "+str(self.group)+", Port : "+str(self.port))
    #fonction qui va initialiser le socket d'écoute
    def connect(self):
        self.socket.bind(('localhost', self.port))
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(5)
        self.socket.listen(30)
        #print("Socket bind au port : "+str(self.group*10+self.identifiant))
    
    # fonction qui va servir à envoyer un nombre aléatoire pendant l'éléction de leader 
    def envoyer_aleatoire(self):
        #ameliorer si le nombre recu est > au nombre deja généré
        for i in range(nb_capteurs_par_groupe):
            port_envoie = plage_port+self.group*nb_capteurs_par_groupe+i
            
            # envoie le numero à tout le groupe sauf à moi même
            if port_envoie != self.port:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(("localhost",port_envoie))
                s.send((str(self.port)+","+str(self.nombre_election)).encode('utf-8'))
                s.close()
        # une fois que j'envoie mon numéro a tout le monde, ce n'est plus mon tour
        self.mon_tour = False

     # fonction qui va servir à écouter pour la réception d'un nombre aléatoire pendant l'éléction de leader   
    def recevoir_aleatoire(self):
        # on accepte la connection et on reçoit les infos 
        try:
            (clientsocket, address) = self.socket.accept()
            recu = clientsocket.recv(24)
            str_finale = recu.decode()
            li = list(str_finale.split(",")) 
            print("reçu : "+str(str_finale))
            port_finale = int(li[0])
            int_finale = int(li[1])
        # on compare la valeur recu avec la valeur temporaire, si la valeur recu est plus grande , 
        #on remplace la valeur et le nouveau leader temporaire est remplacé
            if int_finale > self.nombre_temp:
                print("nouveau leader temporaire")
                self.nombre_temp = int_finale
                self.id_leader = port_finale
            # on regarde si on est le suivant (la différence entre l'id precedant et le notre doit être egale à 1)
            if plage_port+self.group*nb_capteurs_par_groupe+self.identifiant - port_finale == 1:
                self.mon_tour = True
                print("A mon tour ! ")
        except socket.timeout:
            print("Noeud:", self.identifiant, "Timeout")
            print("Capteur numéro : "+str(self.identifiant)+", Groupe "+str(self.group)+", Port leader : "+str(self.id_leader))
            self.finex = True
    # fonction qui va envoyer un nombre aléatoire une fois la l'élection faite       
    def envoyer_au_leader(self):
        try:
            self.socket_envoie_au_leader = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_envoie_au_leader.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_envoie_au_leader.connect(("localhost",self.id_leader))
            self.socket_envoie_au_leader.send((str(random.randint(0,10))).encode('utf-8'))
            self.socket_envoie_au_leader.close()
        except OSError:
        	pass
    #fonction qui va recevoir un nombre aléatoire des autres capteurs une fois la l'élection faite 
    def recevoir_des_esclaves(self):
        while(1):
            try:
                (clientsocket, address) = self.socket.accept()
                recu = clientsocket.recv(24)
                str_finale = int(recu.decode())
                print("Leader groupe "+str(self.group)+", message reçu : "+str(str_finale))
            except socket.timeout:
                print("Noeud:", self.identifiant, "Timeout")
            
    #ferme les connections      
    def fermer_connection(self):
        self.socket.close()



# main du programme
if __name__ == "__main__":
	plage_port = 5000
	nb_capteurs_par_groupe = 10
	identifiant_incremente = 0
	groupe1 = []
	groupe2 = []
	groupe3 = []
	all_groupe = list([groupe1,groupe2,groupe3])

	for id_groupe,groupe in enumerate(all_groupe):
		identifiant_incremente = 0
		for j in range(nb_capteurs_par_groupe):
			groupe.append(threading.Thread(target=thread_function, args=(identifiant_incremente,id_groupe)))
			groupe[j].start()
			identifiant_incremente += 1