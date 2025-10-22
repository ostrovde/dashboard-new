# RayAgro Ops (локально)

## Билд UI
```bash
npm run build
```

## Ручной запуск диагностики
```bash
python3 diagnostics.py --json
```

## Отчёт диагностики (с логом)
```bash
python3 scripts/diag_report.py
ls -lt logs | head -n 2
```

## Авто-диагностика после билда
- Включена через `systemd.path`: следит за `dist/index.html`.
- Юниты: `/etc/systemd/system/diag-report.path`, `diag-report.service`.

## Микро-оркестратор (локально)
- Health: `GET  http://127.0.0.1:8078/health`
- Диагностика: `POST http://127.0.0.1:8078/diagnostics`
- Патч: `POST http://127.0.0.1:8078/patch` (body = unified diff)
- PR: `POST http://127.0.0.1:8078/pr` (body = текст в PR)
- Build/Test: `POST http://127.0.0.1:8078/run?task=build|test|diag`
- DoD в PR: `POST http://127.0.0.1:8078/donesheet`

## Откат (локально)
```bash
git revert <commit_sha>
```
