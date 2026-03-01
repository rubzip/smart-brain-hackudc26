# Migraciones de Base de Datos

Esta carpeta contiene las migraciones de la base de datos en orden cronológico.

## Convención de nombres

`YYYYMMDD_HHMMSS_descripcion.sql`

Ejemplo: `20260228_153000_add_priority_to_tasks.sql`

## Aplicar migraciones

```bash
psql -U user -d smartbrain -f schemas/init.sql
psql -U user -d smartbrain -f schemas/migrations/20260228_153000_example.sql
```

## Crear nueva migración

1. Crear archivo con timestamp actual
2. Escribir SQL de migración (con rollback si es posible)
3. Aplicar con psql o herramienta de migración

## Herramientas recomendadas

- **Alembic**: Para migraciones con Python/SQLAlchemy
- **Flyway**: Para migraciones versionadas
- **psql**: Para aplicación manual
