El presente repositorio de GitHub contiene dos códigos en Python:

Calculadora de velocidad de tsunami (1) 🌊

Toolbox (2) 🛠️

La calculadora de velocidad (1) permite conocer el tiempo que tardará un tsunami, desde las coordenadas insertadas por el usuario (en ETRS89 H29N), hasta la ciudad de Cádiz. El resultado se presenta en minutos. En suma, el código calcula el tiempo de recorrido del tsunami para cada celda, dividiendo la distancia entre la velocidad en cada tramo.

La velocidad del tsunami para cada celda se calcula con la fórmula:

√(g*d)
	​


⚠️ Es importante descargar la batimetría de la zona de estudio para cada caso.
Además, pueden introducirse tantas coordenadas como desee el usuario, ya que no existe un máximo.

En la toolbox (2) se reformula el código anterior para recrearlo como una herramienta de ArcGIS Pro. En este caso, solo se permite la introducción de un punto de coordenadas.
 
