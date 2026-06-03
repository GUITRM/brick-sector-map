import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim
import time

class DataProcessor:
    """Processa dados de CEP e bricks do arquivo Excel"""
    
    def __init__(self, excel_path):
        """
        Inicializa o processador
        
        Args:
            excel_path: Caminho do arquivo CEPBRICK.xlsx
        """
        self.excel_path = excel_path
        self.df = None
        self.gdf = None
        
    def load_excel(self):
        """Carrega dados do arquivo Excel"""
        print(f"Carregando arquivo: {self.excel_path}")
        self.df = pd.read_excel(self.excel_path)
        print(f"✓ Arquivo carregado: {len(self.df)} registros")
        print(f"Colunas: {list(self.df.columns)}")
        return self.df
    
    def validate_data(self):
        """Valida a estrutura dos dados"""
        required_columns = ['CEP', 'BRICK', 'SETOR']
        missing = [col for col in required_columns if col not in self.df.columns]
        
        if missing:
            raise ValueError(f"Colunas obrigatórias faltando: {missing}")
        
        print("✓ Estrutura de dados validada")
        return True
    
    def aggregate_by_brick(self):
        """Agrupa dados por brick para evitar duplicatas"""
        print("\nAgrupando por brick...")
        self.df['CEP'] = self.df['CEP'].astype(str).str.zfill(8)
        
        # Agrupa e conta registros por brick
        self.df_agg = self.df.groupby(['BRICK', 'SETOR']).agg({
            'CEP': ['count', lambda x: ','.join(x)]
        }).reset_index()
        
        self.df_agg.columns = ['BRICK', 'SETOR', 'QTD_CEPS', 'CEPS']
        print(f"✓ {len(self.df_agg)} bricks únicos encontrados")
        return self.df_agg
    
    def geocode_bricks(self):
        """
        Geocodifica os bricks para obter latitude/longitude
        Usa Nominatim para buscar as coordenadas
        """
        print("\nGeocodificando bricks...")
        geolocator = Nominatim(user_agent="brick_sector_map")
        
        latitudes = []
        longitudes = []
        
        for idx, brick in enumerate(self.df_agg['BRICK'], 1):
            try:
                # Busca coordenadas para o brick + Brasil
                location = geolocator.geocode(f"{brick}, Brasil", timeout=10)
                
                if location:
                    latitudes.append(location.latitude)
                    longitudes.append(location.longitude)
                    print(f"  [{idx}/{len(self.df_agg)}] {brick}: ({location.latitude:.4f}, {location.longitude:.4f})")
                else:
                    latitudes.append(None)
                    longitudes.append(None)
                    print(f"  [{idx}/{len(self.df_agg)}] {brick}: Não encontrado")
                
                # Rate limit: 1 segundo entre requisições
                time.sleep(1)
                
            except Exception as e:
                latitudes.append(None)
                longitudes.append(None)
                print(f"  [{idx}/{len(self.df_agg)}] {brick}: Erro - {str(e)}")
        
        self.df_agg['latitude'] = latitudes
        self.df_agg['longitude'] = longitudes
        
        # Remove registros sem coordenadas
        self.df_agg = self.df_agg.dropna(subset=['latitude', 'longitude'])
        print(f"✓ {len(self.df_agg)} bricks geocodificados com sucesso")
        
        return self.df_agg
    
    def create_geodataframe(self):
        """Converte para GeoDataFrame"""
        from shapely.geometry import Point
        
        print("\nCriando GeoDataFrame...")
        geometry = [Point(xy) for xy in zip(self.df_agg['longitude'], self.df_agg['latitude'])]
        self.gdf = gpd.GeoDataFrame(self.df_agg, geometry=geometry, crs='EPSG:4326')
        print("✓ GeoDataFrame criado")
        
        return self.gdf
    
    def get_summary(self):
        """Retorna resumo dos dados processados"""
        summary = {
            'total_bricks': len(self.df_agg),
            'total_ceps': self.df_agg['QTD_CEPS'].sum(),
            'setores_unicos': self.df_agg['SETOR'].nunique(),
            'setores': sorted(self.df_agg['SETOR'].unique().tolist())
        }
        return summary
