""" Entraînement apprentissage """
import sys 
import processing                # Algorithmes de la boîte à outil.
from qgis.core import QgsProject # Chargement des méthodes spécifiques aux projets.

## CHARGER LES DONNEES ##
chemin_donnees = r"C:\Users\will\Dropbox\FORMATIONS\PYQGIS\DONNEES"
# Arrondissements 
uri = f"{chemin_donnees}\\arrondissements.shp"
arr = iface.addVectorLayer(uri, "arrondissements", "ogr")

# Gares 
uri = f"{chemin_donnees}\\gares_sncf.shp"
gares = iface.addVectorLayer(uri, "gares", "ogr")

# Métros
uri = f"{chemin_donnees}\\entrees_sorties_metro.shp"
metros = iface.addVectorLayer(uri, "metros", "ogr")

## Contrôle des système de référence de coordonnées ##
# Remarque : on pourrait également en faire une fonction.
for i in QgsProject.instance().mapLayers().values() :
    crs = i.crs().authid() 
    # print(f"{i.name()}:{crs}")
    
    if crs == '' : # Issu de print(f"{i.name()}:{crs}").
        couche_reprojetee = processing.runAndLoadResults(
            "native:reprojectlayer",
            {"INPUT":i,
            "TARGET_CRS":QgsCoordinateReferenceSystem("IGNF:LAMB93"),
            "OUTPUT":"TEMPORARY_OUTPUT"}
        )["OUTPUT"]
    else :
        pass

## Extraction de la gare de Part-Dieu ##

# Sélection par expression :
expr = "nom = 'Gare de Lyon Part-Dieu'"
part_dieu = processing.runAndLoadResults(
    "native:extractbyexpression",
    {"INPUT" : couche_reprojetee,
     "EXPRESSION" : expr,
     "OUTPUT":"TEMPORARY_OUTPUT"}
)["OUTPUT"]

## Création de la zone tampon ##

tampon_partdieu = processing.runAndLoadResults(
    "native:buffer",
    {"INPUT":part_dieu,
     "DISTANCE":1000,
     "SEGMENTS":25,
     "END_CAP_STYLE":0,
     "JOIN_STYLE":0,
     "MITER_LIMIT":2,
     "DISSOLVE":False,
     "OUTPUT":"TEMPORARY_OUTPUT"})["OUTPUT"]

## Intersection des stations de métros ##
metro_1000m = processing.runAndLoadResults(
    "native:intersection",
    {"INPUT":metros,
     "OVERLAY":tampon_partdieu,
     "INPUT_FIELDS":list(),
     "OVERLAY_FIELDS":list(),
     "OUTPUT":"TEMPORARY_OUTPUT"})["OUTPUT"]

## Puis renommer la couche finale ##
# 1) Identifier la couche 
projet = QgsProject.instance()
projet.mapLayersByName("Intersection")[0].setName("metro_1000m")

## Sauvegarder des couches ##

# 1) Sélectionner une couche par son nom :
couche = projet.mapLayersByName("metro_1000m")[0]
chemin_resultats = r"C:\Users\will\Dropbox\FORMATIONS\PYQGIS\RESULTATS\metros_1000m_v2.shp"

# 2) Exporter la couche en géopackage.
QgsVectorLayerExporter.exportLayer(
    layer = couche,
    uri = chemin_resultats,
    providerKey = "ogr",
    destCRS = QgsCoordinateReferenceSystem("EPSG:2154"))

# Préférable pour exporter des fichier en shapefile.
QgsVectorFileWriter.writeAsVectorFormat(
    layer = couche, 
    fileName = chemin_resultats, 
    fileEncoding = "utf-8", 
    destCRS = QgsCoordinateReferenceSystem("EPSG:2154"), 
    driverName = "ESRI Shapefile")


##### FIN #####