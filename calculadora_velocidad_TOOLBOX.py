# -*- coding: utf-8 -*-
import arcpy
import os
from arcpy.sa import *
from shutil import rmtree
from tkinter import messagebox

class Toolbox(object):
    def __init__(self):
        self.label = "Toolbox Evacuación Tsunami"
        self.alias = "evacuacion_tsunami"
        self.tools = [SimulacionEvacuacion]

class SimulacionEvacuacion(object):
    def __init__(self):
        self.label = "Simulación Ruta de Evacuación por Tsunami"
        self.description = "Crea línea geodésica entre Cádiz y un punto destino, realiza análisis de velocidad y tiempo, y devuelve resultados."
        self.canRunInBackground = False

    def getParameterInfo(self):
        params = [
            arcpy.Parameter(
                displayName="Directorio de resultados",
                name="resultados",
                datatype="DEFolder",
                parameterType="Required",
                direction="Input"
            ),
            arcpy.Parameter(
                displayName="Coordenada X del punto destino",
                name="x_destino",
                datatype="GPDouble",
                parameterType="Required",
                direction="Input"
            ),
            arcpy.Parameter(
                displayName="Coordenada Y del punto destino",
                name="y_destino",
                datatype="GPDouble",
                parameterType="Required",
                direction="Input"
            ),
            arcpy.Parameter(
                displayName="DEM del Atlántico (GEBCO)",
                name="dem_atlantico",
                datatype="DERasterDataset",
                parameterType="Required",
                direction="Input"
            )
        ]
        return params

    def execute(self, parameters, messages):
        resultados = parameters[0].valueAsText
        x = parameters[1].value
        y = parameters[2].value
        dem = parameters[3].valueAsText

        if os.path.exists(resultados):
            rmtree(resultados)
        os.mkdir(resultados)

        sr = arcpy.SpatialReference(25829)

        # Crear capa de puntos
        puntos_path = os.path.join(resultados, "cadiz_puntos.shp")
        arcpy.CreateFeatureclass_management(resultados, "cadiz_puntos.shp", "POINT", spatial_reference=sr)
        arcpy.AddField_management(puntos_path, "ID", "LONG")

        punto_inicial = (749619.490, 4046543.086)
        punto_destino = (x, y)

        with arcpy.da.InsertCursor(puntos_path, ["SHAPE@XY", "ID"]) as cursor:
            cursor.insertRow([punto_inicial, 1])
            cursor.insertRow([punto_destino, 2])

        # Crear línea entre puntos
        linea_path = os.path.join(resultados, "linea.shp")
        arcpy.CreateFeatureclass_management(resultados, "linea.shp", "POLYLINE", spatial_reference=sr)
        arcpy.AddField_management(linea_path, "ID_INICIO", "LONG")
        arcpy.AddField_management(linea_path, "ID_FIN", "LONG")

        array = arcpy.Array([arcpy.Point(*punto_inicial), arcpy.Point(*punto_destino)])
        linea = arcpy.Polyline(array)
        with arcpy.da.InsertCursor(linea_path, ["SHAPE@", "ID_INICIO", "ID_FIN"]) as cursor:
            cursor.insertRow([linea, 1, 2])

        # Línea geodésica densificada
        geodetic_line = os.path.join(resultados, "linea_geodesica.shp")
        arcpy.management.GeodeticDensify(linea_path, geodetic_line, "GEODESIC")

        # Cálculo de velocidad con raster
        arcpy.CheckOutExtension("Spatial")
        output_raster = os.path.join(resultados, "raster_GEBCO.tif")
        velocidad = Int(SquareRoot(9.80665 * (Raster(dem) * -1)))
        velocidad.save(output_raster)

        # Extracción por máscara
        extract_mask = os.path.join(resultados, "extractmask.tif")
        outExtractByMask = ExtractByMask(output_raster, geodetic_line)
        outExtractByMask.save(extract_mask)

        # Raster a polígono
        out_poligono = os.path.join(resultados, "polylinea.shp")
        arcpy.conversion.RasterToPolygon(extract_mask, out_poligono, "NO_SIMPLIFY", "VALUE")

        # Intersección
        intersectado = os.path.join(resultados, "intersect_pairwise")
        arcpy.analysis.PairwiseIntersect([geodetic_line, out_poligono], intersectado, "ALL", "", "INPUT")

        # Longitud y tiempo
        arcpy.management.CalculateGeometryAttributes(intersectado, [["Shape_Le", "LENGTH"]], "METERS")
        arcpy.AddField_management(intersectado, "Tiempo_via", "DOUBLE")

        # Filtro por gridcode > 0
        filtrado = os.path.join(resultados, "SELECT")
        arcpy.analysis.Select(intersectado, filtrado, '"gridcode" > 0')

        arcpy.management.CalculateField(filtrado, "Tiempo_via", "!Shape_Le! / !gridcode! / 60", "PYTHON3")

        # Estadísticas finales
        final_dir = os.path.join(resultados, "RESULTADOS_FINAL")
        if os.path.exists(final_dir):
            rmtree(final_dir)
        os.mkdir(final_dir)

        out_tabla = os.path.join(final_dir, "tablaDEFINITVA.dbf")
        arcpy.analysis.Statistics(filtrado, out_tabla, [["Tiempo_via", "SUM"]], "ID_FIN")

        with arcpy.da.SearchCursor(out_tabla, ['ID_FIN', 'SUM_Tiempo']) as cursor:
            for row in cursor:
                resultado = f"Punto ID {row[0]}: {round(row[1], 2)} minutos estimados"
                messages.addMessage(resultado)
                messagebox.showinfo('Resultado', resultado)

