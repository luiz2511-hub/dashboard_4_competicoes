# Football Analytics — 3 competições

Nova versão baseada no dashboard original `dashboard_pronto`, mantendo a proposta visual e a tabela com estatísticas.

Competições incluídas:
- FIFA World Cup (`WC`)
- UEFA Champions League (`CL`)
- Campeonato Brasileiro Série A (`BSA`)

Inclui barra lateral, seletor de temporada, cards, tabela e quatro gráficos. Não inclui mapas, Série B ou Copa do Brasil.

## Rodar no Windows
1. Instale Python 3.10+.
2. No terminal desta pasta:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Copie `.env.example` para `.env` e informe sua chave da football-data.org em `FOOTBALL_DATA_TOKEN`.
4. Execute `python app.py`.
5. Abra http://127.0.0.1:8000

## Deploy no Render
Build command: `pip install -r requirements.txt`
Start command: `gunicorn app:app`
Configure `FOOTBALL_DATA_TOKEN` nas variáveis de ambiente. Não publique o `.env`.

## API e cache
O backend consulta football-data.org usando `WC`, `CL` e `BSA`. O cache é mantido por até 24 horas por competição e temporada; o botão de atualização força uma nova consulta. A disponibilidade de competições e temporadas depende do plano e da chave. Se a API não liberar uma competição/temporada, o dashboard informa o erro e não inventa dados.

Os gráficos são calculados com os dados retornados pela tabela. Para torneios/temporadas sem classificação disponível nessa API, será necessária outra fonte de dados.

Esta é uma cópia independente. Nenhum arquivo do repositório original foi modificado.
