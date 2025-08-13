import arcpy
import os
from arcpy.sa import *
from shutil import rmtree
from tkinter import messagebox



# Ruta de trabajo
resultados = r"C:\Users\becari.a.sola\Documents\ArcGIS\Projects\ArcGIS_TFGE\resultados"

rmtree(resultados)
os.mkdir(resultados)


# Nombre del archivo de puntos
nombre_puntos = "cadiz_puntos.shp"
output_puntos = os.path.join(resultados, nombre_puntos)

sr = arcpy.SpatialReference(25829)  # ETRS89 UTM Zona 29N

# Crear una única Feature Class para almacenar todos los puntos
arcpy.CreateFeatureclass_management(resultados, nombre_puntos, "POINT", spatial_reference=sr)

# Agregar un campo de ID con valores incrementales
arcpy.AddField_management(output_puntos, "ID", "LONG")

# Insertar el primer punto fijo con ID = 1
coordenadas_iniciales = (749619.490, 4046543.086)
with arcpy.da.InsertCursor(output_puntos, ["SHAPE@XY", "ID"]) as cursor:
    cursor.insertRow([coordenadas_iniciales, 1])

print("Punto inicial creado con ID = 1.")

# Pedir al usuario más puntos
n = int(input('Número de puntos que deseas introducir: '))

# Lista de puntos para almacenar las coordenadas
puntos = [(749619.490, 4046543.086)]  # Incluir el punto inicial
for i in range(n):
    x = float(input(f'Introducir coordenada X para el punto {i+1}: '))
    y = float(input(f'Introducir coordenada Y para el punto {i+1}: '))
    coordenadas = (x, y)
    puntos.append(coordenadas)  # Guardar las coordenadas de cada punto

    # Insertar el punto en la capa de puntos
    with arcpy.da.InsertCursor(output_puntos, ["SHAPE@XY", "ID"]) as cursor:
        cursor.insertRow([coordenadas, i + 2])  # El primer punto fue el ID = 1, continuamos desde 2

    print(f'Punto {i+1} agregado con ID = {i+2}.')

# Crear la Feature Class para las líneas
nombre_linea = "lineas_cadiz.shp"
output_linea = os.path.join(resultados, nombre_linea)

arcpy.CreateFeatureclass_management(resultados, nombre_linea, "POLYLINE", spatial_reference=sr)

# Agregar un campo de ID de inicio y fin a la línea
arcpy.AddField_management(output_linea, "ID_INICIO", "LONG")
arcpy.AddField_management(output_linea, "ID_FIN", "LONG")

# Insertar las líneas desde el punto inicial hacia los puntos introducidos
with arcpy.da.InsertCursor(output_linea, ["SHAPE@", "ID_INICIO", "ID_FIN"]) as cursor:
    for i in range(1, len(puntos)):  # Comenzamos desde el segundo punto
        # Crear la línea desde el punto inicial hasta el punto actual
        array = arcpy.Array([arcpy.Point(puntos[0][0], puntos[0][1]), arcpy.Point(puntos[i][0], puntos[i][1])])
        polyline = arcpy.Polyline(array)

        # Insertar la línea en la capa
        cursor.insertRow([polyline, 1, i + 1])  # ID_INICIO = 1 (punto inicial), ID_FIN = i + 1 (ID del punto)

        print(f"Línea desde el punto 1 hasta el punto {i + 1} agregada con ID_INICIO = 1 y ID_FIN = {i + 1}.")

print("Líneas creadas con éxito.")


# Crear la línea geodésica densificada
nombre_geodetic = "linea_geodesica.shp"
out_feature_class = os.path.join(resultados, nombre_geodetic)

arcpy.management.GeodeticDensify(output_linea, out_feature_class, "GEODESIC")

print("Geodesia creada.")


# Habilitar la extensión Spatial Analyst
arcpy.CheckOutExtension("Spatial")

# Definir la ruta del ráster de entrada
atlantic_dem = r"C:/Users/becari.a.sola/Documents/ArcGIS/Projects/ArcGIS_TFGE/GEBCO_05_Mar_2025_ff2c4f0025f4/gebco_2024_n38.0_s34.0_w-12.0_e-6.0.asc"  # Modifica la ruta correcta

# Definir la ruta del ráster de salida
output_raster = os.path.join(resultados, "raster_GEBCO.tif")


# Aplicar la fórmula
resultado = Int(SquareRoot(9.80665 * (Raster(atlantic_dem)*-1)))

# Guardar el ráster resultante
resultado.save(output_raster)

print("Cálculo completado. Ráster guardado en:", output_raster)


outExtractByMask = ExtractByMask(output_raster, out_feature_class, "INSIDE")


outExtractByMask.save(r"C:\Users\becari.a.sola\Documents\ArcGIS\Projects\ArcGIS_TFGE\resultados\extractmask.tif")
print('Extract realizado')


in_raster = r"C:\Users\becari.a.sola\Documents\ArcGIS\Projects\ArcGIS_TFGE\resultados\extractmask.tif"
out_polygon_features = os.path.join(resultados, "polylinea.shp")

arcpy.conversion.RasterToPolygon(in_raster, out_polygon_features, "NO_SIMPLIFY", "VALUE")

print("conversion realizada")


in_features = [out_feature_class, out_polygon_features]
out_feature_class2 = os.path.join(resultados, "intersect_pairwise")

# Parámetros opcionales correctamente definidos
join_attributes = "ALL"  # Puede ser "ALL", "NO_FID" o "ONLY_FID"
cluster_tolerance = ""  # Si no deseas definir tolerancia, usa una cadena vacía
output_type = "INPUT"  # Puede ser "INPUT", "LINE", o "POINT"

arcpy.analysis.PairwiseIntersect(in_features, out_feature_class2, join_attributes, cluster_tolerance, output_type)
print("intersección creada correctamente ")

arcpy.management.CalculateGeometryAttributes(out_feature_class2, [["Shape_Le", "LENGTH"]], "METERS")
print("Campo Shape_Length calculado manualmente.")

arcpy.AddField_management(out_feature_class2, "Tiempo_via", "DOUBLE")




# Capa de entrada
input_layer = r"C:\Users\becari.a.sola\Documents\ArcGIS\Projects\ArcGIS_TFGE\resultados\intersect_pairwise"

# Capa filtrada (donde gridcode > 0)
filtered_layer = r"C:\Users\becari.a.sola\Documents\ArcGIS\Projects\ArcGIS_TFGE\resultados\SELECT"

# Expresión SQL para seleccionar solo los registros donde gridcode > 0
sql_query = '"gridcode" > 0'

# Aplicar el filtro y crear la nueva capa
arcpy.analysis.Select(input_layer, filtered_layer, sql_query)

arcpy.management.CalculateField(filtered_layer,"Tiempo_via", "!Shape_Le! / !gridcode! /60")


final = os.path.join(resultados, "RESULTADOS_FINAL")
if not os.path.exists(final):
    os.mkdir(final)
else:
    shutil.emtree(final)
    os.mkdir(final)


out_tableT = os.path.join(final, "tablaDEFINITVA.dbf")
arcpy.analysis.Statistics(filtered_layer, out_tableT, [["Tiempo_via", "SUM"]], "ID_FIN")

with arcpy.da.SearchCursor(out_tableT, ['ID_FIN','SUM_Tiempo']) as cursor:
    for row in cursor:
        result =(row[0], '=', row[1])
        print(result)
        info = messagebox.showinfo('Resultado', result)
        
