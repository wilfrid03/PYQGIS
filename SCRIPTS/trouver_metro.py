""" TROUVER LES GARES A MOINS DE 1000M DE LA GARE DE LYON

Ce script doit être utilisé dans QGIS. Il permet d'identifier toutes les stations de métro dans un rayon de 500m autour de la gare Part Dieu.
"""

import sys 
import processing # les géotraitements QGIS 
from qgis.core import QgsProject # Charger les méthodes 
#+ spécifiques au projet qgis.

## print(sys.version)

## CHARGER LES DONNEES       ##
chemin_donnees = r"C:\Users\will\Dropbox\FORMATIONS\PYQGIS\DONNEES"
# Couche des arrondissement :
uri = f"{chemin_donnees}\\arrondissements.shp"
arr = iface.addVectorLayer(
    vectorLayerPath=uri,
    baseName="Arrondissements",
    providerKey="ogr"
)

# Couche des gares 
uri = f"{chemin_donnees}\\gares_sncf.shp"
gares = iface.addVectorLayer(
    vectorLayerPath=uri,
    baseName="Gare",
    providerKey="ogr"
)

# Couche des métros 
uri = f"{chemin_donnees}\\entrees_sorties_metro.shp"
metros = iface.addVectorLayer(
    vectorLayerPath=uri,
    baseName="metros",
    providerKey="ogr"
)

## CONTROLES                                              ##
# Regarder la table attributaire de chque table.

# Contrôle du CRS :
def crs_controle(layer:qgis._core.QgsVectorLayer) :
    crs = layer.crs().authid()    # Récupérer l'identifiant du crs.
    print(layer.name(), ":", crs) # Afficher le crs de la couche

def controle_crs_couches() :
    for i in QgsProject.instance().mapLayers().values() :
        # .mapLayers() permet de récupérer un tableau d'info 
        #+ sur les couches.
        crs_controle(layer=i)
    
# Reprojeter une couche sans crs :
gares_reprojetee = processing.runAndLoadResults(
    "native:reprojectlayer", # Utiliser le processing de reprojection natif.
    {
        "INPUT":gares,
        "TARGET_CRS":QgsCoordinateReferenceSystem("EPSG:2154"),
        "OUTPUT":"TEMPORARY_OUTPUT"
    })["OUTPUT"]

controle_crs_couches() # Contrôler la projection des couches.

## SELECTIONNER LA GARE POI                                   ##
# Pour sélectionner la gare de Lyon Part-Dieu, nous allons
#+ utiliser une expression. Les expressions QGIS sont utiles
#+ pour de la sélection pour mettre en place des filtres,
#+ ou encore des styles.

expression = "nom = 'Gare de Lyon Part-Dieu'"
# Sélection :
part_dieu = processing.runAndLoadResults(
    "native:extractbyexpression", # Traitement extract by expression.
    {"INPUT":gares_reprojetee,
    "EXPRESSION":expression,
    "OUTPUT":"TEMPORARY_OUTPUT"})["OUTPUT"]

## Puis création d'une zone tampon de 1000m autour de la gare Part-Dieu.
# note : un "buffer de 1000m" signifie "buffer de 
part_dieu_buffer = processing.runAndLoadResults(
    "native:buffer",
    {"INPUT":part_dieu, # Objet de référence.
    "DISTANCE":1000,    # Distance souahitée.
    "SEGMENT":25,       # Nombre de segments pour les angles.
    "END_CAP_STYLE":0,
    "JOIN_STYLE":0,
    "MITER_LIMIT":2,
    "DISSOLVE":False,
    "OUTPUT":"TEMPORARY_OUTPUT"})["OUTPUT"]

# Visualiser le résultat :
# A ce stade, on ne peut pas prendre réellement
#+ le contrôle des tables temporaires avec les outils.

## Identifier les stations demétro à 1000m ou moins :
metros_100m = processing.runAndLoadResults(
    "native:intersection",
    {"INPUT":metros,
    "OVERLAY":part_dieu_buffer,
    "INPUT_FIELDS":list(),
    "OVERLAY_FIELDS":list(),
    "OUTPUT":"TEMPORARY_OUTPUT"})["OUTPUT"]



# Dans ce cas, il faut les saisir par leur nom :
# Enregistrer la couche issus de l'intersection.
projet = QgsProject.instance() # Récupérer le porjet courant.
for id, layer in projet.mapLayers().items() :
    print(layer.name())

projet.mapLayersByName("Intersection")[0].set_name("metro_500m")

## Sauvegarder la couche :
couche = projet.mapLayersByName("metro_500m")[0]
res_chemin = r"C:\Users\will\Dropbox\FORMATIONS\PYQGIS\RESULTATS\metro_500m.shp"
QgsVectorLayerExporter.exportLayer(
                                layer=couche, 
                                uri=res_chemin, 
                                providerKey = 'ogr', 
                                destCRS = QgsCoordinateReferenceSystem('EPSG:2154'))









##### FIN #####