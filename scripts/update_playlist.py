name: Update M3U Playlist

on:
  schedule:
    - cron: '0 */6 * * *'  # Cada 6 horas
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ github.workspace }}
        
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Historial completo para Git
          
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install dependencies
        run: pip install requests
          
      - name: Run updater
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
          GITHUB_WORKSPACE: ${{ github.workspace }}
        run: |
          echo "📍 Directorio de trabajo: $GITHUB_WORKSPACE"
          python scripts/update_playlist.py
          
          # Verificación estricta
          if [ ! -f "canales.m3u" ]; then
            echo "❌ Error: Archivo M3U no generado"
            ls -la
            exit 1
          fi
          
          echo "✅ Archivo generado correctamente"
          head -n 5 canales.m3u  # Muestra muestra del contenido
          
      - name: Commit changes
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          git config --global user.name "GitHub Actions"
          git config --global user.email "actions@github.com"
          
          # Solo commit si hay cambios reales
          if git diff --quiet --exit-code; then
            echo "🟢 No hay cambios para commitear"
          else
            git add canales.m3u
            git commit -m "🔄 Actualización M3U [skip ci]"
            git pull --rebase
            git push
            echo "✅ Cambios subidos correctamente"
          fi
