# Support formation PyQGIS

## Liens utiles 

[Formation PyQGIS de Nicolas Roeland](https://roelandtn.frama.io/cours_pyqgis/)
[Plugin QGIS Mobility Areas du Cerema](rpc2://search.tag/https://github.com/crocovert/mobilityareas/), à consulter

## Utiliser la console Python de QGIS

**Ajouter une couche depuis la console** :

```
# iface n'a pas besoin d'être importé explicitement.
uri = "chemin/vers/le/fichier/"
shape = iface.addVectorLayer(
    vectorLayerPath: Qstring = uri,              # chemin vers le fichier,
    baseName: Qstring = "nom du fichier",        # Nom de la couche dans QGIS
    providerKey: Qstring = "ogr"                 # Convention d'ouverture.
)
```

**Qstring** : Chaîne de caractère, gérée par l'interface de QGIS, Qt. Qt transmet la str à l'application.
La méthode iface.addVectorLayer() retourne un objet QgsVectorLayer.

**Afficher la table attributaire** :
```
iface.showAttributeTable(variable)
# Prend en argument une variable et non le nom d'une couche.
```










***** FIN *****