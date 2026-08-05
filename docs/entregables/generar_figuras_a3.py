import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist

# Configuración de colores institucionales
COLOR_NAVY = '#1F4D78'
COLOR_BLUE = '#2563EB'
COLOR_SKY = '#3B82F6'
COLOR_AMBER = '#F97316'
COLOR_MUTED = '#64748B'

def generar_matriz_competitiva():
    """Genera un gráfico de gradiente de características vs costo/esfuerzo"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Datos simulados de competidores
    competidores = ['Karisma Data', 'Bloomberg Terminal', 'Herramientas BI (Power BI, Pyramid)', 'Bases Aisladas / Excel', 'Silos Departamentales']
    x_cost = [4, 9, 5, 2, 3]  # Costo/Esfuerzo
    y_feat = [9, 10, 7, 3, 4] # Características para la Institución
    sizes = [800, 500, 500, 400, 400]
    colors = [COLOR_AMBER, COLOR_NAVY, COLOR_SKY, COLOR_MUTED, COLOR_MUTED]
    
    scatter = ax.scatter(x_cost, y_feat, s=sizes, c=colors, alpha=0.8, edgecolors='w', linewidth=2)
    
    # Etiquetas
    for i, txt in enumerate(competidores):
        ax.annotate(txt, (x_cost[i], y_feat[i]), xytext=(0, -15), 
                    textcoords='offset points', ha='center', va='top', 
                    fontweight='bold' if txt == 'Karisma Data' else 'normal',
                    color=COLOR_NAVY)
    
    ax.set_title('Gradiente de Postura Competitiva (Institucional)', fontsize=16, fontweight='bold', color=COLOR_NAVY, pad=20)
    ax.set_xlabel('Costo y Esfuerzo de Implementación', fontsize=12, color=COLOR_NAVY)
    ax.set_ylabel('Funcionalidad Específica (Datos Macroeconómicos/Silos)', fontsize=12, color=COLOR_NAVY)
    
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11)
    
    ax.grid(True, linestyle='--', alpha=0.5, color=COLOR_MUTED)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLOR_NAVY)
    ax.spines['bottom'].set_color(COLOR_NAVY)
    
    plt.tight_layout()
    plt.savefig('figuras/a3_matriz_competitiva.png', dpi=300, bbox_inches='tight')
    plt.close()

def generar_dendrograma_card_sorting():
    """Genera un dendrograma simulado del Card Sorting"""
    # Términos en lenguaje de usuario (alineados a escenarios)
    etiquetas = [
        'Cartera de Crédito', 'Posiciones de Liquidez', 'Operaciones de Derivados', 'Exportación en 2do Plano',
        'Tablero Directivo de Riesgos', 'Señales de Riesgo',
        'Catálogo de Metadatos', 'Flujos de Aprobación', 'Bitácora de Accesos',
        'Consumo por API', 'Mi Perfil', 'Solicitar Permiso'
    ]
    
    # Matriz de distancia simulada (los elementos cercanos están correlacionados)
    X = np.array([
        [1, 9], [1, 8.5], [1, 9.2], [1.5, 8.8],  # Fuentes y Extracción (4 tarjetas)
        [8, 2], [8.5, 2],                        # Supervisión (2 tarjetas)
        [5, 5], [5.2, 4.8], [4.8, 5.2],          # Gobierno (3 tarjetas)
        [9, 9], [9.2, 8.8], [8.8, 9]             # Integración y Perfiles (3 tarjetas)
    ])
    
    etiquetas_ordenadas = etiquetas
    
    dist_matrix = pdist(X)
    Z = linkage(dist_matrix, 'ward')
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    import sys
    sys.setrecursionlimit(10000)
    
    dendro = dendrogram(
        Z, labels=etiquetas_ordenadas, orientation='right', 
        leaf_font_size=10, 
        color_threshold=3.5, 
        above_threshold_color=COLOR_MUTED
    )
    
    ax.set_title('Análisis de Agrupamiento (Card Sorting) - Similitud', fontsize=16, fontweight='bold', color=COLOR_NAVY, pad=20)
    ax.set_xlabel('Distancia (Disimilitud)', fontsize=12, color=COLOR_NAVY)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color(COLOR_NAVY)
    
    plt.tight_layout()
    plt.savefig('figuras/a3_dendrograma.png', dpi=300, bbox_inches='tight')
    plt.close()

def generar_mapa_navegacion():
    """Genera un mapa de sitio (jerárquico) visual"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Coordenadas y cajas (X, Y, texto, ancho, alto)
    boxes = {
        'Home': (5, 9, 'Karisma Data\n(Inicio / Buscador)'),
        'Catalogo': (2, 6, 'Exploración y Extracción\n(Laura / Diego)'),
        'Gobierno': (5, 6, 'Gobierno y Supervisión\n(Arturo / Roberto)'),
        'Admin': (8, 6, 'Administración\n(Mariana / Ximena)'),
        # Hijos Catalogo
        'C_Cred': (1, 3, 'Catálogo\nTemático'),
        'C_Liq': (2.3, 3, 'Buscador\nFacetado'),
        'C_Exp': (3.6, 3, 'Motor de\nExportación'),
        # Hijos Gobierno
        'G_Meta': (5, 3, 'Catálogo de\nMetadatos'),
        'G_Dash': (6.3, 3, 'Tableros\nDirectivos'),
        # Hijos Admin
        'A_Acc': (7.6, 3, 'Gestión de\nAccesos'),
        'A_API': (8.9, 3, 'Credenciales\nAPI')
    }
    
    # Líneas de jerarquía (padre, hijo)
    edges = [
        ('Home', 'Catalogo'), ('Home', 'Gobierno'), ('Home', 'Admin'),
        ('Catalogo', 'C_Cred'), ('Catalogo', 'C_Liq'), ('Catalogo', 'C_Exp'),
        ('Gobierno', 'G_Meta'), ('Gobierno', 'G_Dash'),
        ('Admin', 'A_Acc'), ('Admin', 'A_API')
    ]
    
    # Dibujar flechas
    for p, c in edges:
        px, py = boxes[p][0], boxes[p][1]
        cx, cy = boxes[c][0], boxes[c][1]
        
        # Líneas ortogonales
        ax.plot([px, px], [py-0.5, py-1.5], color=COLOR_MUTED, lw=2)
        ax.plot([px, cx], [py-1.5, py-1.5], color=COLOR_MUTED, lw=2)
        ax.plot([cx, cx], [py-1.5, cy+0.5], color=COLOR_MUTED, lw=2)
    
    # Dibujar cajas
    for k, (x, y, txt) in boxes.items():
        color = COLOR_NAVY if y == 9 else COLOR_SKY if y == 6 else 'white'
        txt_col = 'white' if y >= 6 else COLOR_NAVY
        ec = COLOR_NAVY
        
        # Ajustar ancho de caja
        width = 1.8 if y == 9 else 1.2 if y == 3 else 2.2
        height = 1.0
        
        box = plt.Rectangle((x - width/2, y - height/2), width, height, 
                           facecolor=color, edgecolor=ec, lw=2, zorder=5)
        ax.add_patch(box)
        
        ax.text(x, y, txt, ha='center', va='center', color=txt_col, 
                fontsize=10 if y == 3 else 11, fontweight='bold', zorder=10)

    ax.set_title('Mapa de Navegación (Arquitectura de Información)', fontsize=16, fontweight='bold', color=COLOR_NAVY, pad=20)
    
    ax.set_xlim(0, 10)
    ax.set_ylim(2, 10)
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig('figuras/a3_mapa_sitio.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == '__main__':
    # Ensure directory exists
    os.makedirs('figuras', exist_ok=True)
    
    generar_matriz_competitiva()
    generar_dendrograma_card_sorting()
    generar_mapa_navegacion()
    print("Figuras A3 generadas con éxito en la carpeta 'figuras/'.")
