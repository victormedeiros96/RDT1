from data_interface import DataSourceInterface
import pandas as pd

# Exemplo de uso com arquivo JSON

interface = DataSourceInterface()


# Exemplo de uso com Excel
titulo = "Levantamento Visual Detalhado - LVD"

print("Excel salvo com título centralizado.")



# Exemplo de leitura e transformação do josiel.json em DataFrame
interface_json = DataSourceInterface(json_path="deteccoes.json")

# Ler o arquivo JSON
data = interface_json.read_json()

# Transformar em DataFrame
import json
import pandas as pd

# Lista para armazenar os dados estruturados
dados_estruturados = []

# Iterar sobre os KMs
for km, km_data in data.items():
    # Iterar sobre os arquivos de imagem de cada KM
    for index,(arquivo_imagem, detecoes) in enumerate(km_data.items()):
        # Iterar sobre cada detecção
      
        for deteccao in detecoes:
            for deteccao_id, deteccao_info in deteccao.items():
                # Extrair informações da detecção
                linha = {
                    'KM': int(km.split("_")[1]),
                    'arquivo_imagem': arquivo_imagem,
                    'deteccao_id': deteccao_id,
                    'classe': deteccao_info.get('class', ''),
                    'area':deteccao_info.get('area',0),
                    'linha': deteccao_id[3],
                    'coluna':deteccao_id[1],
                    'quadrante': index,
                    'direction': deteccao_info.get('direction',""),
                    'thickness':deteccao_info.get('thickness',0),
                    'bbox_x1': deteccao_info.get('global_bbox', [None])[0] if len(deteccao_info.get('global_bbox', [])) > 0 else None,
                    'bbox_y1': deteccao_info.get('global_bbox', [None])[1] if len(deteccao_info.get('global_bbox', [])) > 1 else None,
                    'bbox_x2': deteccao_info.get('global_bbox', [None])[2] if len(deteccao_info.get('global_bbox', [])) > 2 else None,
                    'bbox_y2': deteccao_info.get('global_bbox', [None])[3] if len(deteccao_info.get('global_bbox', [])) > 3 else None,
                    'polygon': str(deteccao_info.get('global_polygon', []))  # Converter para string pois é uma lista
                    
                }
                dados_estruturados.append(linha)

# Criar DataFrame
df = pd.DataFrame(dados_estruturados)

# Mostrar informações do DataFrame
print(f"DataFrame criado com {len(df)} registros")

print("\nClasses encontradas:")
print(df['classe'].value_counts())


# Salvar o DataFrame em Excel se desejar
interface.write_excel_with_title("planilha.xlsx", titulo,0,2,df )#df['KM'].min(),df['KM'].max()
df.to_excel("retigrafico.xlsx", index=False)
