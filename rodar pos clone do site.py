import os
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse

def sincronizar_assets_canva():
    # 1. Garante a criação do .nojekyll
    Path('.nojekyll').touch(exist_ok=True)
    print("✔ Arquivo .nojekyll verificado/criado.")

    # 2. Carrega o manifest.json
    manifest_path = Path('manifest.json')
    if not manifest_path.exists():
        print("❌ Erro: manifest.json não foi encontrado na raiz.")
        return

    with open(manifest_path, 'r', encoding='utf-8') as f:
        try:
            manifest = json.load(f)
        except json.JSONDecodeError:
            print("❌ Erro: O arquivo manifest.json possui sintaxe inválida.")
            return

    sucessos = 0
    faltantes = 0

    print("\n--- Processando de-para do Manifest ---")

    for chave_origem, url_destino in manifest.items():
        # Extrai o caminho relativo dentro de _assets/
        # Ex: ".../_assets/images/hash.woff2" -> "_assets/images/hash.woff2"
        # Ex: ".../_assets/f006f4aff9718490.ltr.css" -> "_assets/f006f4aff9718490.ltr.css"
        
        caminho_relativo_destino = None
        if '_assets/' in url_destino:
            caminho_relativo_destino = '_assets/' + url_destino.split('_assets/')[-1]
        elif 'blob:' in url_destino:
            # Para URLs blob, enviamos por padrão as imagens para _assets/media/
            nome_hash = os.path.basename(chave_origem)
            caminho_relativo_destino = f"_assets/media/{nome_hash}"

        if not caminho_relativo_destino:
            continue

        destino_final = Path(caminho_relativo_destino)
        destino_final.parent.mkdir(parents=True, exist_ok=True)

        # Determina o arquivo de origem local
        # Tenta primeiro pela rota do manifesto (ex: 'fonts/0.woff2', 'images/94.png')
        arquivo_origem = Path(chave_origem)
        
        # Caso o arquivo não esteja na subpasta descrita na chave, tenta buscar pelo nome do arquivo na raiz
        if not arquivo_origem.exists():
            arquivo_origem = Path(os.path.basename(chave_origem))

        # Executa a cópia se o arquivo de origem existir
        if arquivo_origem.exists():
            shutil.copy2(arquivo_origem, destino_final)
            print(f"✔ Copiado: {arquivo_origem} ➔ {destino_final}")
            sucessos += 1
        else:
            print(f"⚠️ Não encontrado localmente: {chave_origem} (Requerido para: {destino_final})")
            faltantes += 1

    print(f"\n==========================================")
    print(f"Concluído: {sucessos} arquivos estruturados em _assets/")
    if faltantes > 0:
        print(f"Atenção: {faltantes} arquivos do manifesto não foram encontrados localmente.")
    print(f"==========================================\n")

if __name__ == '__main__':
    sincronizar_assets_canva()