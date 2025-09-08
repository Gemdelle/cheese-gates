# 🔧 Guía de Solución de Problemas - Build Script

## ❗ Problema Común: Error de Sintaxis en PowerShell

### **Síntomas:**
```
The string is missing the terminator: ".
Missing closing '}' in statement block or type definition.
```

### **Causas Posibles:**
1. **Encoding del archivo** corrupto (UTF-8 vs Windows-1252)
2. **Caracteres especiales** invisibles en el archivo
3. **Finales de línea** inconsistentes (CRLF vs LF)
4. **Versión de PowerShell** muy antigua

## ✅ **Soluciones**

### **Solución 1: Usar el Script Limpio**
```powershell
# Usa el archivo de respaldo limpio
.\build_exe_clean.ps1

# O copia el limpio sobre el original
Copy-Item .\build_exe_clean.ps1 .\build_exe.ps1 -Force
```

### **Solución 2: Recrear el Archivo**
Si sigues teniendo problemas, borra y recrea:
```powershell
# Borrar archivo problemático
Remove-Item .\build_exe.ps1 -Force

# Copiar desde el backup limpio
Copy-Item .\build_exe_clean.ps1 .\build_exe.ps1
```

### **Solución 3: Verificar PowerShell**
```powershell
# Verificar versión (necesitas 5.1 o superior)
$PSVersionTable.PSVersion

# Si es muy antigua, actualiza PowerShell desde:
# https://github.com/PowerShell/PowerShell/releases
```

### **Solución 4: Encoding Manual**
Si nada funciona, guarda manualmente con encoding correcto:
```powershell
# Leer contenido y guardar con UTF-8
$content = Get-Content .\build_exe_clean.ps1 -Raw
$content | Out-File .\build_exe.ps1 -Encoding utf8 -NoNewline
```

## 🎯 **Comandos de Test**

### **Verificar Sintaxis:**
```powershell
# Este comando debe pasar sin errores
Get-Command .\build_exe.ps1
```

### **Test Rápido:**
```powershell
# Build de prueba rápido
.\build_exe.ps1 -Mode fast -SkipDeps
```

## 📋 **Compatibilidad Garantizada**

### **Sistemas Probados:**
- ✅ Windows 10 (PowerShell 5.1+)
- ✅ Windows 11 (PowerShell 5.1+)
- ✅ PowerShell Core 7.x
- ✅ Diferentes encodings de archivo
- ✅ Diferentes rutas de usuario

### **Requisitos Mínimos:**
- **PowerShell**: 5.1 o superior
- **Python**: 3.7 o superior
- **Permisos**: Lectura/escritura en el directorio

### **Archivos de Respaldo:**
- `build_exe.ps1` → Script principal
- `build_exe_clean.ps1` → Versión limpia de respaldo

## 🚀 **Si Todo Falla**

### **Método Manual:**
1. Abre PowerShell como Administrador
2. Navega al directorio del proyecto
3. Ejecuta comandos uno por uno:

```powershell
# Instalar dependencias
.\venv\Scripts\python.exe -m pip install -r requirements.txt

# Build manual
.\venv\Scripts\python.exe -m PyInstaller --onefile --windowed --name CheeseGates main.py
```

### **Contacto:**
Si ninguna solución funciona, proporciona:
- Versión de Windows
- Versión de PowerShell (`$PSVersionTable`)
- Error completo (captura de pantalla)
- Ruta del proyecto (¿tiene caracteres especiales?)
