import folium
from folium import plugins
import matplotlib.pyplot as plt
from matplotlib.colors import to_hex
import numpy as np

class MapGenerator:
    """Gera mapa interativo colorido por setor"""
    
    def __init__(self, gdf, output_path='output/mapa_setores.html'):
        """
        Inicializa o gerador de mapa
        
        Args:
            gdf: GeoDataFrame com dados geocodificados
            output_path: Caminho para salvar o mapa HTML
        """
        self.gdf = gdf
        self.output_path = output_path
        self.map = None
        self.colors = self._generate_colors()
    
    def _generate_colors(self):
        """Gera paleta de cores para os setores"""
        setores = sorted(self.gdf['SETOR'].unique())
        
        # Usa colormap do matplotlib
        cmap = plt.cm.get_cmap('tab20')
        colors = {}
        
        for idx, setor in enumerate(setores):
            color_rgb = cmap(idx / len(setores))
            colors[setor] = to_hex(color_rgb)
        
        return colors
    
    def create_map(self, center=None, zoom=4):
        """
        Cria o mapa base
        
        Args:
            center: Coordenadas [lat, lon] para centrar. Padrão: Brasil
            zoom: Nível de zoom inicial
        """
        print("\nCriando mapa base...")
        
        # Centro padrão: Brasil
        if center is None:
            center = [-14.2350, -51.9253]
        
        self.map = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles='OpenStreetMap',
            prefer_canvas=True
        )
        
        print("✓ Mapa base criado")
        return self.map
    
    def add_markers(self):
        """Adiciona marcadores coloridos para cada brick"""
        print("\nAdicionando marcadores...")
        
        for idx, row in self.gdf.iterrows():
            setor = row['SETOR']
            brick = row['BRICK']
            lat = row['latitude']
            lon = row['longitude']
            qtd_ceps = row['QTD_CEPS']
            
            # Cor baseada no setor
            color = self.colors.get(setor, '#808080')
            
            # Popup com informações
            popup_text = f"""
            <b>{brick}</b><br>
            Setor: {setor}<br>
            CEPs: {qtd_ceps}<br>
            Lat: {lat:.4f}, Lon: {lon:.4f}
            """
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                popup=folium.Popup(popup_text, max_width=300),
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2,
                opacity=0.9
            ).add_to(self.map)
        
        print(f"✓ {len(self.gdf)} marcadores adicionados")
        return self.map
    
    def add_legend(self):
        """Adiciona legenda de setores"""
        print("\nAdicionando legenda...")
        
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 280px; 
                    background-color: white; border:2px solid grey; 
                    z-index:9999; font-size:14px; padding: 10px;
                    border-radius: 5px; box-shadow: 2px 2px 6px rgba(0,0,0,0.3)">
            <h4 style="margin-top: 0;">Setores</h4>
            <div style="max-height: 300px; overflow-y: auto;">
        '''
        
        for setor in sorted(self.colors.keys()):
            color = self.colors[setor]
            count = len(self.gdf[self.gdf['SETOR'] == setor])
            legend_html += f'''
                <p style="margin: 5px 0;">
                    <span style="display: inline-block; 
                                 width: 12px; height: 12px; 
                                 background-color: {color}; 
                                 border-radius: 50%;"></span>
                    Setor {setor} ({count} bricks)
                </p>
            '''
        
        legend_html += '''
            </div>
        </div>
        '''
        
        self.map.get_root().html.add_child(folium.Element(legend_html))
        print("✓ Legenda adicionada")
        return self.map
    
    def add_layer_control(self):
        """Adiciona controle de camadas"""
        print("\nAdicionando controle de camadas...")
        
        # Cria um FeatureGroup para cada setor
        for setor in sorted(self.gdf['SETOR'].unique()):
            fg = folium.FeatureGroup(name=f'Setor {setor}')
            
            setor_data = self.gdf[self.gdf['SETOR'] == setor]
            color = self.colors.get(setor, '#808080')
            
            for idx, row in setor_data.iterrows():
                popup_text = f"<b>{row['BRICK']}</b><br>Setor: {setor}<br>CEPs: {row['QTD_CEPS']}"
                
                folium.CircleMarker(
                    location=[row['latitude'], row['longitude']],
                    radius=8,
                    popup=popup_text,
                    color=color,
                    fill=True,
                    fillColor=color,
                    fillOpacity=0.7,
                    weight=2
                ).add_to(fg)
            
            fg.add_to(self.map)
        
        folium.LayerControl().add_to(self.map)
        print("✓ Controle de camadas adicionado")
        return self.map
    
    def save(self):
        """Salva o mapa em arquivo HTML"""
        print(f"\nSalvando mapa em: {self.output_path}")
        self.map.save(self.output_path)
        print(f"✓ Mapa salvo com sucesso!")
        return self.output_path
    
    def generate(self, use_layer_control=True):
        """
        Gera o mapa completo
        
        Args:
            use_layer_control: Se True, adiciona controle de camadas ao invés de legenda
        """
        self.create_map()
        self.add_markers()
        
        if use_layer_control:
            self.add_layer_control()
        else:
            self.add_legend()
        
        self.save()
        
        return self.map
