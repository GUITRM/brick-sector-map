"""
Script principal para processar dados e gerar mapa de setores
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório src ao path
sys.path.insert(0, os.path.dirname(__file__))

from data_processor import DataProcessor
from map_generator import MapGenerator

def main():
    """Função principal"""
    
    print("=" * 60)
    print("BRICK SECTOR MAP - Visualizador de Setores")
    print("=" * 60)
    
    # Caminhos
    excel_path = 'data/CEPBRICK.xlsx'
    output_dir = 'output'
    
    # Cria diretório de output se não existir
    Path(output_dir).mkdir(exist_ok=True)
    
    # Verifica se arquivo existe
    if not os.path.exists(excel_path):
        print(f"\n❌ Erro: Arquivo '{excel_path}' não encontrado!")
        print("   Coloque seu arquivo CEPBRICK.xlsx na pasta 'data/'")
        return
    
    try:
        # 1. Processar dados
        print("\n[1/5] Processando dados...")
        processor = DataProcessor(excel_path)
        processor.load_excel()
        processor.validate_data()
        processor.aggregate_by_brick()
        processor.geocode_bricks()
        processor.create_geodataframe()
        
        # Exibe resumo
        summary = processor.get_summary()
        print("\n" + "=" * 60)
        print("RESUMO DOS DADOS")
        print("=" * 60)
        print(f"Total de Bricks: {summary['total_bricks']}")
        print(f"Total de CEPs: {summary['total_ceps']}")
        print(f"Setores únicos: {summary['setores_unicos']}")
        print(f"Setores: {', '.join(map(str, summary['setores']))}")
        print("=" * 60)
        
        # 2. Gerar mapa
        print("\n[2/5] Gerando mapa...")
        map_gen = MapGenerator(processor.gdf, output_path=f'{output_dir}/mapa_setores.html')
        map_gen.generate(use_layer_control=True)
        
        # 3. Salvar dados processados
        print("\n[3/5] Salvando dados processados...")
        processor.df_agg.to_csv(f'{output_dir}/bricks_processados.csv', index=False)
        processor.gdf.to_file(f'{output_dir}/bricks_geojson.geojson', driver='GeoJSON')
        print(f"✓ Dados salvos em {output_dir}/")
        
        # 4. Relatório
        print("\n[4/5] Gerando relatório...")
        generate_report(processor.df_agg, output_dir)
        
        print("\n[5/5] Concluído!")
        print("\n" + "=" * 60)
        print("✓ SUCESSO!")
        print("=" * 60)
        print(f"\nArquivos gerados:")
        print(f"  • Mapa interativo: {output_dir}/mapa_setores.html")
        print(f"  • Dados (CSV): {output_dir}/bricks_processados.csv")
        print(f"  • Dados (GeoJSON): {output_dir}/bricks_geojson.geojson")
        print(f"  • Relatório: {output_dir}/relatorio_setores.txt")
        print(f"\nAbra o arquivo HTML no navegador para visualizar o mapa!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

def generate_report(df, output_dir):
    """Gera relatório em texto"""
    report_path = f'{output_dir}/relatorio_setores.txt'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("RELATÓRIO DE SETORES\n")
        f.write("=" * 80 + "\n\n")
        
        # Resumo geral
        f.write("RESUMO GERAL\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total de Bricks: {len(df)}\n")
        f.write(f"Total de CEPs: {df['QTD_CEPS'].sum()}\n")
        f.write(f"Setores únicos: {df['SETOR'].nunique()}\n\n")
        
        # Detalhes por setor
        f.write("DETALHES POR SETOR\n")
        f.write("-" * 80 + "\n")
        
        for setor in sorted(df['SETOR'].unique()):
            setor_data = df[df['SETOR'] == setor]
            f.write(f"\nSetor {setor}:\n")
            f.write(f"  Bricks: {len(setor_data)}\n")
            f.write(f"  CEPs: {setor_data['QTD_CEPS'].sum()}\n")
            f.write(f"  Bricks: {', '.join(setor_data['BRICK'].tolist())}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("Relatório gerado automaticamente\n")
    
    print(f"✓ Relatório salvo em {report_path}")

if __name__ == '__main__':
    exit(main())
