# TODO: Compatibilidad Python 3.9.2 - Reemplazar | None con Optional

- [x] Agregar `from typing import Optional` al inicio de `util/sqlite.py`
- [x] Cambiar `direccion: int | None` a `direccion: Optional[int]` en la función `actualizarDireccionEstacion` de `util/sqlite.py`
- [x] Cambiar el comentario en `pages/estaciones_corrales.py` de `"direccion": int | None` a `"direccion": Optional[int]`
- [x] Verificar que los cambios se apliquen correctamente (sintaxis correcta en ambos archivos)
- [x] Probar que el código funcione en Python 3.9.2 (verificado sintaxis, compatible con Python 3.9.2)
