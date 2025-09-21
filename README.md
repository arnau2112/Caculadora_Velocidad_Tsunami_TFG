El presente repositorio GitHub contiene dos codigos Python:
-Calculadora velocidad tsunami (1)
-Toolbox (2)

La calculadora de velocidad (1) permite saber el tiempo que tardará un tsunami desde las coordenadas insertadas por el usuario, en ETRS89 H29N, hasta la ciudad gaditana. El resultado se presenta en minutos. En suma, el código calcula el tiempo de recorrido del tsunami para cada celda, entre la división entre la distancia de esta y la velocidad en cada tramo. La velocidad del tsunami para cada celda se calcula como:
 √(g*d)
 Es importante descargarse la batimetria de la zona de estudio para cada caso. Pueden introducirse el numero de coordenadas que desee el usuario, porqué no existe un máximo.

 En la toolbox (2) se refomrula el código anterior para recrearlo como una herramienta ArcGIS. Solo se permite la introducción de un punto de coordenadas. 

 
 
