import pygame
import sys
import math

#Fait par :
# Clement Faure
# Clement Dufour
# Tom Torrente





pygame.init()

# initialisation de la fenetre
LARGEUR, HAUTEUR = 1280, 720
ecran = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("Mancala")

# chargement des images
try:
    plateau = pygame.image.load("plateaumancala.png").convert_alpha()
    plateau = pygame.transform.scale(plateau, (LARGEUR, HAUTEUR))

    bille = pygame.image.load("bille.png").convert_alpha()
    bille = pygame.transform.scale(bille, (50, 50))
except pygame.error as e:
    print("Erreur image :", e)
    pygame.quit()
    sys.exit()

# emplacements possibles des billes
trous_haut = [(260,170),(410,170),(560,170),(715,170),(860,170),(1020,170)]
trous_bas  = [(260,530),(410,530),(560,530),(715,530),(870,530),(1020,530)]
positions = trous_haut + trous_bas

tresor_haut = (100, 360)
tresor_bas  = (1170, 360)

RAYON_CLIC = 60

# Etat du jeu
trous = [4] * 12          # 4 billes dans chaque trou
tresors = [0, 0]          # [tresor_haut, tresor_bas]
joueur = 1                # 0 = haut, 1 = bas
fin = False
message_fin = ""

police = pygame.font.SysFont(None, 36)
grande_police = pygame.font.SysFont(None, 60)


# les differentes fonctions servant a faire que le jeu fonctionne
def trou_du_joueur(j, i):
    if j == 0:
        return 0 <= i <= 5
    else:
        return 6 <= i <= 11

def oppose(i):
    return 11 - i


# donne l'emplacement du clic

def trouver_trou(pos_souris):
    mx, my = pos_souris
    for i, (cx, cy) in enumerate(positions):
        if math.hypot(mx - cx, my - cy) < RAYON_CLIC:
            return i
    return None

def dessiner_billes(centre, nb):
    if nb <= 0:
        return
    cx, cy = centre

    # ici on fait en sorte que les billes forment toujours un carre
    taille = math.ceil(math.sqrt(nb))
    esp = 30
    x0 = cx - (taille - 1) * esp / 2
    y0 = cy - (taille - 1) * esp / 2

    k = 0
    for lig in range(taille):
        for col in range(taille):
            if k >= nb:
                return
            x = x0 + col * esp
            y = y0 + lig * esp
            ecran.blit(bille, (x - 20, y - 20))
            k += 1

def jouer_coup(depart, j):
    #Retourne True si le joueur rejoue (dernière bille dans son trésor).
    nb = trous[depart]
    trous[depart] = 0

    idx = depart
    dernier_trou = None
    dernier_dans_tresor = False

    while nb > 0:
        idx = (idx + 1) % 14   # 0..11 trous, 12 trésor haut, 13 trésor bas

        # on saute le trésor adverse
        if j == 0 and idx == 13:
            continue
        if j == 1 and idx == 12:
            continue

        # poser une bille
        if idx <= 11:
            trous[idx] += 1
            dernier_trou = idx
            dernier_dans_tresor = False
        else:
            if idx == 12:
                tresors[0] += 1
            else:
                tresors[1] += 1
            dernier_trou = None
            dernier_dans_tresor = True

        nb -= 1

    # rejouer si dernière bille dans son trésor
    if dernier_dans_tresor:
        if (j == 0 and idx == 12) or (j == 1 and idx == 13):
            return True

    # on ajoute la regle de capture du jeu ( la regle n'est peut etre pas la bonne)
    if dernier_trou is not None and trou_du_joueur(j, dernier_trou):
        if trous[dernier_trou] == 1:  # il était vide avant
            o = oppose(dernier_trou)
            if trous[o] > 0:
                gain = trous[o] + trous[dernier_trou]
                trous[o] = 0
                trous[dernier_trou] = 0
                tresors[j] += gain

    return False

def verifier_fin():
    global fin, message_fin

    haut_vide = sum(trous[0:6]) == 0
    bas_vide = sum(trous[6:12]) == 0

    if not (haut_vide or bas_vide):
        return

    # on ramasse le reste
    if not haut_vide:
        tresors[0] += sum(trous[0:6])
        for i in range(6):
            trous[i] = 0

    if not bas_vide:
        tresors[1] += sum(trous[6:12])
        for i in range(6, 12):
            trous[i] = 0

    fin = True
    if tresors[0] > tresors[1]:
        message_fin = "Joueur HAUT gagne !"
    elif tresors[1] > tresors[0]:
        message_fin = "Joueur BAS gagne !"
    else:
        message_fin = "Égalité !"

def reset():
    global trous, tresors, joueur, fin, message_fin
    trous = [4] * 12
    tresors = [0, 0]
    joueur = 1
    fin = False
    message_fin = ""


# Boucle qui sert a actualiser le jeu et le faire marcher tant que la fenetre est ouverte
horloge = pygame.time.Clock()
en_cours = True

while en_cours:
    horloge.tick(60)

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            en_cours = False

        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_r:
                reset()

        if ev.type == pygame.MOUSEBUTTONDOWN and not fin:
            i = trouver_trou(pygame.mouse.get_pos())
            if i is not None:
                if trou_du_joueur(joueur, i) and trous[i] > 0:
                    rejoue = jouer_coup(i, joueur)
                    verifier_fin()
                    if (not fin) and (not rejoue):
                        joueur = 1 - joueur

    # Affichage du jeu pour le joueur
    ecran.fill((30, 30, 30))
    ecran.blit(plateau, (0, 0))

    for i, centre in enumerate(positions):
        dessiner_billes(centre, trous[i])

    dessiner_billes(tresor_haut, tresors[0])
    dessiner_billes(tresor_bas, tresors[1])

    if not fin:
        texte = "Tour : Joueur BAS" if joueur == 1 else "Tour : Joueur HAUT"
        ecran.blit(police.render(texte, True, (255, 255, 255)), (20, 20))
    else:
        t = grande_police.render(message_fin, True, (255, 255, 255))
        ecran.blit(t, (LARGEUR//2 - t.get_width()//2, 20))
        s = police.render("Appuie sur R pour rejouer", True, (255, 255, 255))
        ecran.blit(s, (LARGEUR//2 - s.get_width()//2, 85))

    pygame.display.flip()

pygame.quit()
sys.exit()
