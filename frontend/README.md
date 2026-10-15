# Frontend — Sistema de Cátedras Abiertas USB Medellín

Frontend React + Vite construido sobre la API y estructura existentes del proyecto Cátedras.

## Incluye

- Landing/catalogo institucional de cátedras.
- Búsqueda por nombre, tema o sede.
- Filtro por categoría.
- Modal de detalle de cátedra.
- Flujo de registro de estudiante en 3 pasos: identificación → OTP → confirmación.
- Vista de “Mis inscripciones”.
- Panel de administración de sedes.
- CRUD de sedes conectado a `GET/POST/PUT/DELETE /api/sede`.
- Fallback local para visualizar el catálogo y sedes cuando la API todavía no está levantada.
- Diseño responsive.
- Paleta institucional del manual: naranja `#EF7D00` y negro `#1D1D1B`.
- Uso de tipografías complementarias Montserrat/Raleway.

## Ejecutar

```powershell
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`
API: `http://localhost:8042`

Si la API está en otra dirección, copia `.env.example` a `.env` y cambia `VITE_API_URL`.

## Nota sobre la API

Se agregó CORS para permitir que el frontend Vite consuma la API desde `localhost:5173` durante desarrollo. El backend mantiene sus endpoints originales y su contrato de v1.
