# Automazione Deploy & Rollback Stack AI

## Descrizione
Script per automatizzare il download, la conversione in GGUF e il deployment con rollback di modelli LLM locali su stack AI basato su systemd.

## Architettura
- `scripts/download_model.sh`: scarica un modello da URL e verifica checksum SHA256.
- `scripts/convert_to_gguf.py`: converte un modello Hugging Face in formato GGUF usando llama.cpp.
- Configurazioni systemd (in `configs/`) per il servizio di inferenza con meccanismo di rollback automatico.
- Log di attività in `logs/`.

## Installazione
1. Clonare il repository.
2. Assicurarsi di avere le dipendenze: `bash`, `curl` o `wget`, `python3`, `llama.cpp` (con lo script di conversione).
3. Impostare le variabili d'ambiente necessarie (es. `LLAMA_CPP_PATH`) oppure modificare gli script.
4. Rendere eseguibili gli script: `chmod +x scripts/*.sh scripts/*.py`.

## Uso
- Scaricare e verificare un modello:
  ```bash
  ./scripts/download_model.sh <URL_MODEL> <SHA256_ATTESO>
  ```
- Convertire un modello in GGUF:
  ```bash
  ./scripts/convert_to_gguf.py <directory_modello_hf> [file_output.gguf] [--outtype f16]
  ```
- Deploy del servizio (richiede privilegi di systemd user):
  ```bash
  # Copiare le unit file in ~/.config/systemd/user/
  cp configs/*.service ~/.config/systemd/user/
  systemctl --user daemon-reload
  systemctl --user start <nome_servizio>
  ```
- Rollback automatico gestito dallo script di deploy (vedere configs).

## Esempi
```bash
# Esempio di download
./scripts/download_model.sh https://huggingface.co/TheBloke/Qwen3-35B-A3B-GGUF/resolve/main/qwen3-35b-a3b.gguf e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

# Esempio di conversione (se si ha il modello HF)
./scripts/convert_to_gguf.py ./models/Qwen3-35B-A3B-HF ./gguf/qwen3-35b-a3b.gguf --outtype q4_0
```

## Stato
✅ COMPLETATO — 2026-06-14
Tutte le fasi sono state realizzate: struttura, script di download/checksum, conversione GGUF, deploy systemd con rollback.