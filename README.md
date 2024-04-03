#Instalar :
1) conda env create -f environment.yaml
#Como producir los archivos de la ferrovia:
1) Ejecute python extraer_ferrovia.py
2) Si es la primera vez que instala todo el sistema entonces:
   2.1 Ejecute python NcJsonPoligon.py first   --- ejecuto este paso la primera vez entonces vaya directo al siguiente paso
   2.2 Ejecute python NcJsonPoligon.py all

 Ejemplo de una procución de datos automatizada (luego de haber ejecutado paso 2.1 por primera vez):
  python extraer_ferrovia.py
  python NcJsonPoligon.py all
 
 Siempre mantenga el orden de ejecución anterior, primero produzca los datos de la ferrovia y luego los datos para los layers

#Como ejecutar el app:
1) Activar enviroment DashboardsSE
2) streamlit run app.py 
3) Una vez que se ejecute en la consola verá un mensaje como el siguiente que le 
    indicará donde desplegar el app:
 You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.0.180:8501
