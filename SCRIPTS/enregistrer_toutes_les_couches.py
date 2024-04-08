""" Script pour enregistrer toutes les couches ouvertes dans un projet 

Usage:
======
    python enregistrer_toutes_les_couches.py
    Script a exécuter directement dans QGIS.
    Ce script permet d'enregistrer toutes les couches ouvertes dans un projet 
    dans un répertoire en local.
    
    Note : faire une 2e version, qui permet d'enregistrer les couches
    d'un projet QGIS sans l'ouvrir avec son interface graphique.

"""

__authors__ = ("")
__contact__ = ("")
__copyright__ = "None"
__date__ = "2024-04-05"
__version__= "3.9.5"

""" Etapes du script 
1) Charger au moins deux couches manuellement.

2) Définir un espace de stockage de destination.

3) Parcourir l'ensemble des couches dans le projet courant. 
3.1) Lors de ce parcours, récupérer les noms de chaque couche.
3.2) Vérifier la projection. Si la projection est celle souhaité, 
passer à la suite.
3.3) Si la projection n'est pas celle souhaitée, reprojeter la couche.
3.4) Ajouter la couche reprojetée au projet.
3.5) Enregistrer les couches une par une dans le répertoire défini en 2).
Utiliser les noms des couches dans le projet pour nommer les couches 
sauvegardées.

4) Contrôler les enregistrements après sauvegarde.
4.1) Est-ce que les géométries sont bonnes ?
4.2) Est-ce que la projection est conforme aux attentes ?
4.3) Est-ce que l'encodage est le même que celui en entrée ?
"""

import os 
import sys 

import processing
from qgis.core import QgsProject 

# Définir un espace de stcokage de destination :
DEST:str = r"C:\Users\will\Dropbox\FORMATIONS\PYQGIS\RESULTATS" 

# Définir l'espace sources des données :
SOURCE:str = r"C:\Users\will\Dropbox\FORMATIONS\PYQGIS\DONNEES"

# Définir le système de projection de sortie :
CRS_DEST = QgsCoordinateReferenceSystem("IGNF:LAMB93")

p = QgsProject.instance()           # Récupérer le projet courant.

couches_a_enregistrer:list = list() # Liste des couches à enregistrer.

# Afficher la liste des couches présentes dans le projet :
def run(projet_qgis:qgis.core.QgsProject.instance(), 
        projection:QgsCoordinateReferenceSystem) :
    """ ***** Description *****
    
    projet_qgis:qgis.core.QgsProject.instance()) : projet qgis sur 
    lequel va s'exécuter les instructions de lecture de couche.
    projection:QgsCoordinateReferenceSystem : Projection souhaitée 
    pour le contrôle.
    
    projet_qgis : projet QGIS à manipuler.
    projection : projection de contrôle et de destination souhaitée.
    liste_couches_a_enregistrer : liste dans laquelle les couches seront listées
    afin d'être ensuite enregistrées dans un répertoire.
    
    """
    
    liste_couches_a_enregistrer:list = list()
    
    for id, couche in projet_qgis.mapLayers().items() :
        
        # Récupérer le nom de la couche courante :
        nom_couche = couche.name() 
        # print(nom_couche)
        crs_couche = couche.crs().authid()
        
        # Contrôler la projection :
        if crs_couche == projection :
            print("La couche", nom_couche, "est conforme", couche.crs())
            liste_couches_a_enregistrer.append(nom_couche)
        
        else :
            couche_reprojetee = processing.runAndLoadResults(
            "native:reprojectlayer",
            {"INPUT":nom_couche,
            "TARGET_CRS":projection,
            "OUTPUT":"TEMPORARY_OUTPUT"})["OUTPUT"]
            
            # Puis renommer la couche reprojetée :
            nom_couche_reprojetee = f"{nom_couche}_reprojetee"
            projet_qgis.mapLayersByName("Reprojeté")[0].setName(nom_couche_reprojetee)
            
            liste_couches_a_enregistrer.append(nom_couche_reprojetee) 
            
            # Puis supprimer toutes les couches reprojetées appelée "Reprojeté".
            if len(projet_qgis.mapLayersByName("Reprojeté")) > 0 :
                couche_a_suppr = projet.mapLayersByName("Reprojeté")[0]
                projet_qgis.removeMapLayer(couche_a_suppr.id())
            else :
                pass

            
            # https://dev.to/mierune/get-started-with-pyqgis-02-manage-layers-with-qgis-python-console-mhc
    return liste_couches_a_enregistrer
    
# Puis enregistrer toutes les couches.
def enregistrer_fichiers(couche, chemin_resultat, crs_dest) :
    
    # chemin_resultat doit être modifié avec l'argument couche.
    
    try :
    
        QgsVectorFileWriter.writeAsVectorFormat(
        layer = couche,               # Couche à enregistrer.
        fileName = chemin_resultat,   # Chemin vers l'espace d'enregistrement.
        fileEncoding = "utf-8",       # Encodage.
        destCRS = crs_dest,           # Projection de destination
        driverName = "MapInfo File")
        # Liste driverName : https://gis.stackexchange.com/questions/352506/list-of-usable-ogr-drivers-for-pyqgis
        
        print("La couche", chemin_resultat, "a été enregistrée")
    
    except Exception as e :
        print("Erreur lors de l'enregistrement")
        print(e)
           
        
        
# Exécution principale :
couches_a_enregistrer = run(projet_qgis = p, projection = CRS_DEST)
    
# Enregistrer le résultat.
if len(couches_a_enregistrer) > 0 :
    
    for i in couches_a_enregistrer :
        # Adapter le chemin de destination.
        chemin_resultat = f"{DEST}\\{i}"
        couche_a_enregistrer = p.mapLayersByName(i)[0]
        
        # Lancer la fonction d'enregistrement avec le chemin adapté.
        enregistrer_fichiers(couche = couche_a_enregistrer, 
                             chemin_resultat = chemin_resultat,
                             crs_dest = CRS_DEST)
                             
else :
    print("La liste des couches à enregistrer est de ", 
    len(couches_a_enregistrer))
    


##### FIN #####