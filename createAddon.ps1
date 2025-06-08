# Remove o arquivo zip antigo, se existir
Remove-Item -Path "puppenspieler.zip" -Force -ErrorAction SilentlyContinue

# Cria o diretório
New-Item -Path "puppenspieler" -ItemType Directory -Force

# Copia os arquivos da pasta src para puppenspieler
Copy-Item -Path ".\src\*" -Destination ".\puppenspieler\" -Recurse -Force

# Cria um novo arquivo zip
Compress-Archive -Path ".\puppenspieler\*" -DestinationPath "puppenspieler.zip" -Force

# Remove os arquivos temporários da pasta puppenspieler
Remove-Item -Path ".\puppenspieler\*" -Recurse -Force

# Remove o diretório vazio
Remove-Item -Path "puppenspieler" -Force
