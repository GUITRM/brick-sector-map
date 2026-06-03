# Brick Sector Map 🗺️

Visualizador interativo de bairros (bricks) do Brasil com alocação de setores em mapa colorido.

## Descrição

Este projeto permite visualizar bairros brasileiros em um mapa interativo, coloridos por setor. Utiliza dados de CEP, nome do brick (bairro) e setor para gerar uma visualização geoespacial.

## Estrutura do Projeto

```
brick-sector-map/
├── data/
│   └── CEPBRICK.xlsx          # Base de dados com CEP, BRICK e SETOR
├── src/
│   ├── main.py                # Script principal
│   ├── data_processor.py       # Processamento de dados
│   └── map_generator.py        # Geração do mapa
├── output/
│   └── mapa_setores.html       # Mapa interativo gerado
├── requirements.txt             # Dependências Python
└── README.md                    # Este arquivo
```

## Requisitos

- Python 3.8+
- Pandas
- Geopandas
- Folium
- Openpyxl

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

```bash
python src/main.py
```

O script irá:
1. Ler o arquivo `CEPBRICK.xlsx`
2. Processar os dados de CEP e bricks
3. Geocodificar os CEPs para obter coordenadas
4. Gerar um mapa interativo colorido por setor
5. Salvar em `output/mapa_setores.html`

## Estrutura do Excel

O arquivo `CEPBRICK.xlsx` deve ter as seguintes colunas:

| CEP | BRICK | SETOR |
|-----|-------|-------|
| 01310100 | Centro | 01 |
| 01310200 | Centro | 01 |
| 02000000 | Bom Retiro | 02 |

## Saída

Um arquivo HTML interativo (`mapa_setores.html`) será gerado com:
- Mapa colorido por setor
- Informações ao clicar no marcador
- Filtros por setor
- Legenda de cores

## Próximas Etapas

- [x] Criar estrutura do projeto
- [x] Implementar data processor
- [x] Implementar map generator
- [x] Criar script principal
- [ ] Testar com dados reais
- [ ] Otimizar performance

## Licença

MIT
