# ADR 008 — Confiança TLS nativa para consulta de atualização

- Estado: Aceita
- Data: 2026-11-08 (registro retrospectivo)
- Responsável: mantenedor do projeto
- Substitui: nenhuma
- Substituída por: nenhuma

## Contexto

Alguns ambientes corporativos instalam autoridades certificadoras próprias no
Windows. O executável empacotado precisa respeitar o armazenamento confiável do
sistema sem enfraquecer HTTPS.

## Decisão

Usar `truststore` para validar HTTPS pelo armazenamento nativo do sistema; no
Windows, isso utiliza CryptoAPI e respeita raízes públicas e corporativas
instaladas pelo administrador. Manter verificação do certificado e hostname.

É proibido usar `CERT_NONE`, desabilitar hostname ou embutir certificado
específico de cliente para contornar uma falha. Erros de rede permanecem
silenciosos para não bloquear o fluxo de backup.

## Consequências

- o comportamento segue a política de confiança do Windows;
- inspeção HTTPS corporativa funciona quando a raiz foi instalada pela TI;
- falhas não podem ser “corrigidas” reduzindo segurança;
- atualização continua passiva, sem substituição automática do executável.

## Evidências

- `src/core/update_checker.py`;
- `requirements.txt`;
- `docs/HELP.md`;
- testes de update checker.
