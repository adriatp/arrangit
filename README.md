# Arrangit - Gestor de Tareas del Proyecto

Un gestor de tareas simple para proyectos, que guarda toda la información en `.arrangit.json`.

## Instalación

1. Clona o copia el proyecto
2. Asegúrate de que el script `arrangit` sea ejecutable:
   ```bash
   chmod +x arrangit
   ```

## Configuración de Autocompletado

Para habilitar el autocompletado con TAB, añade esto a tu `.bashrc` o `.zshrc`:

```bash
source /ruta/completa/a/arrangit/completions.sh
```

## Uso

### Comandos Disponibles

- `./arrangit list` - Listar todas las tareas
- `./arrangit task "nombre"` - Crear o seleccionar tarea
- `./arrangit subtask "nombre"` - Crear o seleccionar subtarea
- `./arrangit active` - Mostrar tarea activa
- `./arrangit done "nombre"` - Marcar tarea como completada
- `./arrangit delete "nombre"` - Eliminar tarea

### Ejemplos

```bash
# Crear una nueva tarea
./arrangit task "Desarrollar API" -d "Crear endpoints para usuarios"

# Crear una subtarea (seleccionarás la tarea padre)
./arrangit subtask "Autenticación"

# Marcar tarea como completada
./arrangit done "Desarrollar API"

# Eliminar tarea
./arrangit delete "Tarea antigua"

# Ver tarea activa
./arrangit active

# Listar todas las tareas
./arrangit list
```

## Características

- **Búsqueda por nombre**: No necesitas recordar IDs
- **Autocompletado**: Usa TAB para completar nombres de tareas
- **Subtareas**: Crea jerarquías de tareas
- **Tarea activa**: Siempre hay una tarea activa para trabajar
- **Persistencia**: Todo se guarda automáticamente en `.arrangit.json`

## Estructura de Archivos

- `src/` - Código fuente del programa
- `.arrangit.json` - Base de datos de tareas
- `arrangit` - Script principal
- `completions.sh` - Script de autocompletado

