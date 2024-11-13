# Environmental Temperature Monitoring System (ETMS)

El **Environmental Temperature Monitoring System (ETMS)** es un sistema diseñado para monitorear, analizar y visualizar datos de temperatura obtenidos de sensores. Incluye funcionalidades avanzadas como gráficos interactivos, alertas configurables, generación de reportes en PDF y administración de usuarios.

**Nota importante:** Para la recepción de datos en tiempo real, es esencial que todo el subsistema **ADMON (Acquisition and Monitoring system)** esté funcionando correctamente. ADMON gestiona la adquisición y monitoreo de datos de temperatura, sirviendo como la base para la visualización y análisis en ETMS.

---

## Características

- **Autenticación y administración de usuarios**:
  - Registro de nuevos usuarios con aprobación por un administrador.
  - Inicio de sesión seguro y cierre de sesión.

- **Gestión y visualización de datos**:
  - Consulta de datos en tiempo real y datos históricos.
  - Gráficos interactivos para análisis de tendencias, rendimiento y distribución de temperatura.
  - Alertas configurables basadas en umbrales máximos y mínimos.

- **Reportes automatizados**:
  - Generación de reportes en PDF con estadísticas detalladas de los sensores.

- **Configuración avanzada**:
  - Filtrado de sensores por grupos ("Pixels", "Strips" o "All").
  - Configuración de rangos de tiempo y valores de umbral para alertas.

---

## Instalación

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/Grupo-de-Investigacion-ATLAS-PUJ/EnvironmentalTemperatureMonitoringSystem.git
   cd EnvironmentalTemperatureMonitoringSystem

2. **Verificar Conectividad ADMON**:

Para comprobar y poder correr el subsistema ETMS, se busca que el substistema ADMON este funcionando correctamente y mandando datos a InfluxDB

3. **Correr el programa**:

Una vez ya se tenga el programa y el subsistema ADMON se ejecuta python utilizando el comando Python .\main.py

## Requisitos

- **Python 3.8 o superior**.
- **InfluxDB configurado correctamente**.
- **Subsistema ADMON**:
  - Debe estar operativo para garantizar la recepción de datos de sensores.

---

## Tecnologías Utilizadas

- **Flask** - Framework para el backend.
- **Plotly** - Visualización interactiva de datos.
- **FPDF** - Generación de reportes en PDF.
- **Pandas** - Manipulación y análisis de datos.
- **InfluxDB** - Base de datos para series temporales.

