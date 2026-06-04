import requests
from bs4 import BeautifulSoup
import app.models as models
def probar_otro_sitio(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'lxml')
            
            contenedor_foto = soup.select_one('div.imagen img')
            titulo = soup.select('.post-categoria-link')[0].text.strip()
            print(f"✅ ¡FUNCIONÓ!: {titulo}")
            url_img = None
            if contenedor_foto:
                # Probamos 'src', y si no está, 'data-src' (común en sitios con carga lenta)
                url_img = contenedor_foto.get('src') or contenedor_foto.get('data-src')
                
                # Limpieza básica
                url_img = url_img.strip()
                print(f"URL de la imagen encontrada: {url_img}")
                url_img = descargar_imagen(url_img, titulo)
            else:
                print("EEEE")
            
            duracion = soup.select(".duracion")[0].text.strip()[:-1]
            # Extraemos el texto de cada uno
            print(duracion)
            ingredientes = extraer_ingredientes(soup)
            print(ingredientes)
            pasos_tags = soup.select('.orden')

            instrucciones = []

            for tag in pasos_tags:
                # find_next busca el siguiente elemento 'p' en el árbol, sin importar si es hijo o hermano
                parrafo_instruccion = tag.find_next('p')
                
                if parrafo_instruccion:
                    texto_paso = parrafo_instruccion.get_text(strip=True)
                    instrucciones.append(texto_paso)

            # Unimos todo en un solo string para tu DB (separado por saltos de línea)
            instrucciones_final = "\n".join(instrucciones)
            print(instrucciones_final)
            
            return {
                "nombre": titulo,
                "tiempo": int(duracion),
                "tipo": 'C',
                "comida": "cena", 
                "instrucciones": instrucciones_final, 
                "id_usuario": 1, 
                "publica": 1,
                "precio_estimado": 2,
                "image_ruta": url_img,
                "ingredientes": ingredientes
            }
        else:
            print(f"Error {response.status_code} en este sitio también.")
    except Exception as e:
        print(f"Error de red: {e}")


def extraer_ingredientes(soup):
    ingredientes = []
    
    # PLAN A: El selector que ya tenías (específico)
    items = soup.select('.ingrediente, .recipe-ingredient, .ingredient-list li')
    if items:
        return [li.get_text(strip=True) for li in items]

    # PLAN B: Buscar por el texto del encabezado (Muy robusto)
    # Buscamos un h2, h3 o div que contenga la palabra "Ingredientes"
    header = soup.find(lambda tag: tag.name in ['h2', 'h3', 'div'] and "Ingredientes" in tag.text)
    
    if header:
        # Buscamos la primera lista (ul o ol) que aparezca DESPUÉS de ese encabezado
        lista = header.find_next(['ul', 'ol'])
        if lista:
            return [li.get_text(strip=True) for li in lista.find_all('li')]

    return ingredientes # Si llega acá vacío, el sitio es realmente raro

def descargar_imagen(url, nombre_receta):
    # Creamos un nombre de archivo limpio (sin espacios)
    nombre_archivo = nombre_receta.lower().replace(" ", "_") + ".jpg"
    ruta_destino = f"app/static/img/recetas/{nombre_archivo}"
    
    try:
        img_data = requests.get(url).content
        with open(ruta_destino, 'wb') as handler:
            handler.write(img_data)
        return nombre_archivo # Esta es la ruta que guardás en la DB
    except Exception as e:
        print(f"Error descargando imagen: {e}")
        return None

# Probá con una tarta de jamón y queso de ahí:
#probar_otro_sitio("https://recetas.elperiodico.com/receta-de-potaje-de-garbanzos-a-la-antigua-asi-se-hacia-antes-y-por-eso-sabe-mejor-78637.html")
# "https://recetas.elperiodico.com/receta-de-rosquillas-de-limon-de-la-abuela-el-truco-para-que-no-se-rompan-al-freirlas-y-queden-esponjosas-78647.html",
URLS = [
    "https://recetas.elperiodico.com/receta-de-banana-bread-saludable-sin-gluten-sin-azucar-y-super-esponjoso-78553.html",
    
]

if __name__ == "__main__":
    for url in URLS:
        datos_receta = probar_otro_sitio(url)
        print(datos_receta)
        print(models.insertar_receta(datos_receta))
