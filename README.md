Para iniciar se debe crear un entorno virtuale env python:

python -m venv {nombre del entorno}

Luego ingresar al entorno virtual:

source {nombre del entorno}/bin/activate

Luego generar un archivo .env con la variable de entorno OPENAI_API_KEY (Puede sacarse del notion en el documento de accesos)

Instalar las dependencias:

pip install -r requierements.txt

Por ultimo ejecutar el script:

python langchain_p.py
